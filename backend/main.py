"""AI Requirement Analysis Workbench - FastAPI entry point."""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.sessions import router as sessions_router
from api.messages import router as messages_router
from api.config import router as config_router
from api.sdd import router as sdd_router
from api.suggestions import router as suggestions_router

app = FastAPI(
    title="AI Requirement Analysis Workbench",
    description="AI Requirement Analysis Workbench API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)
app.include_router(messages_router)
app.include_router(config_router)
app.include_router(sdd_router)
app.include_router(suggestions_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
