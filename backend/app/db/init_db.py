import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401
from app.models.user import User

logger = structlog.get_logger()

async def init_db(db: AsyncSession) -> None:
    """Bootstrap initial database state including default admin account."""
    # Ensure tables exist even if migrations haven't run yet
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if not settings.bootstrap_admin_username:
        return

    result = await db.execute(
        select(User).where(User.username == settings.bootstrap_admin_username)
    )
    user = result.scalar_one_or_none()

    if not user:
        password = settings.bootstrap_admin_password or "Admin@Sentinel2026!"
        admin = User(
            username=settings.bootstrap_admin_username,
            email=settings.bootstrap_admin_email or "admin@sentineledge.local",
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        logger.info(
            "Bootstrap admin created",
            username=admin.username,
            email=admin.email,
        )
    else:
        logger.info("Admin user already initialized", username=user.username)
