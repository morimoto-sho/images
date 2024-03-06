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

# Use your LINE channel access token and channel secret
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# Nurse types and salary mapping
nurse_types = ["マルチタイプ看護師", "イノベーター看護師", "ハートフル看護師", "アイアン看護師", "ブリッジ看護師", "スカラー看護師", "エンデュランス看護師", "クイックレスポンス看護師", "アダプタブル看護師", "ビジョナリー看護師", "エキスパート看護師"]
salary_map = {
    "マルチタイプ看護師": "900万円",
    # Add other nurse types and their expected salaries here
}

# Sample questions
questions = [
    "あなたは新しい医療機器をすぐに使いこなせますか？",
    "患者さんの心を温かく包み込むことができますか？",
    "どんな厳しい状況でもブレない強さを持っていますか？",
    "新人ナースとの橋渡し役として、知識を惜しみなく共有しますか？",
    # Add more questions as needed
    "あなたは今転職を考えていますか？",
    "あなたは今の職場に不満を感じていますか？",
]

# This endpoint is called by LINE when a message is sent to the bot
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    if text == "診断開始":
        start_diagnosis(event)

def start_diagnosis(event):
    # Implement logic to start the diagnosis by asking the first question
    pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
