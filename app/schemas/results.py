from ast import List
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime


class AnswerSchema(BaseModel):
    question_id: int
    selected: str


class ResultCreate(BaseModel):
    quiz_id: int
    participant_id: str
    trainer_id: str
    quiz_title: str
    num_of_questions: int
    time_taken_seconds: int
    attempted_at: Optional[datetime] = None
    options_qna: List[AnswerSchema]


class ResultResponse(BaseModel):
    id: int
    quiz_id: int
    participant_id: str
    trainer_id: str
    quiz_title: str
    score: int
    num_of_questions: int
    attempted_at: datetime
    time_taken_seconds: int

    model_config = {
        "from_attributes": True,
    }
