from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import require_permission
from app.auth.encounter_deps import get_authorized_encounter
from app.core.content_negotiation import format_response, format_list_response
from app.di.dependencies.encounter import get_encounter_service
from app.models.encounter import EncounterModel
from app.schemas.encounter import (
    EncounterCreateSchema,
    EncounterPatchSchema,
    EncounterResponseSchema,
)
from app.services.encounter_service import EncounterService

router = APIRouter()


# ── Create Encounter ───────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=EncounterResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("encounter", "create"))],
    operation_id="create_encounter",
    summary="Create a new Encounter resource",
    description="Creates an Encounter event. All sub-resources (types, participants, reason codes, diagnoses, locations) are submitted as part of the single document.",
)
async def create_encounter(
    payload: EncounterCreateSchema,
    request: Request,
    encounter_service: EncounterService = Depends(get_encounter_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    encounter = await encounter_service.create_encounter(payload, user_id, org_id)
    return format_response(
        encounter_service._to_fhir(encounter),
        encounter_service._to_plain(encounter),
        request,
    )


# ── Get own Encounters (/me) ───────────────────────────────────────────────
# Declared before /{encounter_id} to avoid routing conflicts.


@router.get(
    "/me",
    response_model=list[EncounterResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("encounter", "read"))],
    operation_id="get_my_encounters",
    summary="List all Encounter resources for the currently authenticated user",
)
async def get_my_encounters(
    request: Request,
    encounter_service: EncounterService = Depends(get_encounter_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    encounters = await encounter_service.get_me(user_id, org_id)
    return format_list_response(
        [encounter_service._to_fhir(e) for e in encounters],
        [encounter_service._to_plain(e) for e in encounters],
        request,
    )


# ── Get Encounter by public encounter_id ──────────────────────────────────


@router.get(
    "/{encounter_id}",
    response_model=EncounterResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("encounter", "read"))],
    operation_id="get_encounter_by_id",
    summary="Retrieve an Encounter resource by public encounter_id",
)
async def get_encounter(
    request: Request,
    encounter: EncounterModel = Depends(get_authorized_encounter),
    encounter_service: EncounterService = Depends(get_encounter_service),
):
    return format_response(
        encounter_service._to_fhir(encounter),
        encounter_service._to_plain(encounter),
        request,
    )


# ── Patch Encounter ────────────────────────────────────────────────────────


@router.patch(
    "/{encounter_id}",
    response_model=EncounterResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("encounter", "update"))],
    operation_id="patch_encounter",
    summary="Partially update an Encounter resource",
    description="Only lifecycle fields are patchable: status, period_end, priority. Structural data cannot be changed after creation.",
)
async def patch_encounter(
    payload: EncounterPatchSchema,
    request: Request,
    encounter: EncounterModel = Depends(get_authorized_encounter),
    encounter_service: EncounterService = Depends(get_encounter_service),
):
    updated = await encounter_service.patch_encounter(encounter.encounter_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return format_response(
        encounter_service._to_fhir(updated),
        encounter_service._to_plain(updated),
        request,
    )


# ── List Encounters ────────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=list[EncounterResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("encounter", "read"))],
    operation_id="list_encounters",
    summary="List all Encounter resources",
    description="Returns all encounters. Filter by subject patient using `?patient_id={patient_id}` (public patient_id).",
)
async def list_encounters(
    request: Request,
    patient_id: Optional[int] = None,
    encounter_service: EncounterService = Depends(get_encounter_service),
):
    encounters = await encounter_service.list_encounters(patient_id=patient_id)
    return format_list_response(
        [encounter_service._to_fhir(e) for e in encounters],
        [encounter_service._to_plain(e) for e in encounters],
        request,
    )


# ── Delete Encounter ───────────────────────────────────────────────────────


@router.delete(
    "/{encounter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("encounter", "delete"))],
    operation_id="delete_encounter",
    summary="Delete an Encounter resource",
)
async def delete_encounter(
    encounter: EncounterModel = Depends(get_authorized_encounter),
    encounter_service: EncounterService = Depends(get_encounter_service),
):
    await encounter_service.delete_encounter(encounter.encounter_id)
    return None
