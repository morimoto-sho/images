from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import os
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

line_bot_api = LineBotApi('9vhVHnOG2ySYldADpiacTQjwz4cEAEJW93dg3g/BCUGE8q4+WoEJfADJ1Oij0S/XDS6+PwaxHY4cCbxQcqcnSA1ragmegQJxcNax8qYXo51CiPPhWrvfzYFmIJAY7Ri9d7BO3uQLQdg/hXtYCq+bFgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3a6d6100f0621453f5477776424f4cfe')

users_current_question = {}  # ユーザーIDをキーとした現在の質問番号の記録
users_answers = {}  # ユーザーIDをキーとした回答の記録

# 質問リスト
questions = [
    "患者さんの意見や感情に敏感ですか？",
    "新しい方法や技術を積極的に取り入れようとしますか？",
    "プレッシャーの中でも冷静に対応できますか？",
    "あなたは今転職を考えていますか？",
    "計画を立てて目標に向かって頑張ることが得意ですか？",
    "新しい場面や状況に柔軟に対応できますか？",
    "異性との出会いを求めていますか？",
    "自分の強みや弱みを理解していますか？",
    "規則や手続きを重視しますか？",
    "自分の感情や考えを明確に述べることが得意ですか？",
    "物事を組織的に進めるのが好きですか？",
    "あなたは今の職場に不満を感じていますか？",
]

# 質問に対応するMBTIタイプと点数を調整
question_nurse_type_mapping = {
    0: {"INFJ": 2, "ISFJ": 2, "ENFJ": 2, "ESFJ": 2, "INFP": 2, "ISFP": 2, "ENFP": 2, "ESFP": 2},
    1: {"ENTP": 2, "INTP": 2, "ENTJ": 2, "INTJ": 2, "ENFP": 2, "INFP": 2, "ENTJ": 1, "INTJ": 1},
    2: {"ISTJ": 2, "ESTJ": 2, "INTJ": 2, "ENTJ": 2, "ISFJ": 2, "INFJ": 1},  
    3: {"ENTP": 5, "ESTJ": 1, "ISTJ": 1, "INFJ": 2, "INTP": 2},
    4: {"INTJ": 2, "ENTJ": 2, "ISTJ": 2, "ESTJ": 2, "ISFJ": 1},  
    5: {"ENFP": 2, "INFP": 2, "ENTP": 2, "INTP": 2, "ESFP": 1, "ISFP": 1},  
    6: {"ESFP": 2, "ISFP": 2, "ENFP": 2, "INFP": 2},  
    7: {"INTJ": 2, "INFJ": 2, "ISTJ": 1, "ISFJ": 1, "ENFP": 1, "ISFP": 1},  
    8: {"ENFJ": 2, "ESFJ": 2, "INFJ": 2, "ISFJ": 2, "ESTJ": 1, "ISTJ": 1},  
    9: {"ENTJ": 2, "INTJ": 2, "ENTP": 1, "INTP": 1, "ENFJ": 2, "ESFJ": 1},  
    10: {"ENTP": 2, "INTJ": 1, "INFJ": 1, "ISFJ": 1, "ESTJ": 1},  
    11: {"ENTP": 2, "INTJ": 1, "INFJ": 1, "ISFJ": 1, "ISFP": 1},  
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

    if text == "診断開始(少しお待ちください)":
        users_current_question[user_id] = 0
        users_answers[user_id] = []
        ask_question(event.reply_token, 0)
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
    # 全質問に対応するMBTIタイプを一括で取得し、初期化
    all_mbti_types = set()
    for mapping in question_nurse_type_mapping.values():
        all_mbti_types.update(mapping.keys())

    mbti_scores = {mbti: 0 for mbti in all_mbti_types}  # 全てのMBTIタイプを初期化
    
    # 各質問の回答に基づいてスコアを加算
    for question_index, answer in enumerate(answers):
        if answer == "はい":
            for mbti, score in question_nurse_type_mapping[question_index].items():
                mbti_scores[mbti] += score

    highest_score = max(mbti_scores.values())
    
    # 合計スコアがゼロの場合の処理を追加
    if highest_score == 0:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="診断結果が生成できませんでした。もう一度お試しください。"))
        return

    # スコアが最大のMBTIタイプを選択
    top_mbti_types = [mbti for mbti, score in mbti_scores.items() if score == highest_score]
    
    # 結果が出ない場合のチェックを追加
    if not top_mbti_types:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="診断結果が生成できませんでした。もう一度お試しください。"))
        return

    selected_mbti_type = random.choice(top_mbti_types)
    result_message = f"あなたの看護師タイプは: {selected_mbti_type} です。結果を見るには、以下のボタンを押してください。"

    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(
            text=result_message,
            quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="結果を見る", text=selected_mbti_type))])
        )
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)