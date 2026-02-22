from fastapi import APIRouter, Depends, HTTPException, status
from fhir.resources.patient import Patient
from app.services.patient_service import PatientService
from app.schemas.patient import PatientCreateSchema
from app.di.dependencies.patient import get_patient_service

router = APIRouter()


@router.post("/", response_model=Patient, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreateSchema,
    patient_service: PatientService = Depends(get_patient_service),
):
    data_dict = payload.model_dump(exclude_none=True)
    try:
        validated_fhir_resource = Patient.model_validate(data_dict)
        return await patient_service.create_patient(
            validated_fhir_resource.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=Patient)
async def get_patient(
    id: int, patient_service: PatientService = Depends(get_patient_service)
):
    patient = await patient_service.get_patient(id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/", response_model=list[Patient])
async def list_patients(
    patient_service: PatientService = Depends(get_patient_service),
):
    return await patient_service.list_patients()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    id: int, patient_service: PatientService = Depends(get_patient_service)
):
    deleted = await patient_service.delete_patient(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return None
