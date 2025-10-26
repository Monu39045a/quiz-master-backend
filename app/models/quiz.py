from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime, timezone
import enum


class QuizStatus(enum.Enum):
    scheduled = "scheduled"
    started = "started"
    completed = "completed"


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String, nullable=False)
    scheduled_time = Column(DateTime(timezone=True),
                            default=lambda: datetime.now(timezone.utc))
    num_questions = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(Enum(QuizStatus), default=QuizStatus.scheduled)
    created_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc))

    # Relationships
    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete")
    trainer = relationship("User", back_populates="quizzes")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(String, nullable=False)
    question_type = Column(String, nullable=False)  # e.g., 'mcq', 'tf'
    options = Column(String, nullable=True)  # JSON string for options if MCQ
    correct_answer = Column(String, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
