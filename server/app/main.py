

from app.errors.handlers import (application_error_handler, unhandled_exception_handler)
from app.errors.base import ApplicationError
from fastapi import FastAPI
from app.api.v1.endpoints import patient, practitioner, encounter
from app.core.database import engine, Base

app = FastAPI(title="FastAPI FHIR Server")

# Startup event to create tables if they don't exist (for demo purposes)
# In production, use Alembic migrations.
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# app.add_exception_handler(ApplicationError, application_error_handler)
# app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(patient.router, prefix="/patient", tags=["Patient"])
app.include_router(practitioner.router, prefix="/practitioner", tags=["Practitioner"])
app.include_router(encounter.router, prefix="/encounter", tags=["Encounter"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
