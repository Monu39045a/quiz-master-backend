from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List


class QuestionCreate(BaseModel):
    question_text: str
    question_type: str  # e.g., 'mcq', 'tf'
    options: Optional[List[str]] = None  # JSON string for options if MCQ
    correct_answer: str


class QuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str

    model_config = {
        "from_attributes": True
    }


class QuizCreate(BaseModel):
    trainer_id: str
    title: str
    scheduled_time: Optional[datetime] = None
    num_questions: int
    duration_minutes: int


class QuizResponse(BaseModel):
    id: int
    trainer_id: str
    title: str
    scheduled_time: datetime
    num_questions: int
    duration_minutes: int
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
