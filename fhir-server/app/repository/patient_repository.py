from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from app.models.patient import PatientModel
from fhir.resources.patient import Patient
from pydantic import ValidationError
from app.errors.infrastructure import InfrastructureError
from app.schemas.resources import PatientCreateSchema, PatientResponseSchema


class PatientRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(self, payload: PatientCreateSchema) -> PatientResponseSchema:
        async with self.session_factory() as session:
            patient = PatientModel(**payload.model_dump(exclude={"resourceType"}))

            try:
                session.add(patient)
                await session.commit()
                await session.refresh(patient)
            except Exception:
                await session.rollback()
                raise

            return PatientResponseSchema.model_validate(patient)

    async def update(
        self, patient_id: int, payload: PatientCreateSchema
    ) -> Optional[PatientResponseSchema]:
        async with self.session_factory() as session:
            stmt = select(PatientModel).where(PatientModel.id == patient_id)
            result = await session.execute(stmt)
            patient = result.scalars().first()

            if not patient:
                return None

            update_data = payload.model_dump(
                exclude_unset=True,
                exclude={"resourceType"},
            )

            for key, value in update_data.items():
                setattr(patient, key, value)

            try:
                await session.commit()
                await session.refresh(patient)
            except Exception:
                await session.rollback()
                raise

            return PatientResponseSchema.model_validate(patient)

    async def get_by_id(self, patient_id: int) -> Optional[PatientResponseSchema]:
        async with self.session_factory() as session:
            stmt = select(PatientModel).where(PatientModel.id == patient_id)
            result = await session.execute(stmt)
            patient = result.scalars().first()

            if not patient:
                return None

            return PatientResponseSchema.model_validate(patient)

    async def get_raw(self, patient_id: int) -> Optional[PatientModel]:
        async with self.session_factory() as session:
            stmt = select(PatientModel).where(PatientModel.id == patient_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def list(self) -> List[PatientResponseSchema]:
        async with self.session_factory() as session:
            stmt = select(PatientModel)
            result = await session.execute(stmt)
            patients = result.scalars().all()
            return [
                PatientResponseSchema.model_validate(patient) for patient in patients
            ]

    async def delete(self, patient_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(PatientModel).where(PatientModel.id == patient_id)
            result = await session.execute(stmt)
            patient = result.scalars().first()

            if not patient:
                return False

            try:
                await session.delete(patient)
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise

    def _map_to_fhir(self, patient: PatientModel) -> dict:
        """
        Convert internal DB model to FHIR Patient resource format
        """

        name = None
        if patient.first_name or patient.last_name:
            name = [
                {
                    "use": "official",
                    "family": patient.last_name,
                    "given": [
                        x for x in [patient.first_name, patient.middle_name] if x
                    ],
                }
            ]

        patient_data = {
            "resourceType": "Patient",
            "id": str(patient.id),
            "identifier": [
                {
                    "system": "http://hospital.local/patient-id",
                    "value": str(patient.patient_id),
                }
            ],
            "active": patient.active,
            "name": name,
            "gender": patient.gender,
            "birthDate": patient.birth_date.isoformat() if patient.birth_date else None,
            "deceasedBoolean": patient.deceased_boolean,
            "deceasedDateTime": patient.deceased_dateTime.isoformat()
            if patient.deceased_dateTime
            else None,
            "maritalStatus": patient.marital_status,
        }

        try:
            return Patient.model_validate(patient_data)
        except ValidationError as e:
            raise InfrastructureError(
                message="Failed to map database entity to FHIR Patient",
                cause=e,
            )
