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
    # Add more questions
]
# A dictionary to track the state and answers of each user
user_sessions = {}

@app.route("/callback", methods=['POST'])
def callback():
    # Get request body and signature
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    # Handle request
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    # Start diagnosis
    if text == "診断開始":
        user_sessions[user_id] = {'current_question': 0, 'answers': []}
        ask_question(user_id, 0, event.reply_token)
        return
    
    # Handle answer and determine next step
    if user_id in user_sessions:
        session = user_sessions[user_id]
        session['answers'].append(text)  # Store answer
        next_question = session['current_question'] + 1
        
        if next_question < len(questions):
            session['current_question'] = next_question
            ask_question(user_id, next_question, event.reply_token)
        else:
            # All questions answered, determine result
            result = determine_result(session['answers'])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
            del user_sessions[user_id]  # Clear session

def ask_question(user_id, question_index, reply_token):
    question = questions[question_index]
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="はい", text="はい")),
        QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
    ])
    line_bot_api.reply_message(reply_token, TextSendMessage(text=question, quick_reply=quick_reply))

def determine_result(answers):
    # Logic to determine the result based on answers
    return "Your nurse type is: XYZ"  # Placeholder result

if __name__ == "__main__":
    app.run()
