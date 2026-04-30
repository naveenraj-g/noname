from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select

from app.models.vitals.vitals import VitalsModel
from app.schemas.vitals import VitalsCreateSchema, VitalsPatchSchema


class VitalsRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def get_by_vitals_id(self, vitals_id: int) -> Optional[VitalsModel]:
        async with self.session_factory() as session:
            stmt = select(VitalsModel).where(VitalsModel.vitals_id == vitals_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_me(self, user_id: str, org_id: Optional[str]) -> List[VitalsModel]:
        async with self.session_factory() as session:
            stmt = select(VitalsModel).where(VitalsModel.user_id == user_id)
            if org_id:
                stmt = stmt.where(VitalsModel.org_id == org_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def list(
        self,
        user_id: Optional[str] = None,
        patient_id: Optional[int] = None,
        org_id: Optional[str] = None,
    ) -> List[VitalsModel]:
        async with self.session_factory() as session:
            stmt = select(VitalsModel)
            if user_id:
                stmt = stmt.where(VitalsModel.user_id == user_id)
            if patient_id is not None:
                stmt = stmt.where(VitalsModel.patient_id == patient_id)
            if org_id:
                stmt = stmt.where(VitalsModel.org_id == org_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def create(
        self,
        payload: VitalsCreateSchema,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> VitalsModel:
        data = payload.model_dump(exclude_unset=False)
        vitals = VitalsModel(
            user_id=user_id,
            org_id=org_id,
            **data,
        )
        async with self.session_factory() as session:
            try:
                session.add(vitals)
                await session.commit()
                await session.refresh(vitals)
            except Exception:
                await session.rollback()
                raise
        return await self.get_by_vitals_id(vitals.vitals_id)

    async def patch(
        self, vitals_id: int, payload: VitalsPatchSchema
    ) -> Optional[VitalsModel]:
        async with self.session_factory() as session:
            stmt = select(VitalsModel).where(VitalsModel.vitals_id == vitals_id)
            result = await session.execute(stmt)
            vitals = result.scalars().first()

            if not vitals:
                return None

            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(vitals, field, value)

            try:
                await session.commit()
                await session.refresh(vitals)
            except Exception:
                await session.rollback()
                raise

        return await self.get_by_vitals_id(vitals_id)

    async def delete(self, vitals_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(VitalsModel).where(VitalsModel.vitals_id == vitals_id)
            result = await session.execute(stmt)
            vitals = result.scalars().first()

            if not vitals:
                return False

            try:
                await session.delete(vitals)
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise
