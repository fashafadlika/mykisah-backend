from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal

# Dependency FastAPI — menyediakan sesi database async per request, auto-close setelah selesai.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
