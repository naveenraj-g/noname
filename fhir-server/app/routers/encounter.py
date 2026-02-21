from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fhir.resources.encounter import Encounter
from app.core.database import get_fhir_db
from app.repository.encounter_repository import EncounterRepository
from app.services.encounter_service import EncounterService
from typing import Dict, Any
from app.auth.dependencies import get_current_user

router = APIRouter()


async def get_encounter_service(
    session: AsyncSession = Depends(get_fhir_db),
) -> EncounterService:
    repository = EncounterRepository(session)
    return EncounterService(repository)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_encounter(
    payload: Dict[str, Any],  # Accept any dict to avoid schema validation issues
    service: EncounterService = Depends(get_encounter_service),
):
    try:
        return await service.create_encounter(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}")
async def get_encounter(
    id: int, service: EncounterService = Depends(get_encounter_service)
):
    encounter = await service.get_encounter(id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.get("/")
async def list_encounters(service: EncounterService = Depends(get_encounter_service)):
    return await service.list_encounters()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_encounter(
    id: int,
    service: EncounterService = Depends(get_encounter_service),
):
    deleted = await service.delete_encounter(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return None
