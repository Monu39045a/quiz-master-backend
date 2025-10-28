from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List


class QuestionCreate(BaseModel):
    question_text: str
    question_type: str  # e.g., 'mcq', 'tf'
    options: Optional[List[str]] = None  # JSON string for options if MCQ
    correct_answer: str


class QuestionResponse(BaseModel):
    ques_id: int = Field(alias="id")
    quiz_id: int
    question_text: str
    question_type: str
    options: List[str] = None
    correct_answer: str

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class QuizCreate(BaseModel):
    trainer_id: str
    title: str
    start_time: datetime
    end_time: datetime
    num_questions: int
    duration_minutes: int


class QuizResponse(BaseModel):
    id: int
    trainer_id: str
    title: str
    start_time: datetime
    end_time: datetime
    num_questions: int
    duration_minutes: int
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
