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

# Substitute these with your LINE channel access token and channel secret
line_bot_api = LineBotApi('9vhVHnOG2ySYldADpiacTQjwz4cEAEJW93dg3g/BCUGE8q4+WoEJfADJ1Oij0S/XDS6+PwaxHY4cCbxQcqcnSA1ragmegQJxcNax8qYXo51CiPPhWrvfzYFmIJAY7Ri9d7BO3uQLQdg/hXtYCq+bFgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3a6d6100f0621453f5477776424f4cfe')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Sample questions
questions = [
    "あなたは新しい医療機器をすぐに使いこなせますか？",
    "患者さんの心を温かく包み込むことができますか？",
    "あなたは今転職を考えていますか？"
]

# Mapping of nurse types to a brief description
nurse_types = {
    "イノベーター看護師": "技術革新をリードする看護師",
    "ハートフル看護師": "患者の心に寄り添う看護師",
    "マルチタイプ看護師": "多岐にわたる能力を持つ万能看護師"
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
    text = event.message.text
    user_id = event.source.user_id

    if text == "診断開始":
        # Start the diagnosis by sending the first question
        ask_question(event.reply_token, 0, user_id)
    else:
        # Handle answering logic here (simplified for this example)
        if text in ["はい", "いいえ"]:
            # Determine the nurse type based on the answer (simplified logic)
            if text == "はい":
                nurse_type = "イノベーター看護師"
            else:
                nurse_type = "ハートフル看護師"
            
            # Send the diagnosis result
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"あなたの看護師タイプは「{nurse_type}」です。{nurse_types[nurse_type]}")
            )

def ask_question(reply_token, question_index, user_id):
    # Send a question to the user
    question_text = questions[question_index]
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=question_text,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(action=MessageAction(label="はい", text="はい")),
                            QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
                        ])))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
