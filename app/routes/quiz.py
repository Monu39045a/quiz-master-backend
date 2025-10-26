from fastapi import APIRouter, Depends, UploadFile, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.quiz import Quiz, Question
from ..schemas.quiz import QuestionCreate, QuizCreate, QuizResponse, QuestionResponse
from ..utils.excel_parser import parse_quiz_questions
import os
import shutil
from datetime import datetime

router = APIRouter(tags=["quiz"])

UPLOAD_DIR = "quiz_data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create")
async def create_quiz(
    title: str = Form(...),
    scheduled_datetime: str = Form(...),
    num_questions: int = Form(...),
    duration_minutes: int = Form(...),
    trainer_id: int = Form(...),
    file: UploadFile = None,
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    questions_data = parse_quiz_questions(file_path)
    quiz = Quiz(
        title=title,
        scheduled_time=datetime.fromisoformat(scheduled_datetime),
        num_questions=num_questions,
        duration_minutes=duration_minutes,
        trainer_id=trainer_id)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for q_data in questions_data:
        question = Question(
            quiz_id=quiz.id,
            question_text=q_data["question_text"],
            question_type=q_data["question_type"],
            options=q_data["options"],
            correct_answer=q_data["correct_answer"]
        )
        db.add(question)

    db.commit()
    return {"message": "Quiz created successfully", "quiz_id": quiz.id}
