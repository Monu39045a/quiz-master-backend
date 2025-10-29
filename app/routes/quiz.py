from datetime import timezone, datetime
from typing import List
# from http.client import HTTPException
from fastapi import HTTPException
from fastapi import APIRouter, Depends, Query, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.routes.auth import get_current_user
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

################# Quiz Endpoints #################


@router.post("/create")
async def create_quiz(
    title: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    num_questions: int = Form(...),
    duration_minutes: int = Form(...),
    trainer_id: str = Form(...),
    file: UploadFile = None,
    db: Session = Depends(get_db),
    current_user: Session = Depends(get_current_user)
):
    try:
        quiz_start_time = datetime.fromisoformat(start_time)
        quiz_end_time = datetime.fromisoformat(end_time)
    except ValueError as e:
        # Raises a 422 if the datetime format is incorrect
        raise HTTPException(
            status_code=422, detail=f"Invalid date format for start_time or end_time: {e}")

    existing_quiz = (
        db.query(Quiz)
        .filter(and_(
            Quiz.title == title, Quiz.trainer_id == trainer_id, Quiz.start_time == quiz_start_time)
        ).first()
    )
    if existing_quiz:
        raise HTTPException(
            status_code=400, detail="A quiz with this title already exists for this trainer.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    questions_data = parse_quiz_questions(file_path)
    quiz = Quiz(
        title=title,
        start_time=quiz_start_time,
        end_time=quiz_end_time,
        num_questions=num_questions,
        duration_minutes=duration_minutes,
        trainer_id=trainer_id)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    existing_questions = {
        q.question_text.lower().strip() for q in db.query(Question).filter(Question.quiz_id == quiz.id).all()
    }

    new_questions = []
    for q_data in questions_data:
        q_text = q_data["question_text"].strip().lower()
        if q_text in existing_questions:
            continue  # skip duplicates
        new_questions.append(
            Question(
                quiz_id=quiz.id,
                question_text=q_data["question_text"].strip(),
                question_type=q_data["question_type"].strip(),
                options=q_data["options"],
                correct_answer=q_data["correct_answer"].strip(),
            )
        )

    if not new_questions:
        raise HTTPException(
            status_code=400, detail="No new unique questions found in file.")

    db.add_all(new_questions)
    db.commit()

    return {"message": "Quiz created successfully", "quiz_id": quiz.id}


@router.get("/all", response_model=List[QuizResponse])
async def get_all_quizzes(
        role: str = Query(...,
                          description="Role of the user: trainer or participant"),
        trainer_id: str = Query(...,
                                description="Trainer ID of the current user"),
        db: Session = Depends(get_db)):

    now = datetime.now(timezone.utc)
    if role == "trainer":
        quizzes = db.query(Quiz).filter(Quiz.trainer_id == trainer_id).all()
    elif role == "participant":
        quizzes = db.query(Quiz).filter(Quiz.trainer_id != trainer_id).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid role provided")

    for quiz in quizzes:
        if quiz.status == "scheduled" and now >= quiz.start_time:
            quiz.status = "started"
        elif quiz.status in ("scheduled", "started") and now >= quiz.end_time:
            quiz.status = "completed"

    db.commit()
    return quizzes


@router.put("/start/{quiz_id}")
async def start_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.status == "started":
        raise HTTPException(status_code=400, detail="Quiz already started")
    if datetime.utcnow() < quiz.start_time:
        raise HTTPException(
            status_code=400, detail="Quiz cannot be started before start_time")

    quiz.status = "started"
    db.commit()
    db.refresh(quiz)
    return {"message": "Quiz started successfully", "quiz_id": quiz.id, "status": quiz.status}


@router.put("/end/{quiz_id}")
async def end_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.status == "completed":
        raise HTTPException(status_code=400, detail="Quiz already completed")

    quiz.status = "completed"
    db.commit()
    db.refresh(quiz)
    return {"message": "Quiz ended successfully", "quiz_id": quiz.id, "status": quiz.status}


################# Questions Endpoints #################

@router.get("/{quiz_id}/questions", response_model=List[QuestionResponse], response_model_by_alias=True)
def get_quiz_questions(
    quiz_id: int,
    db: Session = Depends(get_db),
    # current_user: Session = Depends(get_current_user)
):
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()

    if not questions:
        raise HTTPException(
            status_code=404, detail="No questions found for this quiz")

    for q in questions:
        if isinstance(q.options, str):
            import json
            try:
                q.options = json.loads(q.options)
            except Exception:
                q.options = []

    return questions
