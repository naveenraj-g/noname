from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # noqa: F401
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.appointment import (
    AppointmentModel,
    AppointmentParticipant,
    AppointmentReasonCode,
)
from app.schemas.appointment import AppointmentCreateSchema, AppointmentPatchSchema


def _with_relationships(stmt):
    """Attach eager-load options for all appointment sub-resources."""
    return stmt.options(
        selectinload(AppointmentModel.participants),
        selectinload(AppointmentModel.reason_codes),
    )


class AppointmentRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    # ── Read ──────────────────────────────────────────────────────────────

    async def get_by_appointment_id(self, appointment_id: int) -> Optional[AppointmentModel]:
        """Fetch by public appointment_id with all sub-resources loaded."""
        async with self.session_factory() as session:
            stmt = _with_relationships(
                select(AppointmentModel).where(
                    AppointmentModel.appointment_id == appointment_id
                )
            )
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_me(self, user_id: str, org_id: str) -> List[AppointmentModel]:
        """Fetch all appointments owned by user_id within org_id."""
        async with self.session_factory() as session:
            stmt = _with_relationships(
                select(AppointmentModel).where(
                    AppointmentModel.user_id == user_id,
                    AppointmentModel.org_id == org_id,
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def list(self, patient_id: Optional[int] = None) -> List[AppointmentModel]:
        """List appointments, optionally filtered by public patient_id."""
        async with self.session_factory() as session:
            stmt = _with_relationships(select(AppointmentModel))
            if patient_id is not None:
                # subject_reference is stored as "Patient/10001"
                stmt = stmt.where(
                    AppointmentModel.subject_reference == f"Patient/{patient_id}"
                )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    # ── Write ─────────────────────────────────────────────────────────────

    async def create(
        self,
        payload: AppointmentCreateSchema,
        user_id: str,
        org_id: Optional[str] = None,
    ) -> AppointmentModel:
        async with self.session_factory() as session:
            appointment = AppointmentModel(
                user_id=user_id,
                org_id=org_id,
                status=payload.status,
                subject_reference=payload.subject,
                start=payload.start,
                end=payload.end,
                minutes_duration=payload.minutes_duration,
                created=payload.created,
                description=payload.description,
                comment=payload.comment,
                patient_instruction=payload.patient_instruction,
                priority_value=payload.priority_value,
                service_category_code=payload.service_category_code,
                service_category_display=payload.service_category_display,
                service_type_code=payload.service_type_code,
                service_type_display=payload.service_type_display,
                specialty_code=payload.specialty_code,
                specialty_display=payload.specialty_display,
                appointment_type_code=payload.appointment_type_code,
                appointment_type_display=payload.appointment_type_display,
            )

            # reason codes
            if payload.reason_codes:
                for r in payload.reason_codes:
                    appointment.reason_codes.append(AppointmentReasonCode(
                        coding_system=r.coding_system,
                        coding_code=r.coding_code,
                        coding_display=r.coding_display,
                        text=r.text,
                    ))

            # participants
            for p in payload.participant:
                appointment.participants.append(AppointmentParticipant(
                    actor_reference=p.actor,
                    actor_display=p.actor_display,
                    type_code=p.type_code,
                    type_display=p.type_display,
                    type_text=p.type_text,
                    required=p.required,
                    status=p.status,
                    period_start=p.period_start,
                    period_end=p.period_end,
                ))

            try:
                session.add(appointment)
                await session.commit()
                await session.refresh(appointment)
            except Exception:
                await session.rollback()
                raise

        return await self.get_by_appointment_id(appointment.appointment_id)

    async def patch(
        self, appointment_id: int, payload: AppointmentPatchSchema
    ) -> Optional[AppointmentModel]:
        """Partial update — only fields explicitly set in payload are written."""
        async with self.session_factory() as session:
            stmt = select(AppointmentModel).where(
                AppointmentModel.appointment_id == appointment_id
            )
            result = await session.execute(stmt)
            appointment = result.scalars().first()

            if not appointment:
                return None

            update_data = payload.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(appointment, field, value)

            try:
                await session.commit()
                await session.refresh(appointment)
            except Exception:
                await session.rollback()
                raise

        return await self.get_by_appointment_id(appointment_id)

    async def delete(self, appointment_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(AppointmentModel).where(
                AppointmentModel.appointment_id == appointment_id
            )
            result = await session.execute(stmt)
            appointment = result.scalars().first()

            if not appointment:
                return False

            try:
                await session.delete(appointment)
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise
