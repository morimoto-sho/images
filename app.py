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
    "あなたは新しい医療機器をすぐに使いこなせますか？",
    "患者さんの心を温かく包み込むことができますか？",
    "どんな厳しい状況でもブレない強さを持っていますか？",
    "新人ナースとの橋渡し役として、知識を惜しみなく共有しますか？",
    "常に最新の医療知識を追求していますか？",
    "長時間のシフト後も、仕事に対する情熱を保っていますか？",
    "緊急事態に迅速かつ的確に対応できますか？",
    "どんな状況にも柔軟に対応できますか？",
    "チームをまとめ、明確なビジョンのもとにリードできますか？",
    "特定の医療分野や技術において深い知識を持っていますか？",
]


# Nurse types and salary mapping
nurse_types = ["マルチタイプ看護師", "イノベーター看護師", "ハートフル看護師", "アイアン看護師", "ブリッジ看護師", "スカラー看護師", "エンデュランス看護師", "クイックレスポンス看護師", "アダプタブル看護師", "ビジョナリー看護師", "エキスパート看護師"]
salary_map = {
    "マルチタイプ看護師": "900万円",
    # Add other nurse types and their expected salaries here
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
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
    # ここでanswersに基づいて結果を計算します
    # 結果表示のロジックを実装
    result_message = "あなたの看護師タイプは: [結果] です。"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result_message))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)