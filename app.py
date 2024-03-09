import os
import random
import logging
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
)

app = Flask(__name__)


line_bot_api = LineBotApi('9vhVHnOG2ySYldADpiacTQjwz4cEAEJW93dg3g/BCUGE8q4+WoEJfADJ1Oij0S/XDS6+PwaxHY4cCbxQcqcnSA1ragmegQJxcNax8qYXo51CiPPhWrvfzYFmIJAY7Ri9d7BO3uQLQdg/hXtYCq+bFgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3a6d6100f0621453f5477776424f4cfe')

users_current_question = {}  # ユーザーIDをキーとした現在の質問番号の記録
users_answers = {}  # ユーザーIDをキーとした回答の記録

# 質問リスト
questions = [
    "患者さんの意見や感情に敏感ですか？",
    "あなたは今転職を考えていますか？",
    "あなたは今の職場に不満を感じていますか？",
]

# 各質問に対する看護師タイプの対応関係と点数
question_nurse_type_mapping = {
    0: {"はい": {"INFJ": 2, "ISFJ": 2, "ENFJ": 2, "ESFJ": 2, "INFP": 2, "ISFP": 2, "ENFP": 1, "ESFP": 1}},  # 感情に敏感（感情）
    1: {"はい": {"ENTP": 20}} , # 組織的（判断）
    2: {"はい": {"ENTP": 20}} , # 組織的（判断）
}



@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")  # ログ出力を追加

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    if text == "診断開始":
        users_current_question[user_id] = 0
        users_answers[user_id] = []
        ask_question(event.reply_token, 0)
    elif text in ["はい", "いいえ"] and user_id in users_current_question:
        process_answer(user_id, text, event.reply_token)

def ask_question(reply_token, question_index):
    question = questions[question_index]
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=question,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(action=MessageAction(label="はい", text="はい")),
                            QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
                        ])))

logging.basicConfig(level=logging.INFO)

def process_answer(user_id, text, reply_token):
    users_answers[user_id].append(text)
    next_question_index = users_current_question[user_id] + 1
    if next_question_index < len(questions):
        users_current_question[user_id] = next_question_index
        ask_question(reply_token, next_question_index)
    else:
        logging.info(f"All questions answered by user {user_id}. Displaying results.")
        display_result(reply_token, users_answers[user_id])
        # Clean up user state after displaying results
        del users_current_question[user_id]
        del users_answers[user_id]

def display_result(reply_token, answers):
    # 計算ロジックに基づく結果を想定
    selected_mbti_type = "ENTP"  # これは例です

    # 診断結果の説明とクイックリプライのボタンを組み合わせたメッセージ
    result_message = f"あなたの看護師タイプは: {selected_mbti_type} です。\n結果を見るには、以下のボタンを押してください。"

    # クイックリプライボタンを作成
    quick_reply_buttons = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="結果を見る", text=selected_mbti_type))
    ])

    # ユーザーにメッセージを送信
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=result_message, quick_reply=quick_reply_buttons)
    )