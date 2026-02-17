
import uuid
from fhir.resources.practitioner import Practitioner
from app.repository.practitioner_repository import PractitionerRepository

class PractitionerService:
    def __init__(self, repository: PractitionerRepository):
        self.repository = repository

    async def create_practitioner(self, practitioner_data: dict) -> Practitioner:
        # Generate ID if not present
        if "id" not in practitioner_data:
            practitioner_data["id"] = str(uuid.uuid4())
        
        practitioner = Practitioner.model_validate(practitioner_data)
        return await self.repository.create(practitioner)

    async def get_practitioner(self, practitioner_id: str) -> Practitioner:
        return await self.repository.get(practitioner_id)

    async def list_practitioners(self) -> list[Practitioner]:
        return await self.repository.list()

    async def delete_practitioner(self, practitioner_id: str) -> bool:
        return await self.repository.delete(practitioner_id)
