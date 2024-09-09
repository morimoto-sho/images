import random
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 質問リスト
questions = [
    "患者さんの意見や感情に敏感ですか？",
    "新しい方法や技術を積極的に取り入れようとしますか？",
    "プレッシャーの中でも冷静に対応できますか？",
    "あなたは今転職を考えていますか？",
    "計画を立てて目標に向かって頑張ることが得意ですか？",
    "新しい場面や状況に柔軟に対応できますか？",
    "異性との出会いを求めていますか？",
    "自分の強みや弱みを理解していますか？",
    "規則や手続きを重視しますか？",
    "自分の感情や考えを明確に述べることが得意ですか？",
    "物事を組織的に進めるのが好きですか？",
    "あなたは今の職場に不満を感じていますか？",
]

# 質問に対応するMBTIタイプと点数
question_nurse_type_mapping = {
    0: {"INFJ": 2, "ISFJ": 2, "ENFJ": 2, "ESFJ": 2, "INFP": 2, "ISFP": 2, "ENFP": 2, "ESFP": 2},
    1: {"ENTP": 2, "INTP": 2, "ENTJ": 2, "INTJ": 2, "ENFP": 2, "INFP": 2, "ENTJ": 1, "INTJ": 1},
    2: {"ISTJ": 2, "ESTJ": 2, "INTJ": 2, "ENTJ": 2, "ISFJ": 2, "INFJ": 1},  
    3: {"ENTP": 5, "ESTJ": 1, "ISTJ": 1, "INFJ": 2, "INTP": 2},
    4: {"INTJ": 2, "ENTJ": 2, "ISTJ": 2, "ESTJ": 2, "ISFJ": 1},  
    5: {"ENFP": 2, "INFP": 2, "ENTP": 2, "INTP": 2, "ESFP": 1, "ISFP": 1},  
    6: {"ESFP": 2, "ISFP": 2, "ENFP": 2, "INFP": 2},  
    7: {"INTJ": 2, "INFJ": 2, "ISTJ": 1, "ISFJ": 1, "ENFP": 1, "ISFP": 1},  
    8: {"ENFJ": 2, "ESFJ": 2, "INFJ": 2, "ISFJ": 2, "ESTJ": 1, "ISTJ": 1},  
    9: {"ENTJ": 2, "INTJ": 2, "ENTP": 1, "INTP": 1, "ENFJ": 2, "ESFJ": 1},  
    10: {"ENTP": 2, "INTJ": 1, "INFJ": 1, "ISFJ": 1, "ESTJ": 1},  
    11: {"ENTP": 2, "INTJ": 1, "INFJ": 1, "ISFJ": 1, "ISFP": 1},  
}

def ask_question(question_index):
    question = questions[question_index]
    logging.info(f"Question {question_index}: {question}")

def process_answer(user_id, answer, current_question_index):
    users_answers[user_id].append(answer)
    next_question_index = current_question_index + 1
    if next_question_index < len(questions):
        ask_question(next_question_index)
        return next_question_index
    else:
        display_result(user_id)

def display_result(user_id):
    # 全質問に対応するMBTIタイプを一括で取得し、初期化
    all_mbti_types = set()
    for mapping in question_nurse_type_mapping.values():
        all_mbti_types.update(mapping.keys())

    mbti_scores = {mbti: 0 for mbti in all_mbti_types}  # 全てのMBTIタイプを初期化
    
    # 各質問の回答に基づいてスコアを加算
    for question_index, answer in enumerate(users_answers[user_id]):
        if answer == "はい":
            for mbti, score in question_nurse_type_mapping[question_index].items():
                mbti_scores[mbti] += score

    highest_score = max(mbti_scores.values())
    
    if highest_score == 0:
        logging.error("診断結果が生成できませんでした。")
        return

    top_mbti_types = [mbti for mbti, score in mbti_scores.items() if score == highest_score]
    
    if not top_mbti_types:
        logging.error("診断結果が生成できませんでした。")
        return

    selected_mbti_type = random.choice(top_mbti_types)
    result_message = f"診断結果: あなたの看護師タイプは {selected_mbti_type} です。"
    logging.info(result_message)

def test_diagnosis():
    user_id = "test_user"
    users_current_question[user_id] = 0
    users_answers[user_id] = []
    current_question_index = 0
    
    # 全て「はい」と回答するシミュレーション
    for _ in range(len(questions)):
        current_question_index = process_answer(user_id, "はい", current_question_index)

if __name__ == "__main__":
    users_current_question = {}
    users_answers = {}
    
    test_diagnosis()  # ターミナルでシミュレーション実行

