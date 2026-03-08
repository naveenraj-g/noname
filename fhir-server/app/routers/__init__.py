from fastapi import APIRouter

from .patient import router as patient_router
from .practitioner import router as practitioner_router
from .encounter import router as encounter_router

api_router = APIRouter()

api_router.include_router(patient_router, prefix="/patients", tags=["Patients"])

# api_router.include_router(
#     practitioner_router, prefix="/practitioners", tags=["Practitioner"]
# )

# api_router.include_router(encounter_router, prefix="/encounters", tags=["Encounter"])
