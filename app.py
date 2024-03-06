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
import os
import random

app = Flask(__name__)

# 環境変数からトークンとシークレットを取得
line_bot_api = LineBotApi(os.environ['YOUR_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['YOUR_CHANNEL_SECRET'])

# 質問リスト
all_questions = [
    # 必ず出題される質問
    "あなたは今転職を考えていますか？",
    "あなたは今の職場に不満を感じていますか？",
    # ランダムに選ばれるその他の質問
    "あなたは新しい医療技術に興味がありますか？",
    "チームワークを大切にしますか？",
    "患者さんの心のケアも大切だと思いますか？",
    "リーダーシップを発揮することが得意ですか？",
    # その他多数の質問をここに追加...
]

# ユーザーの回答を管理する辞書
user_answers = {}

@app.route("/callback", methods=['POST'])
def callback():
    # 省略...

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id

    if user_id not in user_answers:
        # 初めてのユーザーであれば、初期化
        user_answers[user_id] = {"answers": [], "current_question": 0, "questions": generate_questions()}

    text = event.message.text
    user_data = user_answers[user_id]

    if text == "診断開始":
        # 質問の初期化
        user_data["answers"] = []
        user_data["current_question"] = 0
        user_data["questions"] = generate_questions()
        send_question(event.reply_token, user_data["questions"][user_data["current_question"]])
    elif text in ["はい", "いいえ"]:
        user_data["answers"].append(text)
        # 「マルチタイプ看護師」に該当するかのチェック
        if user_data["current_question"] < 2 and text == "はい":
            send_result(event.reply_token, "マルチタイプ看護師")
            del user_answers[user_id]  # ユーザー情報を削除
            return
        # 次の質問へ
        user_data["current_question"] += 1
        if user_data["current_question"] < len(user_data["questions"]):
            send_question(event.reply_token, user_data["questions"][user_data["current_question"]])
        else:
            # 全質問に回答したら結果を送信
            nurse_type = determine_nurse_type(user_data["answers"])
            send_result(event.reply_token, nurse_type)
            del user_answers[user_id]  # ユーザー情報を削除
    else:
        # 不明なメッセージには何もしない
        return

def generate_questions():
    # 必ず出題される質問2つとランダムな質問18個を選択
    selected_questions = random.sample(all_questions[2:], 18)
    return all_questions[:2] + selected_questions

def send_question(reply_token, question_text):
    # 省略...

def determine_nurse_type(
