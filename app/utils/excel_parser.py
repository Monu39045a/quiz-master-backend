import pandas as pd
import json


def parse_quiz_questions(file_path: str):
    """
    Parses an Excel file containing quiz questions and returns a list of question dictionaries.
    Each dictionary contains question_text, question_type, options (if applicable), and correct_answer.
    """
    df = pd.read_excel(file_path)

    questions = []
    for _, row in df.iterrows():
        question_text = row['Question'],
        question_type = row['Type'].strip(
        ).lower(),  # e.g., 'mcq', 'tf'
        correct_answer = row['Answer']

        if question_type == 'mcq':
            options = [
                str(row["Option1"]).strip(),
                str(row["Option2"]).strip(),
                str(row["Option3"]).strip(),
                str(row["Option4"]).strip()
            ]
        else:
            options = ["True", "False"]

        questions.append({
            "question_text": question_text,
            "question_type": question_type,
            "options": json.dumps(options),
            "correct_answer": correct_answer
        })

    return questions
