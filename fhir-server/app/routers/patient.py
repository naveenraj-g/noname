from fastapi import APIRouter, Depends, HTTPException, status, Path
from fhir.resources.patient import Patient
from app.services.patient_service import PatientService
from app.schemas.patient import PatientCreateSchema
from app.di.dependencies.patient import get_patient_service
from app.auth.dependencies import require_permission

router = APIRouter()


# ── Create Patient ─────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=Patient,
    dependencies=[Depends(require_permission("patient", "create"))],
    status_code=status.HTTP_201_CREATED,
    operation_id="create_patient",
    summary="Create a new FHIR Patient resource",
    description="""
Create a new FHIR Patient resource in the system. Requires `patient:create` permission.

This endpoint accepts a structured Patient payload conforming to the HL7 FHIR R4 specification,
validates it against the FHIR Patient schema, and persists it to the database. The server
auto-generates a unique internal ID for the resource.

The payload must include a `resourceType` of "Patient". Recommended fields include at least
one `name` with `use: "official"`, a `gender`, and a `birthDate`. Additional fields such as
`identifier`, `telecom`, and `address` provide richer demographic data.

Returns the complete FHIR Patient resource including the server-assigned `id`.
""",
    response_description="The newly created FHIR Patient resource with auto-generated ID.",
    responses={
        201: {
            "description": "Patient successfully created and persisted to the database."
        },
        400: {
            "description": "Invalid FHIR Patient payload — the request body failed FHIR schema validation."
        },
        401: {
            "description": "Authentication required — missing or invalid authorization credentials."
        },
        422: {
            "description": "Validation error — the request body is malformed or missing required fields."
        },
    },
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


# ── Get Patient by ID ──────────────────────────────────────────────────


@router.get(
    "/{id}",
    response_model=Patient,
    dependencies=[Depends(require_permission("patient", "read"))],
    operation_id="get_patient_by_id",
    summary="Retrieve a Patient resource by ID",
    description="""
Retrieve a single FHIR Patient resource by its internal database ID. Requires `patient:read` permission.

Returns the full Patient resource including all demographics, identifiers, contact
information, and addresses. Returns 404 if no patient exists with the given ID.
""",
    response_description="The FHIR Patient resource matching the given ID.",
    responses={
        200: {"description": "Patient resource found and returned successfully."},
        404: {"description": "No Patient resource exists with the specified ID."},
        401: {
            "description": "Authentication required — missing or invalid authorization credentials."
        },
    },
)
async def get_patient(
    id: int = Path(
        ...,
        title="Patient ID",
        description="The internal database identifier of the Patient resource. Must be a positive integer.",
        examples=[123],
        ge=1,
    ),
    patient_service: PatientService = Depends(get_patient_service),
):
    patient = await patient_service.get_patient(id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ── List All Patients ──────────────────────────────────────────────────


@router.get(
    "/",
    response_model=list[Patient],
    dependencies=[Depends(require_permission("patient", "read"))],
    operation_id="list_patients",
    summary="List all Patient resources",
    description="""
Retrieve a list of all FHIR Patient resources stored in the system. Requires `patient:read` permission.

Returns an array of complete Patient resources. Each resource includes all demographics,
identifiers, contact information, and addresses.

Returns an empty array if no patients exist.
""",
    response_description="An array of all FHIR Patient resources in the system.",
    responses={
        200: {"description": "Successfully retrieved the list of patients."},
        401: {
            "description": "Authentication required — missing or invalid authorization credentials."
        },
        403: {
            "description": "Insufficient permissions — requires patient:read permission."
        },
    },
    response_model_exclude_none=True,
)
async def list_patients(
    patient_service: PatientService = Depends(get_patient_service),
):
    return await patient_service.list_patients()


# ── Update Patient ─────────────────────────────────────────────────────


@router.put(
    "/{id}",
    response_model=Patient,
    dependencies=[Depends(require_permission("patient", "update"))],
    operation_id="update_patient",
    summary="Update an existing Patient resource (full replacement)",
    description="""
Update an existing FHIR Patient resource by replacing it entirely with the provided payload. Requires `patient:update` permission.

This implements FHIR-standard PUT semantics — the entire resource is replaced, not merged.
Any fields not included in the request body will be removed from the resource. To preserve
existing data, include all current fields in the request.

The `id` path parameter identifies the patient to update. The request body must be a valid
FHIR Patient resource. Returns 404 if no patient exists with the given ID.
""",
    response_description="The updated FHIR Patient resource after full replacement.",
    responses={
        200: {"description": "Patient resource successfully updated."},
        400: {
            "description": "Invalid FHIR Patient payload — failed FHIR schema validation."
        },
        404: {"description": "No Patient resource exists with the specified ID."},
        401: {
            "description": "Authentication required — missing or invalid authorization credentials."
        },
        422: {
            "description": "Validation error — the request body is malformed or missing required fields."
        },
    },
)
async def update_patient(
    payload: PatientCreateSchema,
    id: int = Path(
        ...,
        title="Patient ID",
        description="The internal database identifier of the Patient resource to update. Must be a positive integer.",
        examples=[123],
        ge=1,
    ),
    patient_service: PatientService = Depends(get_patient_service),
):
    data_dict = payload.model_dump(exclude_none=True)
    try:
        validated_fhir_resource = Patient.model_validate(data_dict)
        result = await patient_service.update_patient(
            id, validated_fhir_resource.model_dump()
        )
        if not result:
            raise HTTPException(status_code=404, detail="Patient not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Delete Patient ─────────────────────────────────────────────────────


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("patient", "delete"))],
    operation_id="delete_patient",
    summary="Delete a Patient resource by ID",
    description="""
Permanently delete a FHIR Patient resource by its internal database ID. Requires `patient:delete` permission.

This operation is irreversible. All associated data (identifiers, names, telecoms,
addresses) will also be deleted via cascade. Returns 404 if no patient exists with the given ID.

Returns no content on successful deletion (HTTP 204).
""",
    response_description="Patient resource successfully deleted. No content returned.",
    responses={
        204: {"description": "Patient resource successfully deleted."},
        404: {"description": "No Patient resource exists with the specified ID."},
        401: {
            "description": "Authentication required — missing or invalid authorization credentials."
        },
    },
)
async def delete_patient(
    id: int = Path(
        ...,
        title="Patient ID",
        description="The internal database identifier of the Patient resource to delete. Must be a positive integer.",
        examples=[123],
        ge=1,
    ),
    patient_service: PatientService = Depends(get_patient_service),
):
    deleted = await patient_service.delete_patient(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return None
