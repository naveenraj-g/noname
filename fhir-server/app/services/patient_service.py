from app.repository.patient_repository import PatientRepository
from app.schemas.resources import PatientCreateSchema, PatientResponseSchema


class PatientService:
    def __init__(self, repository: PatientRepository):
        self.repository = repository

    async def create_patient(
        self, patient: PatientCreateSchema
    ) -> PatientResponseSchema:
        return await self.repository.create(patient)

    async def update_patient(
        self, patient_id: int, patient: PatientCreateSchema
    ) -> PatientResponseSchema:
        return await self.repository.update(patient_id, patient)

    async def get_patient(self, patient_id: int) -> PatientResponseSchema:
        return await self.repository.get_by_id(patient_id)

    async def list_patients(self) -> list[PatientResponseSchema]:
        return await self.repository.list()

    async def delete_patient(self, patient_id: int) -> bool:
        return await self.repository.delete(patient_id)
