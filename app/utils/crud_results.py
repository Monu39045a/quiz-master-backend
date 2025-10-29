from sqlalchemy.orm import Session

from app.schemas.results import AnswerSchema
from ..models.results import Result
from ..models.quiz import Question
from typing import List
import json
from datetime import datetime


def create_result(db: Session, result_data: dict) -> Result:
    r = Result(
        quiz_id=result_data['quiz_id'],
        participant_id=result_data['participant_id'],
        trainer_id=result_data.get('trainer_id'),
        quiz_title=result_data.get('quiz_title'),
        score=result_data['score'],
        num_of_questions=result_data['num_of_questions'],
        attempted_at=result_data.get('attempted_at', datetime.utcnow()),
        time_taken_seconds=result_data['time_taken_seconds'],
    )
    r.set_options(result_data.get('options_qna', []))
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def get_result_by_quiz_and_participant(db: Session, quiz_id: int, participant_id: str):
    return db.query(Result).filter(
        Result.quiz_id == quiz_id,
        Result.participant_id == participant_id
    ).first()


def calculate_score(db: Session, answers: List[AnswerSchema]):
    score = 0
    normalized = []
    question_ids = [a.question_id for a in answers]

    rows = db.query(Question).filter(
        Question.id.in_(question_ids)).all()
    correct_map = {r.id: r.correct_answer for r in rows}

    for a in answers:
        qid = a.question_id
        selected = a.selected
        is_correct = (correct_map.get(qid) == selected)
        if is_correct:
            score += 1
        normalized.append({
            "question_id": qid,
            "selected": selected,
            "is_correct": is_correct
        })

    num_questions = len(question_ids)
    return score, num_questions, normalized
