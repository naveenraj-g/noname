from fastapi import APIRouter, Depends, HTTPException, status, Request
from fhir.resources.patient import Patient
from app.services.patient_service import PatientService
from app.schemas.patient import PatientCreateSchema
from app.di.dependencies.patient import get_patient_service
from app.auth.dependencies import require_permission

router = APIRouter()


@router.post(
    "/",
    response_model=Patient,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_patient",
    description="Create a new FHIR Patient resource and return the created resource.",
)
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


@router.get(
    "/{id}",
    response_model=Patient,
    operation_id="get_patient_by_id",
    description="Retrieve a Patient resource by its internal database ID.",
)
async def get_patient(
    id: int, patient_service: PatientService = Depends(get_patient_service)
):
    patient = await patient_service.get_patient(id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get(
    "/",
    response_model=list[Patient],
    dependencies=[Depends(require_permission("patient", "read"))],
    operation_id="list_patients",
    description="Retrieve a list of all Patient resources. Requires patient:read permission.",
    tags=["patient", "read"],
)
async def list_patients(
    request: Request,
    patient_service: PatientService = Depends(get_patient_service),
):
    user = request.state.user
    # print(user)
    return await patient_service.list_patients()


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_patient",
    description="Delete a Patient resource by its internal database ID.",
)
async def delete_patient(
    id: int, patient_service: PatientService = Depends(get_patient_service)
):
    deleted = await patient_service.delete_patient(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return None
