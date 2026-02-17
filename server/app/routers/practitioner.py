from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fhir.resources.practitioner import Practitioner
from app.core.database import get_fhir_db
from app.repository.practitioner_repository import PractitionerRepository
from app.services.practitioner_service import PractitionerService
from app.schemas.practitioner import PractitionerCreateSchema

router = APIRouter()


async def get_practitioner_service(
    session: AsyncSession = Depends(get_fhir_db),
) -> PractitionerService:
    repository = PractitionerRepository(session)
    return PractitionerService(repository)


@router.post("/", response_model=Practitioner, status_code=status.HTTP_201_CREATED)
async def create_practitioner(
    payload: PractitionerCreateSchema,
    service: PractitionerService = Depends(get_practitioner_service),
):
    data_dict = payload.model_dump(exclude_none=True)
    try:
        validated_fhir_resource = Practitioner.model_validate(data_dict)
        return await service.create_practitioner(validated_fhir_resource.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=Practitioner)
async def get_practitioner(
    id: int, service: PractitionerService = Depends(get_practitioner_service)
):
    practitioner = await service.get_practitioner(id)
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return practitioner


@router.get("/", response_model=list[Practitioner])
async def list_practitioners(
    service: PractitionerService = Depends(get_practitioner_service),
):
    return await service.list_practitioners()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_practitioner(
    id: int, service: PractitionerService = Depends(get_practitioner_service)
):
    deleted = await service.delete_practitioner(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return None
