from fastapi import APIRouter, Depends, HTTPException, status, Path
from fhir.resources.questionnaireresponse import QuestionnaireResponse
from app.services.questionnaire_response_service import QuestionnaireResponseService
from app.schemas.questionnaire_response import QuestionnaireResponseCreateSchema
from app.di.dependencies.questionnaire_response import get_questionnaire_response_service

router = APIRouter()


# ── Create QuestionnaireResponse ──────────────────────────────────────────────


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    operation_id="create_questionnaire_response",
    summary="Create a new FHIR QuestionnaireResponse resource",
    description="""
Create a new FHIR QuestionnaireResponse resource representing a set of answers
to questions from a Questionnaire.

A QuestionnaireResponse records responses to individual questions, supports nested
group items, and multiple answer value types (boolean, string, coding, quantity, etc.).

Required fields: `questionnaire` (canonical URL) and `status`.

Returns the complete FHIR QuestionnaireResponse resource including the server-assigned `id`.
""",
    response_description="The newly created FHIR QuestionnaireResponse resource with auto-generated ID.",
    responses={
        201: {"description": "QuestionnaireResponse successfully created."},
        400: {"description": "Invalid FHIR QuestionnaireResponse payload."},
        401: {"description": "Authentication required."},
        422: {"description": "Validation error — malformed or missing required fields."},
    },
)
async def create_questionnaire_response(
    payload: QuestionnaireResponseCreateSchema,
    service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    try:
        data_dict = payload.model_dump(exclude_none=True, by_alias=True)
        return await service.create_questionnaire_response(data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Get QuestionnaireResponse by ID ──────────────────────────────────────────


@router.get(
    "/{id}",
    operation_id="get_questionnaire_response_by_id",
    summary="Retrieve a QuestionnaireResponse resource by ID",
    description="""
Retrieve a single FHIR QuestionnaireResponse resource by its internal database ID.

Returns the full resource including all items, nested groups, and answer values.
Returns 404 if no resource exists with the given ID.
""",
    response_description="The FHIR QuestionnaireResponse resource matching the given ID.",
    responses={
        200: {"description": "QuestionnaireResponse found and returned."},
        404: {"description": "No QuestionnaireResponse exists with the specified ID."},
        401: {"description": "Authentication required."},
    },
)
async def get_questionnaire_response(
    id: int = Path(
        ...,
        title="QuestionnaireResponse ID",
        description="The internal database identifier of the QuestionnaireResponse resource.",
        ge=1,
    ),
    service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    qr = await service.get_questionnaire_response(id)
    if not qr:
        raise HTTPException(status_code=404, detail="QuestionnaireResponse not found")
    return qr


# ── List All QuestionnaireResponses ───────────────────────────────────────────


@router.get(
    "/",
    operation_id="list_questionnaire_responses",
    summary="List all QuestionnaireResponse resources",
    description="""
Retrieve a list of all FHIR QuestionnaireResponse resources stored in the system.

Returns an array of complete QuestionnaireResponse resources. Returns an empty array if none exist.
""",
    response_description="An array of all FHIR QuestionnaireResponse resources.",
    responses={
        200: {"description": "Successfully retrieved the list of questionnaire responses."},
        401: {"description": "Authentication required."},
    },
)
async def list_questionnaire_responses(
    service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    return await service.list_questionnaire_responses()


# ── Update QuestionnaireResponse ──────────────────────────────────────────────


@router.put(
    "/{id}",
    operation_id="update_questionnaire_response",
    summary="Update an existing QuestionnaireResponse resource (full replacement)",
    description="""
Update an existing FHIR QuestionnaireResponse resource by replacing it entirely with the provided payload.

Implements FHIR-standard PUT semantics — the entire resource is replaced.
All existing items and answers are removed and replaced with the new payload.

Returns 404 if no resource exists with the given ID.
""",
    response_description="The updated FHIR QuestionnaireResponse resource.",
    responses={
        200: {"description": "QuestionnaireResponse successfully updated."},
        400: {"description": "Invalid FHIR QuestionnaireResponse payload."},
        404: {"description": "No QuestionnaireResponse exists with the specified ID."},
        401: {"description": "Authentication required."},
        422: {"description": "Validation error."},
    },
)
async def update_questionnaire_response(
    payload: QuestionnaireResponseCreateSchema,
    id: int = Path(
        ...,
        title="QuestionnaireResponse ID",
        description="The internal database identifier of the QuestionnaireResponse resource to update.",
        ge=1,
    ),
    service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    try:
        data_dict = payload.model_dump(exclude_none=True, by_alias=True)
        result = await service.update_questionnaire_response(id, data_dict)
        if not result:
            raise HTTPException(status_code=404, detail="QuestionnaireResponse not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Delete QuestionnaireResponse ──────────────────────────────────────────────


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_questionnaire_response",
    summary="Delete a QuestionnaireResponse resource by ID",
    description="""
Permanently delete a FHIR QuestionnaireResponse resource by its internal database ID.

This operation is irreversible. All associated items and answers are deleted via cascade.
Returns 404 if no resource exists with the given ID.

Returns no content on successful deletion (HTTP 204).
""",
    response_description="QuestionnaireResponse successfully deleted. No content returned.",
    responses={
        204: {"description": "QuestionnaireResponse successfully deleted."},
        404: {"description": "No QuestionnaireResponse exists with the specified ID."},
        401: {"description": "Authentication required."},
    },
)
async def delete_questionnaire_response(
    id: int = Path(
        ...,
        title="QuestionnaireResponse ID",
        description="The internal database identifier of the QuestionnaireResponse resource to delete.",
        ge=1,
    ),
    service: QuestionnaireResponseService = Depends(get_questionnaire_response_service),
):
    deleted = await service.delete_questionnaire_response(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="QuestionnaireResponse not found")
    return None
