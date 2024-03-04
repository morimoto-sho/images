from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET'))

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
    user_message = event.message.text

    if user_message == "診断開始":
        questions = [
            "あなたは新しい医療機器をすぐに使いこなせますか？",
            # 他の質問を追加...
        ]
        question = questions[0]  # 最初の質問を送信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=question)
        )
    elif user_message in ["はい", "いいえ"]:  # 簡単な例として、ユーザーが「はい」または「いいえ」と答えた場合
        # ここで質問ごとの処理や、最終的なタイプを決定するロジックを追加
        reply_message = "あなたの回答を受け取りました。"  # 実際には、ユーザーの回答に基づいた処理を行う
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="「診断開始」と送信してください。")
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
