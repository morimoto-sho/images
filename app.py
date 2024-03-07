import os
import random
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
    "新しい方法や技術を積極的に取り入れようとしますか？",
    "チームワークを大切にしますか？",
    "他人の立場や感情を理解するのが得意ですか？",
    "夢や目標を持っていますか？",
    "患者さんの希望やニーズを優先しますか？",
    "プレッシャーの中でも冷静に対応できますか？",
    "計画を立てて目標に向かって頑張ることが得意ですか？",
    "新しい場面や状況に柔軟に対応できますか？",
    "人々との関係を楽しむことが多いですか？",
    "変化を楽しみますか？",
    "自分の強みや弱みを理解していますか？",
    "他人を励ますことが好きですか？",
    "規則や手続きを重視しますか？",
    "自分の感情や考えを明確に述べることが得意ですか？",
    "物事を組織的に進めるのが好きですか？",
    "あなたは今転職を考えていますか？",
    "あなたは今の職場に不満を感じていますか？",
]

# 各質問に対する看護師タイプの対応関係と点数
question_nurse_type_mapping = {
    0: {"はい": {"INFJ": 2, "ISFJ": 2, "ENFJ": 2, "ESFJ": 2, "INFP": 2, "ISFP": 2, "ENFP": 1, "ESFP": 1}},  # 感情に敏感（感情）
    1: {"はい": {"ENTP": 2, "INTP": 2, "ENTJ": 2, "INTJ": 2, "ENFP": 1, "INFP": 1}},  # 新しい技術（直感）
    2: {"はい": {"ESFJ": 2, "ISFJ": 2, "ENFJ": 2, "INFJ": 2, "ESTJ": 1, "ISTJ": 1}},  # チームワーク（感情）
    3: {"はい": {"INFJ": 2, "INFP": 2, "ENFJ": 2, "ENFP": 2, "ISFJ": 1, "ISFP": 1}},  # 他人の感情理解（感情）
    4: {"はい": {"INTJ": 2, "ENTJ": 2, "INFJ": 1, "ENFJ": 1}},  # 目標志向（直感＋判断）
    5: {"はい": {"ISFJ": 2, "ESFJ": 2, "ISFP": 2, "ESFP": 2, "INFJ": 1, "ENFJ": 1}},  # 患者中心（感情）
    6: {"はい": {"ISTJ": 2, "ESTJ": 2, "INTJ": 2, "ENTJ": 2}},  # 冷静さ（思考）
    7: {"はい": {"INTJ": 2, "ENTJ": 2, "ISTJ": 2, "ESTJ": 2}},  # 計画性（判断）
    8: {"はい": {"ENFP": 2, "INFP": 2, "ENTP": 2, "INTP": 2}},  # 柔軟性（知覚）
    9: {"はい": {"ESFP": 2, "ISFP": 2, "ENFP": 2, "INFP": 2}},  # 社交性（外向性）
    10: {"はい": {"ENTP": 2, "INTP": 2, "ENFP": 2, "INFP": 2}},  # 変化を楽しむ（知覚）
    11: {"はい": {"INTJ": 2, "INFJ": 2, "ISTJ": 1, "ISFJ": 1}},  # 自己認識（内向性）
    12: {"はい": {"ENFJ": 2, "ESFJ": 2, "INFJ": 2, "ISFJ": 2}},  # 励ます（感情）
    13: {"はい": {"ISTJ": 2, "ESTJ": 2, "ISFJ": 1, "ESFJ": 1}},  # 規則重視（判断）
    14: {"はい": {"ENTJ": 2, "INTJ": 2, "ENTP": 1, "INTP": 1}},  # 明確な表現（思考）
    15: {"はい": {"ENTP": 100}} , # 組織的（判断）
    16: {"はい": {"ENTP": 100}} , # 組織的（判断）
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
        ask_question(event, 0)
    elif text in ["はい", "いいえ"]:
        users_answers[user_id].append(text)
        next_question_index = users_current_question[user_id] + 1
        if next_question_index < len(questions):
            users_current_question[user_id] = next_question_index
            ask_question(event, next_question_index)
        else:
            # 診断結果を表示
            display_result(event, users_answers[user_id])

def ask_question(event, question_index):
    question = questions[question_index]
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=question,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(action=MessageAction(label="はい", text="はい")),
                            QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
                        ])))

def display_result(event, answers):
    # 各MBTIタイプのスコアを計算
    mbti_scores = {mbti: 0 for mbti in ["INFJ", "ISFJ", "ENFJ", "ESFJ", "ISTP", "ESTP", "ISTJ", "ESTJ", "ENFP", "ENTP", "INFP", "INTP", "ISFP", "ESFP", "ENTJ", "INTJ"]}
    
    for question_index, answer in enumerate(answers):
        if answer == "はい":
            for mbti, score in question_nurse_type_mapping[question_index]["はい"].items():
                mbti_scores[mbti] += score

    # 最も高いスコアのMBTIタイプを見つける
    highest_score = max(mbti_scores.values())
    top_mbti_types = [mbti for mbti, score in mbti_scores.items() if score == highest_score]

    # ランダムに1つのMBTIタイプを選択（複数のタイプが最高スコアの場合）
    selected_mbti_type = random.choice(top_mbti_types)
    
    # 診断結果を表示
    result_message = f"あなたの看護師タイプは: {selected_mbti_type} です。"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result_message))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
