from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import require_permission
from app.auth.appointment_deps import get_authorized_appointment
from app.core.content_negotiation import format_response, format_list_response
from app.di.dependencies.appointment import get_appointment_service
from app.models.appointment import AppointmentModel
from app.schemas.appointment import (
    AppointmentCreateSchema,
    AppointmentPatchSchema,
    AppointmentResponseSchema,
)
from app.services.appointment_service import AppointmentService

router = APIRouter()


# ── Create Appointment ─────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=AppointmentResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("appointment", "create"))],
    operation_id="create_appointment",
    summary="Create a new Appointment resource",
    description="Books an Appointment for a patient and/or practitioner(s). At least one participant is required. References use public IDs (e.g. Patient/10001, Practitioner/30001).",
)
async def create_appointment(
    payload: AppointmentCreateSchema,
    request: Request,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    appointment = await appointment_service.create_appointment(payload, user_id, org_id)
    return format_response(
        appointment_service._to_fhir(appointment),
        appointment_service._to_plain(appointment),
        request,
    )


# ── Get own Appointments (/me) ─────────────────────────────────────────────
# Declared before /{appointment_id} to avoid routing conflicts.


@router.get(
    "/me",
    response_model=list[AppointmentResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("appointment", "read"))],
    operation_id="get_my_appointments",
    summary="List all Appointment resources for the currently authenticated user",
)
async def get_my_appointments(
    request: Request,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    appointments = await appointment_service.get_me(user_id, org_id)
    return format_list_response(
        [appointment_service._to_fhir(a) for a in appointments],
        [appointment_service._to_plain(a) for a in appointments],
        request,
    )


# ── Get Appointment by public appointment_id ───────────────────────────────


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("appointment", "read"))],
    operation_id="get_appointment_by_id",
    summary="Retrieve an Appointment resource by public appointment_id",
)
async def get_appointment(
    request: Request,
    appointment: AppointmentModel = Depends(get_authorized_appointment),
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    return format_response(
        appointment_service._to_fhir(appointment),
        appointment_service._to_plain(appointment),
        request,
    )


# ── Patch Appointment ──────────────────────────────────────────────────────


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("appointment", "update"))],
    operation_id="patch_appointment",
    summary="Partially update an Appointment resource",
    description="Patchable fields: status, start, end, minutes_duration, description, comment, patient_instruction, priority_value. Participants and service fields cannot be changed after creation.",
)
async def patch_appointment(
    payload: AppointmentPatchSchema,
    request: Request,
    appointment: AppointmentModel = Depends(get_authorized_appointment),
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    updated = await appointment_service.patch_appointment(appointment.appointment_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return format_response(
        appointment_service._to_fhir(updated),
        appointment_service._to_plain(updated),
        request,
    )


# ── List Appointments ──────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=list[AppointmentResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("appointment", "read"))],
    operation_id="list_appointments",
    summary="List all Appointment resources",
    description="Returns all appointments. Filter by patient using `?patient_id={patient_id}` (public patient_id).",
)
async def list_appointments(
    request: Request,
    patient_id: Optional[int] = None,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    appointments = await appointment_service.list_appointments(patient_id=patient_id)
    return format_list_response(
        [appointment_service._to_fhir(a) for a in appointments],
        [appointment_service._to_plain(a) for a in appointments],
        request,
    )


# ── Delete Appointment ─────────────────────────────────────────────────────


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("appointment", "delete"))],
    operation_id="delete_appointment",
    summary="Delete an Appointment resource",
)
async def delete_appointment(
    appointment: AppointmentModel = Depends(get_authorized_appointment),
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    await appointment_service.delete_appointment(appointment.appointment_id)
    return None
