import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate

class CameraRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Camera]:
        result = await self.db.execute(select(Camera).offset(skip).limit(limit).order_by(Camera.created_at.desc()))
        return result.scalars().all()

    async def get_by_id(self, camera_id: uuid.UUID) -> Optional[Camera]:
        result = await self.db.execute(select(Camera).where(Camera.id == camera_id))
        return result.scalar_one_or_none()

    async def create(self, camera_in: CameraCreate) -> Camera:
        camera = Camera(**camera_in.model_dump())
        self.db.add(camera)
        await self.db.commit()
        await self.db.refresh(camera)
        return camera

    async def update(self, camera_id: uuid.UUID, camera_in: CameraUpdate) -> Optional[Camera]:
        camera = await self.get_by_id(camera_id)
        if not camera:
            return None
        update_data = camera_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(camera, key, val)
        await self.db.commit()
        await self.db.refresh(camera)
        return camera

    async def delete(self, camera_id: uuid.UUID) -> bool:
        camera = await self.get_by_id(camera_id)
        if not camera:
            return False
        await self.db.delete(camera)
        await self.db.commit()
        return True
