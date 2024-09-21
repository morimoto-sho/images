from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import os
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

line_bot_api = LineBotApi('J8RVJvI8TzJYBctDJkLbkpHUI4d5G8o7I489CZ6PKSA1T/EXO0MOFy2GNpmSZNsdxzK42HmBH6gsXH20chmKOygiFmGRyOBQzc6B5LSsg8iSkTdkbl8W0Y00i6M6GUhdNxmXfLboyu3ma9g3nzeVfgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('acde0b7b4a5b9c4450af73a772bcd00d')

users_current_question = {}  # ユーザーIDをキーとした現在の質問番号の記録
users_answers = {}  # ユーザーIDをキーとした回答の記録

# 質問リスト
questions = [
    "一人で過ごすよりも、多くの人と関わる仕事が好きですか？",
    "自由で柔軟な職場よりも、明確なルールや指示がある方が働きやすいですか？",
    "チームでの協力よりも、自分のペースで一人で仕事を進める方が好きですか？",
    "事実やデータに基づいた判断をする方が得意ですか？",
    "突発的な変化よりも、事前にしっかり計画された仕事の方が好きですか？",
    "長期的なキャリア計画を持って、計画的に進めることが好きですか？",
    "問題を解決する際、まずは詳細な情報や事実を集めますか？",
    "他人にどう思われるかよりも、合理的な決断を優先しますか？",
    "スケジュールがきっちり決まっている方が安心できますか？",
    "転職などを行い新しい環境に身を置きたいですか？"
]

# 質問に対応するMBTIタイプと点数
# 質問に対応するMBTIタイプと点数を調整
# 質問に対応するMBTIタイプと点数を調整
question_type_mapping = {
    0: {"INTJ": 3, "ENTP": 2, "ESTP": 1},  # エンジニア
    1: {"ESFJ": 3, "ENFJ": 2, "ENTP": 1},  # 営業
    2: {"ISTJ": 3, "ESTJ": 2, "ISFJ": 1},  # 製造
    3: {"ISFJ": 3, "ESFJ": 2, "INFJ": 1},  # 事務
    4: {"INTJ": 3, "ENTP": 2, "ESTJ": 1},  # エンジニア
    5: {"ESFJ": 3, "ENFJ": 2, "ESTJ": 1},  # 営業
    6: {"ISTJ": 3, "ISFJ": 2, "ESTJ": 1},  # 製造
    7: {"INFJ": 3, "ISFJ": 2, "ENFJ": 1},  # 事務
    8: {"ESTP": 3, "ENTJ": 2, "ISTJ": 1},  # エンジニア
    9: {"ENFJ": 3, "ESFJ": 2, "INTP": 1},  # 営業
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
    mbti_scores = {mbti: 0 for mbti in question_nurse_type_mapping[0].keys()}
    
    for question_index, answer in enumerate(answers):
        if answer == "はい":
            for mbti, score in question_nurse_type_mapping[question_index].items():
                mbti_scores[mbti] += score

    highest_score = max(mbti_scores.values())
    top_mbti_types = [mbti for mbti, score in mbti_scores.items() if score == highest_score]
    selected_mbti_type = random.choice(top_mbti_types)
    result_message = f"あなたの職業MBTIタイプは: {selected_mbti_type} です。結果を見るには、以下のボタンを押してください。"

    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(
            text=result_message,
            quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="結果を見る", text=selected_mbti_type))])
        )
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
