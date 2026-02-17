
import uuid
from fhir.resources.patient import Patient
from app.repository.patient_repository import PatientRepository

class PatientService:
    def __init__(self, repository: PatientRepository):
        self.repository = repository

    async def create_patient(self, patient_data: dict) -> Patient:
        # Generate ID if not present
        if "id" not in patient_data:
            patient_data["id"] = str(uuid.uuid4())
        
        patient = Patient.model_validate(patient_data)
        return await self.repository.create(patient)

    async def get_patient(self, patient_id: str) -> Patient:
        return await self.repository.get(patient_id)

    async def list_patients(self) -> list[Patient]:
        return await self.repository.list()

    async def delete_patient(self, patient_id: str) -> bool:
        return await self.repository.delete(patient_id)
