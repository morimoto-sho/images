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

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
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

    # ユーザーの回答に基づいて看護師のタイプを判定するロジックをここに実装
# 各ユーザーの回答を追跡
user_answers = {}

# 看護師のタイプと想定年収
# 各看護師のタイプに対応する想定年収
nurse_types = {
    "イノベーター看護師": "800万円",
    "ハートフル看護師": "700万円",
    "アイアン看護師": "850万円",
    "ブリッジ看護師": "750万円",
    "スカラー看護師": "900万円",
    "エンデュランス看護師": "650万円",
    "クイックレスポンス看護師": "800万円",
    "アダプタブル看護師": "700万円",
    "ビジョナリー看護師": "950万円",
    "エキスパート看護師": "1000万円",
}

def determine_nurse_type(answers):
    scores = {key: 0 for key in nurse_types.keys()}

    # 各質問に対する「はい」の回答で特定のタイプのスコアを増加
    question_to_type = [
        ("イノベーター看護師", "ハートフル看護師"),  # 1つ目の質問に対する影響
        ("アイアン看護師", "ブリッジ看護師"),      # 2つ目の質問に対する影響
        # 以下、質問ごとに影響する看護師タイプを追加
    ]

    for i, answer in enumerate(answers):
        if answer == 'yes':
            for nurse_type in question_to_type[min(i, len(question_to_type) - 1)]:
                scores[nurse_type] += 1

    # 最もスコアが高い看護師のタイプを決定
    top_type = max(scores, key=scores.get)
    return top_type, nurse_types[top_type]

# 仮想のユーザー回答
# 実際にはLINE Botからの入力を想定
answers = ["yes", "no", "yes", "yes", "no"]

# 看護師タイプと想定年収を決定
nurse_type, salary = determine_nurse_type(answers)

print(f"あなたの看護師タイプは「{nurse_type}」で、想定年収は{salary}です。")





    # 例: ユーザーからのメッセージに応じて質問を出す
    text = event.message.text  # ユーザーからのメッセージを取得
    if text == "診断開始":
        # 質問を送信
        question_text = questions[0]  # 最初の質問
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=question_text,
                            quick_reply=QuickReply(items=[
                                QuickReplyButton(action=MessageAction(label="はい", text="はい")),
                                QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
                            ]))
        )
    # 他の質問への回答や、診断結果の処理を追加

if __name__ == "__main__":
    app.run()
