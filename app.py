from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
)
import os
import random
import logging

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
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    # 診断開始の処理
    if text == "診断開始":
        users_current_question[user_id] = 0
        users_answers[user_id] = []
        ask_question(event.reply_token, 0)
    # 回答の処理
    elif text in ["はい", "いいえ"] and user_id in users_current_question:
        process_answer(user_id, text, event.reply_token)

def ask_question(reply_token, question_index):
    question = questions[question_index]
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(
            text=question,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="はい", text="はい")),
                QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
            ])
        )
    )

def process_answer(user_id, text, reply_token):
    users_answers[user_id].append(text)
    next_question_index = users_current_question[user_id] + 1
    if next_question_index < len(questions):
        users_current_question[user_id] = next_question_index
        ask_question(reply_token, next_question_index)
    else:
        display_result(reply_token, users_answers[user_id], user_id)

def display_result(reply_token, answers, user_id):
    mbti_scores = {mbti: 0 for mbti in ["INFJ", "ISFJ", "ENFJ", "ESFJ", "ISTP", "ESTP", "ISTJ", "ESTJ", "ENFP", "ENTP", "INFP", "INTP", "ISFP", "ESFP", "ENTJ", "INTJ"]}
    
    for question_index, answer in enumerate(answers):
        if answer == "はい":
            for mbti, score in question_nurse_type_mapping[question_index]["はい"].items():
                mbti_scores[mbti] += score

    highest_score = max(mbti_scores.values())
    top_mbti_types = [mbti for mbti, score in mbti_scores.items() if score == highest_score]
    selected_mbti_type = random.choice(top_mbti_types)

    # 診断結果をユーザーが送信できるようにクイックリプライを設定
    quick_reply_buttons = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="結果を見る", text=selected_mbti_type))
    ])

    result_message = f"あなたの看護師タイプは: {selected_mbti_type} です。結果を見るには、以下のボタンを押してください。"

    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=result_message, quick_reply=quick_reply_buttons)
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)