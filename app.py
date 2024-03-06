from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import os
import random

app = Flask(__name__)

# Your Line Bot API and Webhook Handler keys
line_bot_api = LineBotApi('9vhVHnOG2ySYldADpiacTQjwz4cEAEJW93dg3g/BCUGE8q4+WoEJfADJ1Oij0S/XDS6+PwaxHY4cCbxQcqcnSA1ragmegQJxcNax8qYXo51CiPPhWrvfzYFmIJAY7Ri9d7BO3uQLQdg/hXtYCq+bFgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3a6d6100f0621453f5477776424f4cfe')

mandatory_questions = ["あなたは今転職を考えていますか？", "あなたは今の職場に不満を感じていますか？"]
additional_questions = [
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
    # Add other questions here
]
all_questions = mandatory_questions + additional_questions
user_states = {}

nurse_types = [
    "マルチタイプ看護師",
    "イノベーター看護師",
    "ハートフル看護師",
    "アイアン看護師",
    "ブリッジ看護師",
    "スカラー看護師",
    "エンデュランス看護師",
    "クイックレスポンス看護師",
    "アダプタブル看護師",
    "ビジョナリー看護師",
    "エキスパート看護師"
]

# Define any new nurse types or update salaries here (if applicable)

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
    user_id = event.source.user_id
    text = event.message.text
    
    if text == "診断開始":
        selected_questions = random.sample(all_questions, 8) + mandatory_questions
        user_states[user_id] = {'questions': selected_questions, 'answers': [], 'current_question': 0}
        ask_question(event.reply_token, selected_questions[0])
    elif text in ["はい", "いいえ", "どちらでもない"]:
        process_answer(user_id, text, event.reply_token)

def ask_question(reply_token, question):
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label="はい", text="はい")),
        QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ")),
        # Add more options here if needed
    ]
    messages = TextSendMessage(text=question, quick_reply=QuickReply(items=quick_reply_items))
    line_bot_api.reply_message(reply_token, messages)

def process_answer(user_id, text, reply_token):
    state = user_states[user_id]
    state['answers'].append(text)
    if state['questions'][state['current_question']] in mandatory_questions and text == "はい":
        display_result(reply_token, "マルチタイプ看護師")
        del user_states[user_id]
    else:
        state['current_question'] += 1
        if state['current_question'] < len(state['questions']):
            ask_question(reply_token, state['questions'][state['current_question']])
        else:
            nurse_type = calculate_nurse_type(state['answers'])
            display_result(reply_token, nurse_type)
            del user_states[user_id]

def calculate_nurse_type(answers):
    # Implement your logic to calculate the nurse type based on answers
    return "看護師タイプ"  # Placeholder

def display_result(reply_token, nurse_type):
    message = f"あなたの看護師タイプは「{nurse_type}」です。"
    line_bot_api.reply_message(reply_token, TextSendMessage(text=message))

if __name__ == "__main__":
    app.run()
