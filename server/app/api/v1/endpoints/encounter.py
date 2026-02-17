
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fhir.resources.encounter import Encounter
from app.core.database import get_db
from app.repository.encounter_repository import EncounterRepository
from app.services.encounter_service import EncounterService
from app.schemas.encounter import EncounterCreateSchema

router = APIRouter()

async def get_encounter_service(session: AsyncSession = Depends(get_db)) -> EncounterService:
    repository = EncounterRepository(session)
    return EncounterService(repository)

@router.post("/", response_model=Encounter, status_code=status.HTTP_201_CREATED)
async def create_encounter(
    payload: EncounterCreateSchema,
    service: EncounterService = Depends(get_encounter_service)
):
    data_dict = payload.model_dump(exclude_none=True, by_alias=True)
    try:
        validated_fhir_resource = Encounter.model_validate(data_dict)
        return await service.create_encounter(validated_fhir_resource.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=Encounter)
async def get_encounter(
    id: str,
    service: EncounterService = Depends(get_encounter_service)
):
    encounter = await service.get_encounter(id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter

@router.get("/", response_model=list[Encounter])
async def list_encounters(
    service: EncounterService = Depends(get_encounter_service)
):
    return await service.list_encounters()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_encounter(
    id: str,
    service: EncounterService = Depends(get_encounter_service)
):
    deleted = await service.delete_encounter(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return None
