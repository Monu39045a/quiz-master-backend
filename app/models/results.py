import json
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime, timezone
import json


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    participant_id = Column(String, ForeignKey(
        "users.user_id"), nullable=False)
    trainer_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    quiz_title = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    num_of_questions = Column(Integer, nullable=False)
    attempted_at = Column(DateTime(timezone=True),
                          default=lambda: datetime.now(timezone.utc))
    time_taken_seconds = Column(Integer, nullable=False)
    options_qna = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("quiz_id", "participant_id",
                         name="uq_quiz_participant_once"),
    )

    # Relationships
    quiz = relationship("Quiz")
    participant = relationship("User", foreign_keys=[participant_id])
    trainer = relationship("User", foreign_keys=[trainer_id])

    def set_options(self, options):
        self.options_qna = json.dumps(options)

    def get_options(self):
        return json.loads(self.options_qna) if self.options_qna else []
