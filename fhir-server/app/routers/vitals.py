from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.auth.dependencies import require_permission
from app.auth.vitals_deps import get_authorized_vitals
from app.di.dependencies.vitals import get_vitals_service
from app.models.vitals.vitals import VitalsModel
from app.schemas.vitals import (
    VitalsCreateSchema,
    VitalsPatchSchema,
    VitalsResponseSchema,
)
from app.services.vitals_service import VitalsService

router = APIRouter()


def _serialize(vitals: VitalsModel) -> dict:
    return VitalsResponseSchema(
        id=vitals.vitals_id,
        pseudo_id=vitals.pseudo_id,
        pseudo_id2=vitals.pseudo_id2,
        user_id=vitals.user_id,
        patient_id=vitals.patient_id,
        org_id=vitals.org_id,
        summary=vitals.summary,
        date=vitals.date,
        datetime=vitals.datetime,
        activity_name=vitals.activity_name,
        duration_minutes=vitals.duration_minutes,
        start_time=vitals.start_time,
        end_time=vitals.end_time,
        avg_hr_bpm=vitals.avg_hr_bpm,
        max_hr_bpm=vitals.max_hr_bpm,
        elevation_gain_m=vitals.elevation_gain_m,
        distance_meters=vitals.distance_meters,
        calories_kcal=vitals.calories_kcal,
        steps=vitals.steps,
        speed_mps=vitals.speed_mps,
        active_zone_minutes=vitals.active_zone_minutes,
        fatburn_active_zone_minutes=vitals.fatburn_active_zone_minutes,
        cardio_active_zone_minutes=vitals.cardio_active_zone_minutes,
        peak_active_zone_minutes=vitals.peak_active_zone_minutes,
        age=vitals.age,
        gender=vitals.gender,
        weight_kg=vitals.weight_kg,
        height_cm=vitals.height_cm,
        resting_heart_rate=vitals.resting_heart_rate,
        heart_rate_variability=vitals.heart_rate_variability,
        stress_management_score=vitals.stress_management_score,
        sleep_minutes=vitals.sleep_minutes,
        rem_sleep_minutes=vitals.rem_sleep_minutes,
        deep_sleep_minutes=vitals.deep_sleep_minutes,
        awake_minutes=vitals.awake_minutes,
        light_sleep_minutes=vitals.light_sleep_minutes,
        bed_time=vitals.bed_time,
        wake_up_time=vitals.wake_up_time,
        deep_sleep_percent=vitals.deep_sleep_percent,
        rem_sleep_percent=vitals.rem_sleep_percent,
        awake_percent=vitals.awake_percent,
        light_sleep_percent=vitals.light_sleep_percent,
        created_at=vitals.created_at,
        updated_at=vitals.updated_at,
    ).model_dump(exclude_none=True)


@router.post(
    "/",
    response_model=VitalsResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_vitals",
    summary="Record a new vitals entry",
)
async def create_vitals(
    payload: VitalsCreateSchema,
    request: Request,
    vitals_service: VitalsService = Depends(get_vitals_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    vitals = await vitals_service.create_vitals(payload, user_id, org_id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(_serialize(vitals)),
    )


@router.get(
    "/me",
    response_model=list[VitalsResponseSchema],
    response_model_exclude_none=True,
    operation_id="get_my_vitals",
    summary="List all vitals entries for the currently authenticated user",
)
async def get_my_vitals(
    request: Request,
    vitals_service: VitalsService = Depends(get_vitals_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    records = await vitals_service.get_me(user_id, org_id)
    return JSONResponse(content=jsonable_encoder([_serialize(v) for v in records]))


@router.get(
    "/{vitals_id}",
    response_model=VitalsResponseSchema,
    response_model_exclude_none=True,
    operation_id="get_vitals_by_id",
    summary="Retrieve a vitals entry by public vitals_id",
)
async def get_vitals(
    request: Request,
    vitals: VitalsModel = Depends(get_authorized_vitals),
    vitals_service: VitalsService = Depends(get_vitals_service),
):
    return JSONResponse(content=jsonable_encoder(_serialize(vitals)))


@router.patch(
    "/{vitals_id}",
    response_model=VitalsResponseSchema,
    response_model_exclude_none=True,
    operation_id="patch_vitals",
    summary="Partially update a vitals entry",
)
async def patch_vitals(
    payload: VitalsPatchSchema,
    request: Request,
    vitals: VitalsModel = Depends(get_authorized_vitals),
    vitals_service: VitalsService = Depends(get_vitals_service),
):
    updated = await vitals_service.patch_vitals(vitals.vitals_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Vitals not found")
    return JSONResponse(content=jsonable_encoder(_serialize(updated)))


@router.get(
    "/",
    response_model=list[VitalsResponseSchema],
    response_model_exclude_none=True,
    operation_id="list_vitals",
    summary="List vitals entries with optional filters",
    description="Filter by `?user_id=`, `?patient_id=`, or `?org_id=`.",
)
async def list_vitals(
    request: Request,
    user_id: Optional[str] = None,
    patient_id: Optional[int] = None,
    org_id: Optional[str] = None,
    vitals_service: VitalsService = Depends(get_vitals_service),
):
    records = await vitals_service.list_vitals(
        user_id=user_id, patient_id=patient_id, org_id=org_id
    )
    return JSONResponse(content=jsonable_encoder([_serialize(v) for v in records]))


@router.delete(
    "/{vitals_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_vitals",
    summary="Delete a vitals entry",
)
async def delete_vitals(
    vitals: VitalsModel = Depends(get_authorized_vitals),
    vitals_service: VitalsService = Depends(get_vitals_service),
):
    await vitals_service.delete_vitals(vitals.vitals_id)
    return None
