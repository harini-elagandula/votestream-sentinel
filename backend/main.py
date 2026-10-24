
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import elections, votes, results
from backend.websocket.router import router as websocket_router

app = FastAPI(
    title="VoteStream Sentinel",
    description="Real-Time Online Voting System with Event Streaming",
    version="1.0.0",
)

# Allow the local frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(elections.router)
app.include_router(votes.router)
app.include_router(results.router)
app.include_router(websocket_router)


@app.get("/")
def home():
    return {
        "project": "VoteStream Sentinel",
        "message": "Real-Time Voting API is running",
        "status": "online",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
