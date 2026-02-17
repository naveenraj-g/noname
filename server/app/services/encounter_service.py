
import uuid
from fhir.resources.encounter import Encounter
from app.repository.encounter_repository import EncounterRepository

class EncounterService:
    def __init__(self, repository: EncounterRepository):
        self.repository = repository

    async def create_encounter(self, encounter_data: dict) -> Encounter:
        # Generate ID if not present
        if "id" not in encounter_data:
            encounter_data["id"] = str(uuid.uuid4())
        
        encounter = Encounter.model_validate(encounter_data)
        return await self.repository.create(encounter)

    async def get_encounter(self, encounter_id: str) -> Encounter:
        return await self.repository.get(encounter_id)

    async def list_encounters(self) -> list[Encounter]:
        return await self.repository.list()

    async def delete_encounter(self, encounter_id: str) -> bool:
        return await self.repository.delete(encounter_id)
