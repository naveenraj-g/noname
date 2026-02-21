from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

FHIRBase = declarative_base()


class Database:
    def __init__(self, db_url: str, base):
        self.engine = create_async_engine(db_url, echo=True)
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self.base = base

    async def connect(self):
        # Force initial connection (optional)
        async with self.engine.begin() as conn:
            # await conn.run_sync(self.base.metadata.drop_all)
            await conn.run_sync(self.base.metadata.create_all)

    async def disconnect(self):
        await self.engine.dispose()

    async def get_session(self):
        async with self.session_maker() as session:
            yield session


fhir_db = Database(settings.FHIR_DATABASE_URL, FHIRBase)


# Dependencies
async def get_fhir_db():
    async for session in fhir_db.get_session():
        yield session
