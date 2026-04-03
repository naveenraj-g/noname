from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import require_permission
from app.auth.practitioner_deps import get_authorized_practitioner
from app.core.content_negotiation import format_response, format_list_response
from app.di.dependencies.practitioner import get_practitioner_service
from app.models.practitioner import PractitionerModel
from app.schemas.practitioner import (
    PractitionerCreateSchema,
    PractitionerPatchSchema,
    PractitionerResponseSchema,
    PractitionerIdentifierCreate,
    PractitionerNameCreate,
    PractitionerTelecomCreate,
    PractitionerAddressCreate,
    PractitionerQualificationCreate,
)
from app.services.practitioner_service import PractitionerService

router = APIRouter()


# ── Create Practitioner ────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("practitioner", "create"))],
    operation_id="create_practitioner",
    summary="Create a new Practitioner resource",
    description="Creates a Practitioner with core demographics. Add names, identifiers, telecom, addresses, and qualifications via the sub-resource endpoints.",
)
async def create_practitioner(
    payload: PractitionerCreateSchema,
    request: Request,
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    practitioner = await practitioner_service.create_practitioner(payload, user_id, org_id)
    return format_response(
        practitioner_service._to_fhir(practitioner),
        practitioner_service._to_plain(practitioner),
        request,
    )


# ── Get own Practitioner profile (/me) ────────────────────────────────────
# Declared before /{practitioner_id} so "me" is not matched by the int path param.


@router.get(
    "/me",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("practitioner", "read"))],
    operation_id="get_my_practitioner_profile",
    summary="Get the Practitioner profile for the currently authenticated user",
)
async def get_my_practitioner_profile(
    request: Request,
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    user_id: str = request.state.user.get("sub")
    org_id: str = request.state.user.get("activeOrganizationId")
    practitioner = await practitioner_service.get_me(user_id, org_id)
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner profile not found")
    return format_response(
        practitioner_service._to_fhir(practitioner),
        practitioner_service._to_plain(practitioner),
        request,
    )


# ── Get Practitioner by public practitioner_id ─────────────────────────────


@router.get(
    "/{practitioner_id}",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("practitioner", "read"))],
    operation_id="get_practitioner_by_id",
    summary="Retrieve a Practitioner resource by public practitioner_id",
)
async def get_practitioner(
    request: Request,
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    return format_response(
        practitioner_service._to_fhir(practitioner),
        practitioner_service._to_plain(practitioner),
        request,
    )


# ── Patch Practitioner ─────────────────────────────────────────────────────


@router.patch(
    "/{practitioner_id}",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("practitioner", "update"))],
    operation_id="patch_practitioner",
    summary="Partially update a Practitioner resource",
    description="Only supplied fields are written. Omitted fields are unchanged.",
)
async def patch_practitioner(
    payload: PractitionerPatchSchema,
    request: Request,
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    updated = await practitioner_service.patch_practitioner(practitioner.practitioner_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return format_response(
        practitioner_service._to_fhir(updated),
        practitioner_service._to_plain(updated),
        request,
    )


# ── List Practitioners ─────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=list[PractitionerResponseSchema],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission("practitioner", "read"))],
    operation_id="list_practitioners",
    summary="List all Practitioner resources",
)
async def list_practitioners(
    request: Request,
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    practitioners = await practitioner_service.list_practitioners()
    return format_list_response(
        [practitioner_service._to_fhir(p) for p in practitioners],
        [practitioner_service._to_plain(p) for p in practitioners],
        request,
    )


# ── Delete Practitioner ────────────────────────────────────────────────────


@router.delete(
    "/{practitioner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("practitioner", "delete"))],
    operation_id="delete_practitioner",
    summary="Delete a Practitioner resource",
)
async def delete_practitioner(
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    await practitioner_service.delete_practitioner(practitioner.practitioner_id)
    return None


# ── Sub-resource: Identifiers ──────────────────────────────────────────────


@router.post(
    "/{practitioner_id}/identifiers",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("practitioner", "update"))],
    operation_id="add_practitioner_identifier",
    summary="Add a business identifier to a Practitioner (e.g. NPI, license number)",
)
async def add_identifier(
    payload: PractitionerIdentifierCreate,
    request: Request,
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    updated = await practitioner_service.add_identifier(practitioner.practitioner_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return format_response(
        practitioner_service._to_fhir(updated),
        practitioner_service._to_plain(updated),
        request,
    )


# ── Sub-resource: Names ────────────────────────────────────────────────────


@router.post(
    "/{practitioner_id}/names",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("practitioner", "update"))],
    operation_id="add_practitioner_name",
    summary="Add a name to a Practitioner",
)
async def add_name(
    payload: PractitionerNameCreate,
    request: Request,
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    updated = await practitioner_service.add_name(practitioner.practitioner_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return format_response(
        practitioner_service._to_fhir(updated),
        practitioner_service._to_plain(updated),
        request,
    )


# ── Sub-resource: Telecom ──────────────────────────────────────────────────


@router.post(
    "/{practitioner_id}/telecom",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("practitioner", "update"))],
    operation_id="add_practitioner_telecom",
    summary="Add a contact point (telecom) to a Practitioner",
)
async def add_telecom(
    payload: PractitionerTelecomCreate,
    request: Request,
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    updated = await practitioner_service.add_telecom(practitioner.practitioner_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return format_response(
        practitioner_service._to_fhir(updated),
        practitioner_service._to_plain(updated),
        request,
    )


# ── Sub-resource: Addresses ────────────────────────────────────────────────


@router.post(
    "/{practitioner_id}/addresses",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("practitioner", "update"))],
    operation_id="add_practitioner_address",
    summary="Add an address to a Practitioner",
)
async def add_address(
    payload: PractitionerAddressCreate,
    request: Request,
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    updated = await practitioner_service.add_address(practitioner.practitioner_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return format_response(
        practitioner_service._to_fhir(updated),
        practitioner_service._to_plain(updated),
        request,
    )


# ── Sub-resource: Qualifications ───────────────────────────────────────────


@router.post(
    "/{practitioner_id}/qualifications",
    response_model=PractitionerResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("practitioner", "update"))],
    operation_id="add_practitioner_qualification",
    summary="Add a professional qualification to a Practitioner",
    description="Records a degree, certification, accreditation, or license — e.g. MD, board certification, DEA number.",
)
async def add_qualification(
    payload: PractitionerQualificationCreate,
    request: Request,
    practitioner: PractitionerModel = Depends(get_authorized_practitioner),
    practitioner_service: PractitionerService = Depends(get_practitioner_service),
):
    updated = await practitioner_service.add_qualification(practitioner.practitioner_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return format_response(
        practitioner_service._to_fhir(updated),
        practitioner_service._to_plain(updated),
        request,
    )
