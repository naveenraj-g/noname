from fastapi import APIRouter, Depends, HTTPException, status, Path
from fhir.resources.practitioner import Practitioner
from app.services.practitioner_service import PractitionerService
from app.schemas.practitioner import PractitionerCreateSchema
from app.di.dependencies.practitioner import get_practitioner_service
from app.auth.dependencies import require_permission

router = APIRouter()


# ── Create Practitioner ────────────────────────────────────────────────


@router.post(
    "/",
    response_model=Practitioner,
    dependencies=[Depends(require_permission("practitioner", "create"))],
    status_code=status.HTTP_201_CREATED,
    operation_id="create_practitioner",
    summary="Create a new FHIR Practitioner resource",
    description="""
Create a new FHIR Practitioner resource in the system. Requires `practitioner:create` permission.

This endpoint accepts a structured Practitioner payload conforming to the HL7 FHIR R4
specification, validates it against the FHIR Practitioner schema, and persists it to the
database. The server auto-generates a unique internal ID for the resource.

A Practitioner represents a person who is directly or indirectly involved in the
provisioning of healthcare — including physicians, nurses, pharmacists, and administrative staff.

Recommended fields include at least one `name` with professional prefix (e.g., "Dr."),
`gender`, `telecom` (work phone/email), and `qualification` entries.

Returns the complete FHIR Practitioner resource including the server-assigned `id`.
""",
    response_description="The newly created FHIR Practitioner resource with auto-generated ID.",
    responses={
        201: {"description": "Practitioner successfully created and persisted to the database."},
        400: {"description": "Invalid FHIR Practitioner payload — failed FHIR schema validation."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
        422: {"description": "Validation error — the request body is malformed or missing required fields."},
    },
)
async def create_practitioner(
    payload: PractitionerCreateSchema,
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    data_dict = payload.model_dump(exclude_none=True)
    try:
        validated_fhir_resource = Practitioner.model_validate(data_dict)
        return await practitioner_service.create_practitioner(
            validated_fhir_resource.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Get Practitioner by ID ─────────────────────────────────────────────


@router.get(
    "/{id}",
    response_model=Practitioner,
    dependencies=[Depends(require_permission("practitioner", "read"))],
    operation_id="get_practitioner_by_id",
    summary="Retrieve a Practitioner resource by ID",
    description="""
Retrieve a single FHIR Practitioner resource by its internal database ID. Requires `practitioner:read` permission.

Returns the full Practitioner resource including all demographics, identifiers, contact
information, addresses, and professional qualifications. Returns 404 if no practitioner
exists with the given ID.
""",
    response_description="The FHIR Practitioner resource matching the given ID.",
    responses={
        200: {"description": "Practitioner resource found and returned successfully."},
        404: {"description": "No Practitioner resource exists with the specified ID."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
    },
)
async def get_practitioner(
    id: int = Path(
        ...,
        title="Practitioner ID",
        description="The internal database identifier of the Practitioner resource. Must be a positive integer.",
        examples=[456],
        ge=1,
    ),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    practitioner = await practitioner_service.get_practitioner(id)
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return practitioner


# ── List All Practitioners ─────────────────────────────────────────────


@router.get(
    "/",
    response_model=list[Practitioner],
    dependencies=[Depends(require_permission("practitioner", "read"))],
    operation_id="list_practitioners",
    summary="List all Practitioner resources",
    description="""
Retrieve a list of all FHIR Practitioner resources stored in the system. Requires `practitioner:read` permission.

Returns an array of complete Practitioner resources. Each resource includes all demographics,
identifiers, contact information, addresses, and professional qualifications.

Returns an empty array if no practitioners exist.
""",
    response_description="An array of all FHIR Practitioner resources in the system.",
    responses={
        200: {"description": "Successfully retrieved the list of practitioners."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
    },
)
async def list_practitioners(
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    return await practitioner_service.list_practitioners()


# ── Update Practitioner ────────────────────────────────────────────────


@router.put(
    "/{id}",
    response_model=Practitioner,
    dependencies=[Depends(require_permission("practitioner", "update"))],
    operation_id="update_practitioner",
    summary="Update an existing Practitioner resource (full replacement)",
    description="""
Update an existing FHIR Practitioner resource by replacing it entirely with the provided payload. Requires `practitioner:update` permission.

This implements FHIR-standard PUT semantics — the entire resource is replaced, not merged.
Any fields not included in the request body will be removed from the resource. To preserve
existing data, include all current fields in the request.

The `id` path parameter identifies the practitioner to update. Returns 404 if no
practitioner exists with the given ID.
""",
    response_description="The updated FHIR Practitioner resource after full replacement.",
    responses={
        200: {"description": "Practitioner resource successfully updated."},
        400: {"description": "Invalid FHIR Practitioner payload — failed FHIR schema validation."},
        404: {"description": "No Practitioner resource exists with the specified ID."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
        422: {"description": "Validation error — the request body is malformed or missing required fields."},
    },
)
async def update_practitioner(
    payload: PractitionerCreateSchema,
    id: int = Path(
        ...,
        title="Practitioner ID",
        description="The internal database identifier of the Practitioner resource to update. Must be a positive integer.",
        examples=[456],
        ge=1,
    ),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    data_dict = payload.model_dump(exclude_none=True)
    try:
        validated_fhir_resource = Practitioner.model_validate(data_dict)
        result = await practitioner_service.update_practitioner(
            id, validated_fhir_resource.model_dump()
        )
        if not result:
            raise HTTPException(status_code=404, detail="Practitioner not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Delete Practitioner ────────────────────────────────────────────────


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("practitioner", "delete"))],
    operation_id="delete_practitioner",
    summary="Delete a Practitioner resource by ID",
    description="""
Permanently delete a FHIR Practitioner resource by its internal database ID. Requires `practitioner:delete` permission.

This operation is irreversible. All associated data (identifiers, names, telecoms,
addresses, qualifications) will also be deleted via cascade. Returns 404 if no
practitioner exists with the given ID.

Returns no content on successful deletion (HTTP 204).
""",
    response_description="Practitioner resource successfully deleted. No content returned.",
    responses={
        204: {"description": "Practitioner resource successfully deleted."},
        404: {"description": "No Practitioner resource exists with the specified ID."},
        401: {"description": "Authentication required — missing or invalid authorization credentials."},
    },
)
async def delete_practitioner(
    id: int = Path(
        ...,
        title="Practitioner ID",
        description="The internal database identifier of the Practitioner resource to delete. Must be a positive integer.",
        examples=[456],
        ge=1,
    ),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    deleted = await practitioner_service.delete_practitioner(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return None
