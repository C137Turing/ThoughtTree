"""User config API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.mysql import get_db
from models.user_config import UserConfig
from models.schemas import UserConfigResponse, UserConfigUpdate

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/", response_model=UserConfigResponse)
async def get_config(db: AsyncSession = Depends(get_db)):
    """Get current user configuration."""
    result = await db.execute(select(UserConfig).where(UserConfig.id == 1))
    config = result.scalar_one_or_none()
    if not config:
        config = UserConfig(id=1)
        db.add(config)
        await db.flush()
        await db.commit()
    return UserConfigResponse.model_validate(config)


@router.put("/", response_model=UserConfigResponse)
async def update_config(req: UserConfigUpdate, db: AsyncSession = Depends(get_db)):
    """Update user configuration."""
    update_data = req.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    await db.execute(
        update(UserConfig).where(UserConfig.id == 1).values(**update_data)
    )
    await db.commit()

    result = await db.execute(select(UserConfig).where(UserConfig.id == 1))
    return UserConfigResponse.model_validate(result.scalar_one())
