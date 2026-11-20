"""Seed database with cameras, zones, and initial rules."""
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.rule import Rule

async def seed():
    print("Seeding initial cameras and detection zones...")
    async with AsyncSessionLocal() as db:
        c1 = Camera(name="Main Entrance North", source_type="rtsp", location="Gate 1", status="online", processing_enabled=True)
        c2 = Camera(name="Industrial Logistics Bay", source_type="rtsp", location="Warehouse", status="online", processing_enabled=True)
        c3 = Camera(name="Employee Concourse", source_type="webcam", location="Lobby", status="online", processing_enabled=True)
        c4 = Camera(name="Perimeter Gate South", source_type="file", location="Fence Line", status="online", processing_enabled=True)
        db.add_all([c1, c2, c3, c4])
        await db.commit()
    print("Database seeding completed.")

if __name__ == "__main__":
    asyncio.run(seed())
