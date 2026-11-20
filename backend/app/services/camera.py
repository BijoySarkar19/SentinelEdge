import uuid
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.repositories.camera import CameraRepository

class CameraService:
    def __init__(self, db: AsyncSession):
        self.repo = CameraRepository(db)

    async def list_cameras(self, skip: int = 0, limit: int = 100) -> list[CameraResponse]:
        cams = await self.repo.get_all(skip, limit)
        return [CameraResponse.model_validate(c) for c in cams]

    async def get_camera(self, camera_id: uuid.UUID) -> Optional[CameraResponse]:
        c = await self.repo.get_by_id(camera_id)
        if not c:
            return None
        return CameraResponse.model_validate(c)

    async def create_camera(self, camera_in: CameraCreate) -> CameraResponse:
        c = await self.repo.create(camera_in)
        return CameraResponse.model_validate(c)

    async def update_camera(self, camera_id: uuid.UUID, camera_in: CameraUpdate) -> Optional[CameraResponse]:
        c = await self.repo.update(camera_id, camera_in)
        if not c:
            return None
        return CameraResponse.model_validate(c)

    async def delete_camera(self, camera_id: uuid.UUID) -> bool:
        return await self.repo.delete(camera_id)
