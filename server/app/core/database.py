from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# class Database:
#     def __init__(self):
#         self.engine = create_async_engine(
#             settings.DATABASE_URL,
#             echo=False
#         )
#         self.session_maker = async_sessionmaker(
#             bind=self.engine,
#             class_=AsyncSession,
#             expire_on_commit=False,
#         )
#         self.Base = declarative_base()

#     async def connect(self):
#         # Force initial connection (optional)
#         async with self.engine.begin() as conn:
#             await conn.run_sync(self.Base.metadata.create_all)

#     async def disconnect(self):
#         await self.engine.dispose()

#     async def get_session(self):
#         async with self.session_maker() as session:
#             yield session


# db = Database()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# async def get_db():
#     async for session in db.get_session():
#         yield session
