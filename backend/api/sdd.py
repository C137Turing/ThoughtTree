"""SDD generation API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from graphs.sdd_graph import generate_sdd, get_task

router = APIRouter(prefix="/api/sdd", tags=["sdd"])


class GenerateRequest(BaseModel):
    root_id: str


class GenerateResponse(BaseModel):
    task_id: str


class TaskResponse(BaseModel):
    status: str
    sdd: str | None = None


@router.post("/generate", response_model=GenerateResponse)
async def start_generation(req: GenerateRequest):
    task_id = await generate_sdd(req.root_id)
    return {"task_id": task_id}


@router.get("/task/{task_id}", response_model=TaskResponse)
async def check_task(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": task["status"], "sdd": task["sdd"]}