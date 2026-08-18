from fastapi import APIRouter, Query
from graphs.suggest_graph import generate_suggestions

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("")
async def get_suggestions(root_id: str = Query(...)):
    return await generate_suggestions(root_id)
