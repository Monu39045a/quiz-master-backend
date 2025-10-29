from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import auth, quiz, results, analytics


Base.metadata.create_all(bind=engine)
app = FastAPI(title="Quiz App Backend", version="1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Frontend URLs allowed to access
    allow_credentials=True,           # Allow cookies / auth headers
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)

app.include_router(auth.router, prefix="/auth")
app.include_router(quiz.router, prefix="/quiz")
app.include_router(results.router, prefix="/results")
app.include_router(analytics.router, prefix="/analytics")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Quiz App Backend!",
        "version": app.version,
        "title": app.title
    }
