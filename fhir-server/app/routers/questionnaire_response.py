from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import require_permission
from app.auth.questionnaire_response_deps import get_authorized_questionnaire_response
from app.core.content_negotiation import format_response, format_list_response
from app.di.dependencies.questionnaire_response import get_questionnaire_response_service
from app.models.questionnaire_response import QuestionnaireResponseModel
from app.schemas.questionnaire_response import (
    QuestionnaireResponseCreateSchema,
    QuestionnaireResponsePatchSchema,
    QuestionnaireResponseResponseSchema,
)
from app.services.questionnaire_response_service import QuestionnaireResponseService

router = APIRouter()


# ── Create QuestionnaireResponse ───────────────────────────────────────────


@router.post(
    "/",
    response_model=QuestionnaireResponseResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("questionnaire_response", "create"))],
    operation_id="create_questionnaire_response",
    summary="Create a new QuestionnaireResponse resource",
    description="Records answers to a Questionnaire. Supports nested items, groups, and all FHIR R4 answer value types. References use public IDs (Patient/10001, Encounter/20001, Practitioner/30001).",
)
async def create_questionnaire_response(
    payload: QuestionnaireResponseCreateSchema,
    request: Request,
    qr_service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    qr = await qr_service.create_questionnaire_response(payload, user_id, org_id)
    return format_response(
        qr_service._to_fhir(qr),
        qr_service._to_plain(qr),
        request,
    )


# ── Get own QuestionnaireResponses (/me) ───────────────────────────────────
# Declared before /{questionnaire_response_id} to avoid routing conflicts.


@router.get(
    "/me",
    response_model=list[QuestionnaireResponseResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("questionnaire_response", "read"))],
    operation_id="get_my_questionnaire_responses",
    summary="List all QuestionnaireResponse resources for the currently authenticated user",
)
async def get_my_questionnaire_responses(
    request: Request,
    qr_service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    responses = await qr_service.get_me(user_id, org_id)
    return format_list_response(
        [qr_service._to_fhir(qr) for qr in responses],
        [qr_service._to_plain(qr) for qr in responses],
        request,
    )


# ── Get QuestionnaireResponse by public id ─────────────────────────────────


@router.get(
    "/{questionnaire_response_id}",
    response_model=QuestionnaireResponseResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("questionnaire_response", "read"))],
    operation_id="get_questionnaire_response_by_id",
    summary="Retrieve a QuestionnaireResponse resource by public questionnaire_response_id",
)
async def get_questionnaire_response(
    request: Request,
    qr: QuestionnaireResponseModel = Depends(get_authorized_questionnaire_response),
    qr_service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    return format_response(
        qr_service._to_fhir(qr),
        qr_service._to_plain(qr),
        request,
    )


# ── Patch QuestionnaireResponse ────────────────────────────────────────────


@router.patch(
    "/{questionnaire_response_id}",
    response_model=QuestionnaireResponseResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("questionnaire_response", "update"))],
    operation_id="patch_questionnaire_response",
    summary="Partially update a QuestionnaireResponse resource",
    description="Only lifecycle fields are patchable: status, authored. To replace items/answers, re-create the resource.",
)
async def patch_questionnaire_response(
    payload: QuestionnaireResponsePatchSchema,
    request: Request,
    qr: QuestionnaireResponseModel = Depends(get_authorized_questionnaire_response),
    qr_service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    updated = await qr_service.patch_questionnaire_response(
        qr.questionnaire_response_id, payload
    )
    if not updated:
        raise HTTPException(status_code=404, detail="QuestionnaireResponse not found")
    return format_response(
        qr_service._to_fhir(updated),
        qr_service._to_plain(updated),
        request,
    )


# ── List QuestionnaireResponses ────────────────────────────────────────────


@router.get(
    "/",
    response_model=list[QuestionnaireResponseResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("questionnaire_response", "read"))],
    operation_id="list_questionnaire_responses",
    summary="List all QuestionnaireResponse resources",
    description="Returns all questionnaire responses. Filter by patient using `?patient_id={patient_id}` (public patient_id).",
)
async def list_questionnaire_responses(
    request: Request,
    patient_id: Optional[int] = None,
    qr_service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    responses = await qr_service.list_questionnaire_responses(patient_id=patient_id)
    return format_list_response(
        [qr_service._to_fhir(qr) for qr in responses],
        [qr_service._to_plain(qr) for qr in responses],
        request,
    )


# ── Delete QuestionnaireResponse ───────────────────────────────────────────


@router.delete(
    "/{questionnaire_response_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("questionnaire_response", "delete"))],
    operation_id="delete_questionnaire_response",
    summary="Delete a QuestionnaireResponse resource",
)
async def delete_questionnaire_response(
    qr: QuestionnaireResponseModel = Depends(get_authorized_questionnaire_response),
    qr_service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    await qr_service.delete_questionnaire_response(qr.questionnaire_response_id)
    return None
