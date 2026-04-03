from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import require_permission
from app.auth.patient_deps import get_authorized_patient
from app.core.content_negotiation import format_response, format_list_response
from app.di.dependencies.patient import get_patient_service
from app.models.patient import PatientModel
from app.schemas.resources import (
    PatientCreateSchema,
    PatientPatchSchema,
    PatientResponseSchema,
    IdentifierCreate,
    TelecomCreate,
    AddressCreate,
)
from app.services.patient_service import PatientService

router = APIRouter()


# ── Create Patient ─────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=PatientResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("patient", "create"))],
    operation_id="create_patient",
    summary="Create a new Patient resource",
)
async def create_patient(
    payload: PatientCreateSchema,
    request: Request,
    patient_service: PatientService = Depends(get_patient_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    patient = await patient_service.create_patient(payload, user_id, org_id)
    return format_response(
        patient_service._to_fhir(patient),
        patient_service._to_plain(patient),
        request,
    )


# ── Get own Patient profile (/me) ──────────────────────────────────────────
# Declared before /{patient_id} so "me" is not matched by the int path param.


@router.get(
    "/me",
    response_model=PatientResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("patient", "read"))],
    operation_id="get_my_patient_profile",
    summary="Get the Patient profile for the currently authenticated user",
)
async def get_my_patient_profile(
    request: Request,
    patient_service: PatientService = Depends(get_patient_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    patient = await patient_service.get_me(user_id, org_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return format_response(
        patient_service._to_fhir(patient),
        patient_service._to_plain(patient),
        request,
    )


# ── Get Patient by public patient_id ──────────────────────────────────────


@router.get(
    "/{patient_id}",
    response_model=PatientResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("patient", "read"))],
    operation_id="get_patient_by_id",
    summary="Retrieve a Patient resource by public patient_id",
)
async def get_patient(
    request: Request,
    patient: PatientModel = Depends(get_authorized_patient),
    patient_service: PatientService = Depends(get_patient_service),
):
    return format_response(
        patient_service._to_fhir(patient),
        patient_service._to_plain(patient),
        request,
    )


# ── Patch Patient ──────────────────────────────────────────────────────────


@router.patch(
    "/{patient_id}",
    response_model=PatientResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("patient", "update"))],
    operation_id="patch_patient",
    summary="Partially update a Patient resource",
    description="Only supplied fields are written. Omitted fields are unchanged.",
)
async def patch_patient(
    payload: PatientPatchSchema,
    request: Request,
    patient: PatientModel = Depends(get_authorized_patient),
    patient_service: PatientService = Depends(get_patient_service),
):
    updated = await patient_service.patch_patient(patient.patient_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return format_response(
        patient_service._to_fhir(updated),
        patient_service._to_plain(updated),
        request,
    )


# ── List Patients ──────────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=list[PatientResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("patient", "read"))],
    operation_id="list_patients",
    summary="List all Patient resources",
)
async def list_patients(
    request: Request,
    patient_service: PatientService = Depends(get_patient_service),
):
    patients = await patient_service.list_patients()
    return format_list_response(
        [patient_service._to_fhir(p) for p in patients],
        [patient_service._to_plain(p) for p in patients],
        request,
    )


# ── Delete Patient ─────────────────────────────────────────────────────────


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("patient", "delete"))],
    operation_id="delete_patient",
    summary="Delete a Patient resource",
)
async def delete_patient(
    patient: PatientModel = Depends(get_authorized_patient),
    patient_service: PatientService = Depends(get_patient_service),
):
    await patient_service.delete_patient(patient.patient_id)
    return None


# ── Sub-resource: Identifiers ──────────────────────────────────────────────


@router.post(
    "/{patient_id}/identifiers",
    response_model=PatientResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("patient", "update"))],
    operation_id="add_patient_identifier",
    summary="Add an identifier to a Patient",
)
async def add_identifier(
    payload: IdentifierCreate,
    request: Request,
    patient: PatientModel = Depends(get_authorized_patient),
    patient_service: PatientService = Depends(get_patient_service),
):
    updated = await patient_service.add_identifier(patient.patient_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return format_response(
        patient_service._to_fhir(updated),
        patient_service._to_plain(updated),
        request,
    )


# ── Sub-resource: Telecom ──────────────────────────────────────────────────


@router.post(
    "/{patient_id}/telecom",
    response_model=PatientResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("patient", "update"))],
    operation_id="add_patient_telecom",
    summary="Add a contact point (telecom) to a Patient",
)
async def add_telecom(
    payload: TelecomCreate,
    request: Request,
    patient: PatientModel = Depends(get_authorized_patient),
    patient_service: PatientService = Depends(get_patient_service),
):
    updated = await patient_service.add_telecom(patient.patient_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return format_response(
        patient_service._to_fhir(updated),
        patient_service._to_plain(updated),
        request,
    )


# ── Sub-resource: Addresses ────────────────────────────────────────────────


@router.post(
    "/{patient_id}/addresses",
    response_model=PatientResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("patient", "update"))],
    operation_id="add_patient_address",
    summary="Add an address to a Patient",
)
async def add_address(
    payload: AddressCreate,
    request: Request,
    patient: PatientModel = Depends(get_authorized_patient),
    patient_service: PatientService = Depends(get_patient_service),
):
    updated = await patient_service.add_address(patient.patient_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return format_response(
        patient_service._to_fhir(updated),
        patient_service._to_plain(updated),
        request,
    )
