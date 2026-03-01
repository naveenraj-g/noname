from fastapi import APIRouter, Depends, HTTPException, status, Path
from fhir.resources.encounter import Encounter
from app.services.encounter_service import EncounterService
from app.schemas.encounter import EncounterCreateSchema
from app.di.dependencies.encounter import get_encounter_service
from app.auth.dependencies import require_permission

router = APIRouter()


# ── Create Encounter ───────────────────────────────────────────────────


@router.post(
    "/",
    # dependencies=[Depends(require_permission("encounter", "create"))],
    status_code=status.HTTP_201_CREATED,
    operation_id="create_encounter",
    summary="Create a new FHIR Encounter resource",
    description="""
Create a new FHIR Encounter resource representing a clinical interaction. Requires `encounter:create` permission.

An Encounter documents a patient's visit to a healthcare facility — including clinic visits,
hospital admissions, emergency department visits, and telehealth sessions. The server
validates the payload against the FHIR Encounter schema before persisting.

Required fields: `status` (the encounter lifecycle state) and `class` (the care setting
classification such as "inpatient", "outpatient", or "emergency").

Recommended: Include a `subject` reference to the Patient (e.g., "Patient/123"),
at least one `participant` with a Practitioner reference, and a `period` with start/end times.

Returns the complete FHIR Encounter resource including the server-assigned `id`.
""",
    response_description="The newly created FHIR Encounter resource with auto-generated ID.",
    responses={
        201: {"description": "Encounter successfully created and persisted to the database."},
        400: {"description": "Invalid FHIR Encounter payload — failed FHIR schema validation."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
        422: {"description": "Validation error — the request body is malformed or missing required fields."},
    },
)
async def create_encounter(
    payload: EncounterCreateSchema,
    service: EncounterService = Depends(get_encounter_service),
):
    try:
        data_dict = payload.model_dump(exclude_none=True, by_alias=True)
        return await service.create_encounter(data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Get Encounter by ID ───────────────────────────────────────────────


@router.get(
    "/{id}",
    # dependencies=[Depends(require_permission("encounter", "read"))],
    operation_id="get_encounter_by_id",
    summary="Retrieve an Encounter resource by ID",
    description="""
Retrieve a single FHIR Encounter resource by its internal database ID. Requires `encounter:read` permission.

Returns the full Encounter resource including status, classification, subject reference,
participants, diagnoses, locations, reason codes, and time period. Returns 404 if no
encounter exists with the given ID.
""",
    response_description="The FHIR Encounter resource matching the given ID.",
    responses={
        200: {"description": "Encounter resource found and returned successfully."},
        404: {"description": "No Encounter resource exists with the specified ID."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
    },
)
async def get_encounter(
    id: int = Path(
        ...,
        title="Encounter ID",
        description="The internal database identifier of the Encounter resource. Must be a positive integer.",
        examples=[789],
        ge=1,
    ),
    service: EncounterService = Depends(get_encounter_service),
):
    encounter = await service.get_encounter(id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


# ── List All Encounters ────────────────────────────────────────────────


@router.get(
    "/",
    # dependencies=[Depends(require_permission("encounter", "read"))],
    operation_id="list_encounters",
    summary="List all Encounter resources",
    description="""
Retrieve a list of all FHIR Encounter resources stored in the system. Requires `encounter:read` permission.

Returns an array of complete Encounter resources. Each resource includes status,
classification, subject, participants, diagnoses, locations, and time period.

Returns an empty array if no encounters exist.
""",
    response_description="An array of all FHIR Encounter resources in the system.",
    responses={
        200: {"description": "Successfully retrieved the list of encounters."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
    },
)
async def list_encounters(
    service: EncounterService = Depends(get_encounter_service),
):
    return await service.list_encounters()


# ── Update Encounter ───────────────────────────────────────────────────


@router.put(
    "/{id}",
    # dependencies=[Depends(require_permission("encounter", "update"))],
    operation_id="update_encounter",
    summary="Update an existing Encounter resource (full replacement)",
    description="""
Update an existing FHIR Encounter resource by replacing it entirely with the provided payload. Requires `encounter:update` permission.

This implements FHIR-standard PUT semantics — the entire resource is replaced, not merged.
Any fields not included in the request body will be removed from the resource. To preserve
existing data, include all current fields in the request.

Required fields: `status` and `class`. The `id` path parameter identifies the encounter
to update. Returns 404 if no encounter exists with the given ID.
""",
    response_description="The updated FHIR Encounter resource after full replacement.",
    responses={
        200: {"description": "Encounter resource successfully updated."},
        400: {"description": "Invalid FHIR Encounter payload — failed FHIR schema validation."},
        404: {"description": "No Encounter resource exists with the specified ID."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
        422: {"description": "Validation error — the request body is malformed or missing required fields."},
    },
)
async def update_encounter(
    payload: EncounterCreateSchema,
    id: int = Path(
        ...,
        title="Encounter ID",
        description="The internal database identifier of the Encounter resource to update. Must be a positive integer.",
        examples=[789],
        ge=1,
    ),
    service: EncounterService = Depends(get_encounter_service),
):
    try:
        data_dict = payload.model_dump(exclude_none=True, by_alias=True)
        result = await service.update_encounter(id, data_dict)
        if not result:
            raise HTTPException(status_code=404, detail="Encounter not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Delete Encounter ───────────────────────────────────────────────────


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_permission("encounter", "delete"))],
    operation_id="delete_encounter",
    summary="Delete an Encounter resource by ID",
    description="""
Permanently delete a FHIR Encounter resource by its internal database ID. Requires `encounter:delete` permission.

This operation is irreversible. All associated data (types, participants, diagnoses,
locations, reason codes) will also be deleted via cascade. Returns 404 if no encounter
exists with the given ID.

Returns no content on successful deletion (HTTP 204).
""",
    response_description="Encounter resource successfully deleted. No content returned.",
    responses={
        204: {"description": "Encounter resource successfully deleted."},
        404: {"description": "No Encounter resource exists with the specified ID."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
    },
)
async def delete_encounter(
    id: int = Path(
        ...,
        title="Encounter ID",
        description="The internal database identifier of the Encounter resource to delete. Must be a positive integer.",
        examples=[789],
        ge=1,
    ),
    service: EncounterService = Depends(get_encounter_service),
):
    deleted = await service.delete_encounter(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return None
