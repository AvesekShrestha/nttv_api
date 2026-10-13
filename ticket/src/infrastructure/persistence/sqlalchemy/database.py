from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine : AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True)

session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    async with session_factory() as session:
        yield session
 

class Base(DeclarativeBase) : pass
