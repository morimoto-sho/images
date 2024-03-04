from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
)
import os

app = Flask(__name__)

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# 模拟数据库或持久化存储，用于追踪每个用户的答案
user_states = {}

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
        "あなたは今転職を考えていますか？",
        "あなたは今の職場に不満を感じていますか？",
]

# 看護師のタイプを決定する関数
def determine_nurse_type(answers):
    # スコア計算ロジック...
    # この例では、単純に回答からランダムに選ぶ
    import random
    nurse_types = ["イノベーター看護師", "ハートフル看護師", "アイアン看護師", "ブリッジ看護師", "スカラー看護師"]
    chosen_type = random.choice(nurse_types)
    return chosen_type, "800万円"

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
    message_text = event.message.text

    # ユーザーの状態と回答を管理
    if user_id not in user_states:
        user_states[user_id] = {
            "questions_answered": 0,
            "answers": []
        }
    
    # 回答を保存
    user_states[user_id]["answers"].append(message_text)
    user_states[user_id]["questions_answered"] += 1
    
    # 全ての質問に答えたかチェック
    if user_states[user_id]["questions_answered"] == len(questions):
        nurse_type, salary = determine_nurse_type(user_states[user_id]["answers"])
        message = f"あなたの看護師タイプは「{nurse_type}」で、想定年収は{salary}です。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )
        # ユーザーの状態をリセット
        del user_states[user_id]
    else:
        # 次の質問を送る
        next_question = questions[user_states[user_id]["questions_answered"]]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=next_question)
        )

if __name__ == "__main__":
    app.run()

