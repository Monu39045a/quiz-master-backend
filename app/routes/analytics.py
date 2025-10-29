from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.results import Result

router = APIRouter(tags=["Results"])


@router.get("/quiz/{quiz_id}/analysis")
def get_quiz_analysis(quiz_id: int, db: Session = Depends(get_db)):
    results = db.query(Result).filter(Result.quiz_id == quiz_id).all()
    breakpoint()
    if not results:
        raise HTTPException(
            status_code=404, detail="No results found for this quiz")

    scores = [r.score for r in results]
    times = [r.time_taken_seconds for r in results]
    num_questions = results[0].num_of_questions if results else 0

    num_bins = 5
    bin_size = max(1, num_questions // num_bins)
    score_distribution = {}

    for i in range(0, num_questions + 1, bin_size):
        start = i
        end = min(i + bin_size - 1, num_questions)
        label = f"{start}-{end}"
        count = len([s for s in scores if start <= s <= end])
        score_distribution[label] = count

    # Percentage-based Distribution (optional comparison)
    percent_scores = [(s / num_questions) *
                      100 for s in scores if num_questions > 0]
    percent_bins = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 100)]
    percent_distribution = {
        f"{start}-{end}%": len([p for p in percent_scores if start <= p <= end])
        for start, end in percent_bins
    }

    # Average Stats
    avg_score = sum(scores) / len(scores) if scores else 0
    avg_time = sum(times) / len(times) if times else 0
    fastest_time = min(times) if times else 0
    slowest_time = max(times) if times else 0

    # Score vs Time (for correlation chart)
    score_vs_time = [
        {"participant_id": r.participant_id, "score": r.score,
            "time_taken": r.time_taken_seconds}
        for r in results
    ]

    data = {
        "quiz_id": quiz_id,
        "quiz_title": results[0].quiz_title if results else "",
        "num_participants": len(results),
        "num_questions": num_questions,
        "average_score": round(avg_score, 2),
        "average_time_seconds": round(avg_time, 2),
        "fastest_time_seconds": fastest_time,
        "slowest_time_seconds": slowest_time,
        "score_distribution": score_distribution,      # Absolute bins
        "percentage_distribution": percent_distribution,  # % bins
        "score_vs_time": score_vs_time,                # Scatter/line chart data
    }

    return data
