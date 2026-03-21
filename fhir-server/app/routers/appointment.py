from fastapi import APIRouter, Depends, HTTPException, status, Path
from fhir.resources.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentCreateSchema
from app.di.dependencies.appointment import get_appointment_service

router = APIRouter()


# ── Create Appointment ─────────────────────────────────────────────────


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    operation_id="create_appointment",
    summary="Create a new FHIR Appointment resource",
    description="""
Create a new FHIR Appointment resource representing a scheduled healthcare event.

An Appointment is a booking for a patient and/or practitioner(s) at a specific date and time.
It can represent clinic visits, follow-ups, procedures, telehealth sessions, and more.

Required fields: `status` and `participant` (at least one entry with a `status`).

Recommended: Include `subject` (Patient reference), `start`/`end` times, `serviceType`, and
at least one practitioner participant.

Returns the complete FHIR Appointment resource including the server-assigned `id`.
""",
    response_description="The newly created FHIR Appointment resource with auto-generated ID.",
    responses={
        201: {"description": "Appointment successfully created."},
        400: {"description": "Invalid FHIR Appointment payload."},
        401: {"description": "Authentication required."},
        422: {"description": "Validation error — malformed or missing required fields."},
    },
)
async def create_appointment(
    payload: AppointmentCreateSchema,
    service: AppointmentService = Depends(get_appointment_service),
):
    try:
        data_dict = payload.model_dump(exclude_none=True, by_alias=True)
        return await service.create_appointment(data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Get Appointment by ID ─────────────────────────────────────────────


@router.get(
    "/{id}",
    operation_id="get_appointment_by_id",
    summary="Retrieve an Appointment resource by ID",
    description="""
Retrieve a single FHIR Appointment resource by its internal database ID.

Returns the full Appointment resource including status, schedule, participants, service details,
and reason codes. Returns 404 if no appointment exists with the given ID.
""",
    response_description="The FHIR Appointment resource matching the given ID.",
    responses={
        200: {"description": "Appointment found and returned."},
        404: {"description": "No Appointment exists with the specified ID."},
        401: {"description": "Authentication required."},
    },
)
async def get_appointment(
    id: int = Path(
        ...,
        title="Appointment ID",
        description="The internal database identifier of the Appointment resource.",
        ge=1,
    ),
    service: AppointmentService = Depends(get_appointment_service),
):
    appointment = await service.get_appointment(id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


# ── List All Appointments ─────────────────────────────────────────────


@router.get(
    "/",
    operation_id="list_appointments",
    summary="List all Appointment resources",
    description="""
Retrieve a list of all FHIR Appointment resources stored in the system.

Returns an array of complete Appointment resources. Returns an empty array if none exist.
""",
    response_description="An array of all FHIR Appointment resources.",
    responses={
        200: {"description": "Successfully retrieved the list of appointments."},
        401: {"description": "Authentication required."},
    },
)
async def list_appointments(
    service: AppointmentService = Depends(get_appointment_service),
):
    return await service.list_appointments()


# ── Update Appointment ────────────────────────────────────────────────


@router.put(
    "/{id}",
    operation_id="update_appointment",
    summary="Update an existing Appointment resource (full replacement)",
    description="""
Update an existing FHIR Appointment resource by replacing it entirely with the provided payload.

Implements FHIR-standard PUT semantics — the entire resource is replaced. Any fields not
included will be removed. Required fields: `status` and `participant`.

Returns 404 if no appointment exists with the given ID.
""",
    response_description="The updated FHIR Appointment resource.",
    responses={
        200: {"description": "Appointment successfully updated."},
        400: {"description": "Invalid FHIR Appointment payload."},
        404: {"description": "No Appointment exists with the specified ID."},
        401: {"description": "Authentication required."},
        422: {"description": "Validation error."},
    },
)
async def update_appointment(
    payload: AppointmentCreateSchema,
    id: int = Path(
        ...,
        title="Appointment ID",
        description="The internal database identifier of the Appointment resource to update.",
        ge=1,
    ),
    service: AppointmentService = Depends(get_appointment_service),
):
    try:
        data_dict = payload.model_dump(exclude_none=True, by_alias=True)
        result = await service.update_appointment(id, data_dict)
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Delete Appointment ────────────────────────────────────────────────


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_appointment",
    summary="Delete an Appointment resource by ID",
    description="""
Permanently delete a FHIR Appointment resource by its internal database ID.

This operation is irreversible. All associated participants and reason codes are also
deleted via cascade. Returns 404 if no appointment exists with the given ID.

Returns no content on successful deletion (HTTP 204).
""",
    response_description="Appointment successfully deleted. No content returned.",
    responses={
        204: {"description": "Appointment successfully deleted."},
        404: {"description": "No Appointment exists with the specified ID."},
        401: {"description": "Authentication required."},
    },
)
async def delete_appointment(
    id: int = Path(
        ...,
        title="Appointment ID",
        description="The internal database identifier of the Appointment resource to delete.",
        ge=1,
    ),
    service: AppointmentService = Depends(get_appointment_service),
):
    deleted = await service.delete_appointment(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return None
