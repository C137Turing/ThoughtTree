"""SDD generation and quality check API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from graphs.sdd_graph import generate_sdd, get_task
from graphs.quality_graph import run_quality_check

router = APIRouter(prefix="/api/sdd", tags=["sdd"])


class GenerateRequest(BaseModel):
    root_id: str
    force: bool = False


class GenerateResponse(BaseModel):
    task_id: str


class TaskResponse(BaseModel):
    status: str
    sdd: str | None = None


class QualityCheckRequest(BaseModel):
    root_id: str


@router.post("/generate", response_model=GenerateResponse)
async def start_generation(req: GenerateRequest):
    if not req.force:
        quality = await run_quality_check(req.root_id)
        if not quality.get("overall", {}).get("passed", False):
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Quality check failed. Use force=true to skip.",
                    "report": quality,
                },
            )
    task_id = await generate_sdd(req.root_id)
    return {"task_id": task_id}


@router.get("/task/{task_id}", response_model=TaskResponse)
async def check_task(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": task["status"], "sdd": task["sdd"]}


@router.post("/quality/check")
async def quality_check(req: QualityCheckRequest):
    return await run_quality_check(req.root_id)