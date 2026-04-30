from typing import List, Optional

from app.models.vitals.vitals import VitalsModel
from app.repository.vitals_repository import VitalsRepository
from app.schemas.vitals import VitalsCreateSchema, VitalsPatchSchema


class VitalsService:
    def __init__(self, repository: VitalsRepository):
        self.repository = repository

    async def get_raw_by_vitals_id(self, vitals_id: int) -> Optional[VitalsModel]:
        return await self.repository.get_by_vitals_id(vitals_id)

    async def get_vitals(self, vitals_id: int) -> Optional[VitalsModel]:
        return await self.repository.get_by_vitals_id(vitals_id)

    async def get_me(
        self, user_id: str, org_id: Optional[str]
    ) -> List[VitalsModel]:
        return await self.repository.get_me(user_id, org_id)

    async def list_vitals(
        self,
        user_id: Optional[str] = None,
        patient_id: Optional[int] = None,
        org_id: Optional[str] = None,
    ) -> List[VitalsModel]:
        return await self.repository.list(
            user_id=user_id, patient_id=patient_id, org_id=org_id
        )

    async def create_vitals(
        self,
        payload: VitalsCreateSchema,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> VitalsModel:
        return await self.repository.create(payload, user_id, org_id)

    async def patch_vitals(
        self, vitals_id: int, payload: VitalsPatchSchema
    ) -> Optional[VitalsModel]:
        return await self.repository.patch(vitals_id, payload)

    async def delete_vitals(self, vitals_id: int) -> bool:
        return await self.repository.delete(vitals_id)
