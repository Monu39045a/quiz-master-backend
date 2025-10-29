from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.results import ResultResponse, ResultCreate
from ..utils.crud_results import calculate_score, create_result, get_result_by_quiz_and_participant
router = APIRouter(tags=["Results"])


@router.post("/submits")
async def submit_result(request: Request):
    body = await request.json()
    print("Incoming payload:", body)


@router.post("/submit", response_model=ResultResponse)
def submit_quiz(payload: ResultCreate, db: Session = Depends(get_db)):
    breakpoint()
    existing = get_result_by_quiz_and_participant(
        db, payload.quiz_id, payload.participant_id
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="You have already attempted this quiz.")

    score, num_questions, normalized = calculate_score(
        db, payload.options_qna)
    breakpoint()
    result_data = {
        "quiz_id": payload.quiz_id,
        "participant_id": payload.participant_id,
        "trainer_id": payload.trainer_id,
        "quiz_title": payload.quiz_title,
        "score": score,
        "num_of_questions": payload.num_of_questions,
        "attempted_at": payload.attempted_at,
        "time_taken_seconds": payload.time_taken_seconds,
        "options_qna": normalized,
    }

    result = create_result(db, result_data)

    return result
