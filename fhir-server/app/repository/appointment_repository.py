from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from fhir.resources.appointment import Appointment

from app.models.appointment import (
    AppointmentModel,
    AppointmentParticipant,
    AppointmentReasonCode,
)


class AppointmentRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(self, appointment_data: dict) -> Appointment:
        async with self.session_factory() as session:
            db_appointment = self._build_appointment_model(appointment_data)
            session.add(db_appointment)
            await session.commit()
            await session.refresh(db_appointment)
            return await self.get(db_appointment.id)

    async def update(self, appointment_id: int, appointment_data: dict) -> Optional[Appointment]:
        async with self.session_factory() as session:
            stmt = (
                select(AppointmentModel)
                .where(AppointmentModel.id == appointment_id)
                .options(
                    selectinload(AppointmentModel.participants),
                    selectinload(AppointmentModel.reason_codes),
                )
            )
            result = await session.execute(stmt)
            db_appointment = result.scalars().first()

            if not db_appointment:
                return None

            # Delete existing child records
            for child in db_appointment.participants:
                await session.delete(child)
            for child in db_appointment.reason_codes:
                await session.delete(child)

            # Update scalar fields
            db_appointment.status = appointment_data.get("status", db_appointment.status)
            db_appointment.start = self._parse_dt(appointment_data.get("start"))
            db_appointment.end = self._parse_dt(appointment_data.get("end"))
            db_appointment.minutes_duration = appointment_data.get("minutesDuration")
            db_appointment.created = self._parse_dt(appointment_data.get("created"))
            db_appointment.description = appointment_data.get("description")
            db_appointment.patient_instruction = appointment_data.get("patientInstruction")
            db_appointment.comment = appointment_data.get("comment")
            db_appointment.subject_reference = self._extract_reference(appointment_data.get("subject"))

            priority_data = appointment_data.get("priority")
            db_appointment.priority_value = (
                priority_data.get("value") if isinstance(priority_data, dict) else None
            )

            self._extract_service_fields(db_appointment, appointment_data)

            # Re-create children
            self._add_participants(db_appointment, appointment_data)
            self._add_reason_codes(db_appointment, appointment_data)

            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

            return await self.get(appointment_id)

    async def get(self, appointment_id: int) -> Optional[Appointment]:
        async with self.session_factory() as session:
            stmt = (
                select(AppointmentModel)
                .where(AppointmentModel.id == appointment_id)
                .options(
                    selectinload(AppointmentModel.participants),
                    selectinload(AppointmentModel.reason_codes),
                )
            )
            result = await session.execute(stmt)
            db_appointment = result.scalars().first()

            if not db_appointment:
                return None

            return self._map_to_fhir(db_appointment)

    async def list(self) -> List[Appointment]:
        async with self.session_factory() as session:
            stmt = select(AppointmentModel).options(
                selectinload(AppointmentModel.participants),
                selectinload(AppointmentModel.reason_codes),
            )
            result = await session.execute(stmt)
            db_appointments = result.scalars().all()
            return [self._map_to_fhir(a) for a in db_appointments]

    async def delete(self, appointment_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(AppointmentModel).where(AppointmentModel.id == appointment_id)
            result = await session.execute(stmt)
            db_appointment = result.scalars().first()

            if not db_appointment:
                return False

            try:
                await session.delete(db_appointment)
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise

    # ── Static helpers ─────────────────────────────────────────────────

    @staticmethod
    def _parse_dt(value) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return None

    @staticmethod
    def _extract_reference(ref_data) -> Optional[str]:
        if isinstance(ref_data, dict):
            return ref_data.get("reference")
        return None

    @staticmethod
    def _extract_first_coding(codeable_list: Optional[list]) -> tuple:
        """Return (code, display) from the first coding of the first CodeableConcept."""
        if not codeable_list:
            return None, None
        first = codeable_list[0] if isinstance(codeable_list[0], dict) else {}
        codings = first.get("coding", [])
        if codings:
            c = codings[0]
            return c.get("code"), c.get("display")
        return None, None

    # ── Build model from dict ──────────────────────────────────────────

    def _build_appointment_model(self, data: dict) -> AppointmentModel:
        priority_data = data.get("priority")
        priority_value = (
            priority_data.get("value") if isinstance(priority_data, dict) else None
        )

        db_appointment = AppointmentModel(
            status=data.get("status"),
            start=self._parse_dt(data.get("start")),
            end=self._parse_dt(data.get("end")),
            minutes_duration=data.get("minutesDuration"),
            created=self._parse_dt(data.get("created")),
            description=data.get("description"),
            patient_instruction=data.get("patientInstruction"),
            comment=data.get("comment"),
            priority_value=priority_value,
            subject_reference=self._extract_reference(data.get("subject")),
        )

        self._extract_service_fields(db_appointment, data)
        self._add_participants(db_appointment, data)
        self._add_reason_codes(db_appointment, data)

        return db_appointment

    def _extract_service_fields(self, db_appointment: AppointmentModel, data: dict):
        svc_cat_code, svc_cat_display = self._extract_first_coding(data.get("serviceCategory"))
        db_appointment.service_category_code = svc_cat_code
        db_appointment.service_category_display = svc_cat_display

        svc_type_code, svc_type_display = self._extract_first_coding(data.get("serviceType"))
        db_appointment.service_type_code = svc_type_code
        db_appointment.service_type_display = svc_type_display

        spec_code, spec_display = self._extract_first_coding(data.get("specialty"))
        db_appointment.specialty_code = spec_code
        db_appointment.specialty_display = spec_display

        apt_type = data.get("appointmentType")
        if isinstance(apt_type, dict):
            codings = apt_type.get("coding", [])
            if codings:
                db_appointment.appointment_type_code = codings[0].get("code")
                db_appointment.appointment_type_display = codings[0].get("display")

    def _add_participants(self, db_appointment: AppointmentModel, data: dict):
        participants = data.get("participant", [])
        for participant in participants:
            type_list = participant.get("type", [])
            type_code = type_display = type_text = None
            if type_list:
                first_type = type_list[0] if isinstance(type_list[0], dict) else {}
                codings = first_type.get("coding", [])
                if codings:
                    type_code = codings[0].get("code")
                    type_display = codings[0].get("display")
                type_text = first_type.get("text")

            actor = participant.get("actor", {})
            actor_reference = actor.get("reference") if isinstance(actor, dict) else None
            actor_display = actor.get("display") if isinstance(actor, dict) else None

            period = participant.get("period", {})
            period_start = self._parse_dt(period.get("start") if isinstance(period, dict) else None)
            period_end = self._parse_dt(period.get("end") if isinstance(period, dict) else None)

            db_appointment.participants.append(
                AppointmentParticipant(
                    actor_reference=actor_reference,
                    actor_display=actor_display,
                    type_code=type_code,
                    type_display=type_display,
                    type_text=type_text,
                    required=participant.get("required"),
                    status=participant.get("status", "needs-action"),
                    period_start=period_start,
                    period_end=period_end,
                )
            )

    def _add_reason_codes(self, db_appointment: AppointmentModel, data: dict):
        reasons = data.get("reason", [])
        for reason in reasons:
            if not isinstance(reason, dict):
                continue
            coding_list = reason.get("coding", [])
            for coding in coding_list:
                db_appointment.reason_codes.append(
                    AppointmentReasonCode(
                        coding_system=coding.get("system"),
                        coding_code=coding.get("code"),
                        coding_display=coding.get("display"),
                        text=reason.get("text"),
                    )
                )

    # ── Map DB model to FHIR ───────────────────────────────────────────

    def _map_to_fhir(self, db: AppointmentModel) -> Appointment:
        data: dict = {
            "resourceType": "Appointment",
            "id": str(db.id),
            "status": db.status,
        }

        if db.start:
            data["start"] = db.start.isoformat()
        if db.end:
            data["end"] = db.end.isoformat()
        if db.minutes_duration is not None:
            data["minutesDuration"] = db.minutes_duration
        if db.created:
            data["created"] = db.created.isoformat()
        if db.description:
            data["description"] = db.description
        if db.patient_instruction:
            data["patientInstruction"] = [{"instruction": db.patient_instruction}]
        if db.comment:
            data["note"] = [{"text": db.comment}]
        if db.priority_value is not None:
            data["priority"] = {"value": db.priority_value}
        if db.subject_reference:
            data["subject"] = {"reference": db.subject_reference}

        # Service category
        if db.service_category_code:
            data["serviceCategory"] = [
                {"coding": [{"code": db.service_category_code, "display": db.service_category_display}]}
            ]
        # Service type
        if db.service_type_code:
            data["serviceType"] = [
                {"concept": {"coding": [{"code": db.service_type_code, "display": db.service_type_display}]}}
            ]
        # Specialty
        if db.specialty_code:
            data["specialty"] = [
                {"coding": [{"code": db.specialty_code, "display": db.specialty_display}]}
            ]
        # Appointment type
        if db.appointment_type_code:
            data["appointmentType"] = {
                "coding": [{"code": db.appointment_type_code, "display": db.appointment_type_display}]
            }

        # Reason codes → R5: reason[].value[].concept
        reason_list = []
        for rc in db.reason_codes:
            concept: dict = {}
            if rc.coding_code or rc.coding_system:
                concept["coding"] = [
                    {"system": rc.coding_system, "code": rc.coding_code, "display": rc.coding_display}
                ]
            if rc.text:
                concept["text"] = rc.text
            if concept:
                reason_list.append({"value": [{"concept": concept}]})
        if reason_list:
            data["reason"] = reason_list

        # Participants
        participant_list = []
        for p in db.participants:
            p_data: dict = {"status": p.status}

            if p.actor_reference:
                p_data["actor"] = {"reference": p.actor_reference}
                if p.actor_display:
                    p_data["actor"]["display"] = p.actor_display

            if p.type_code or p.type_text:
                type_entry: dict = {}
                if p.type_code:
                    type_entry["coding"] = [{"code": p.type_code, "display": p.type_display}]
                if p.type_text:
                    type_entry["text"] = p.type_text
                p_data["type"] = [type_entry]

            if p.required:
                p_data["required"] = p.required

            if p.period_start or p.period_end:
                p_data["period"] = {}
                if p.period_start:
                    p_data["period"]["start"] = p.period_start.isoformat()
                if p.period_end:
                    p_data["period"]["end"] = p.period_end.isoformat()

            participant_list.append(p_data)

        data["participant"] = participant_list

        return Appointment.model_validate(data)
