from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.encounter import (
    EncounterModel,
    EncounterType,
    EncounterParticipant,
    EncounterDiagnosis,
    EncounterLocation,
    EncounterReasonCode,
)
from app.models.enum import SubjectReferenceType, ParticipantReferenceType
from fhir.resources.encounter import Encounter
from datetime import datetime


class EncounterRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(self, encounter_data: dict) -> Encounter:
        async with self.session_factory() as session:
            db_encounter = self._build_encounter_model(encounter_data)

            session.add(db_encounter)
            await session.commit()
            await session.refresh(db_encounter)

            return await self.get(db_encounter.id)

    async def update(self, encounter_id: int, encounter_data: dict) -> Optional[Encounter]:
        async with self.session_factory() as session:
            stmt = (
                select(EncounterModel)
                .where(EncounterModel.id == encounter_id)
                .options(
                    selectinload(EncounterModel.types),
                    selectinload(EncounterModel.participants),
                    selectinload(EncounterModel.diagnoses),
                    selectinload(EncounterModel.locations),
                    selectinload(EncounterModel.reason_codes),
                )
            )
            result = await session.execute(stmt)
            db_encounter = result.scalars().first()

            if not db_encounter:
                return None

            # Delete existing child records
            for child in db_encounter.types:
                await session.delete(child)
            for child in db_encounter.participants:
                await session.delete(child)
            for child in db_encounter.diagnoses:
                await session.delete(child)
            for child in db_encounter.locations:
                await session.delete(child)
            for child in db_encounter.reason_codes:
                await session.delete(child)

            # Parse subject reference
            subject_type, subject_id = self._parse_subject_reference(encounter_data)

            # Parse period datetimes
            period = encounter_data.get("period", {})
            period_start = period.get("start") if isinstance(period, dict) else None
            period_end = period.get("end") if isinstance(period, dict) else None
            if period_start and isinstance(period_start, str):
                period_start = datetime.fromisoformat(period_start.replace("Z", "+00:00"))
            if period_end and isinstance(period_end, str):
                period_end = datetime.fromisoformat(period_end.replace("Z", "+00:00"))

            # Extract class_code
            class_data = encounter_data.get("class", {})
            class_code = class_data.get("code") if isinstance(class_data, dict) else None

            # Extract priority
            priority_data = encounter_data.get("priority")
            priority_text = priority_data.get("text") if isinstance(priority_data, dict) else None

            # Update top-level fields
            db_encounter.status = encounter_data.get("status")
            db_encounter.class_code = class_code
            db_encounter.priority = priority_text
            db_encounter.subject_type = subject_type
            db_encounter.subject_id = subject_id
            db_encounter.period_start = period_start
            db_encounter.period_end = period_end

            # Re-create child records
            self._add_types(db_encounter, encounter_data)
            self._add_participants(db_encounter, encounter_data)
            self._add_reason_codes(db_encounter, encounter_data)
            self._add_locations(db_encounter, encounter_data)
            self._add_diagnoses(db_encounter, encounter_data)

            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

            return await self.get(encounter_id)

    async def get(self, encounter_id: int) -> Optional[Encounter]:
        async with self.session_factory() as session:
            stmt = (
                select(EncounterModel)
                .where(EncounterModel.id == encounter_id)
                .options(
                    selectinload(EncounterModel.types),
                    selectinload(EncounterModel.participants),
                    selectinload(EncounterModel.diagnoses),
                    selectinload(EncounterModel.locations),
                    selectinload(EncounterModel.reason_codes),
                )
            )
            result = await session.execute(stmt)
            db_encounter = result.scalars().first()

            if not db_encounter:
                return None

            return self._map_to_fhir(db_encounter)

    async def list(self) -> List[Encounter]:
        async with self.session_factory() as session:
            stmt = select(EncounterModel).options(
                selectinload(EncounterModel.types),
                selectinload(EncounterModel.participants),
                selectinload(EncounterModel.diagnoses),
                selectinload(EncounterModel.locations),
                selectinload(EncounterModel.reason_codes),
            )
            result = await session.execute(stmt)
            db_encounters = result.scalars().all()
            return [self._map_to_fhir(e) for e in db_encounters]

    async def delete(self, encounter_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(EncounterModel).where(EncounterModel.id == encounter_id)
            result = await session.execute(stmt)
            db_encounter = result.scalars().first()

            if not db_encounter:
                return False

            try:
                await session.delete(db_encounter)
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise

    # ── Reference Parsing Helpers ──────────────────────────────────────

    @staticmethod
    def _parse_subject_reference(encounter_data: dict):
        """Parse 'Patient/123' into (SubjectReferenceType.PATIENT, 123)."""
        subject = encounter_data.get("subject")
        if not subject or not isinstance(subject, dict):
            return None, None

        ref_str = subject.get("reference")
        if not ref_str:
            return None, None

        parts = ref_str.split("/")
        if len(parts) != 2:
            return None, None

        resource_type, resource_id = parts
        try:
            subject_type = SubjectReferenceType(resource_type)
            return subject_type, int(resource_id)
        except (ValueError, KeyError):
            return None, None

    @staticmethod
    def _parse_individual_reference(individual: dict):
        """Parse 'Practitioner/456' into (ParticipantReferenceType.PRACTITIONER, 456)."""
        if not individual or not isinstance(individual, dict):
            return None, None

        ref_str = individual.get("reference")
        if not ref_str:
            return None, None

        parts = ref_str.split("/")
        if len(parts) != 2:
            return None, None

        resource_type, resource_id = parts
        try:
            ref_type = ParticipantReferenceType(resource_type)
            return ref_type, int(resource_id)
        except (ValueError, KeyError):
            return None, None

    # ── Helper: Build EncounterModel from dict ─────────────────────────

    def _build_encounter_model(self, encounter_data: dict) -> EncounterModel:
        # Parse subject reference
        subject_type, subject_id = self._parse_subject_reference(encounter_data)

        # Extract class_code
        class_data = encounter_data.get("class", {})
        class_code = class_data.get("code") if isinstance(class_data, dict) else None

        # Extract period and parse datetime strings
        period = encounter_data.get("period", {})
        period_start = period.get("start") if isinstance(period, dict) else None
        period_end = period.get("end") if isinstance(period, dict) else None

        if period_start and isinstance(period_start, str):
            period_start = datetime.fromisoformat(period_start.replace("Z", "+00:00"))
        if period_end and isinstance(period_end, str):
            period_end = datetime.fromisoformat(period_end.replace("Z", "+00:00"))

        # Extract priority
        priority_data = encounter_data.get("priority")
        priority_text = priority_data.get("text") if isinstance(priority_data, dict) else None

        # Create Encounter Model
        db_encounter = EncounterModel(
            status=encounter_data.get("status"),
            class_code=class_code,
            priority=priority_text,
            subject_type=subject_type,
            subject_id=subject_id,
            period_start=period_start,
            period_end=period_end,
        )

        # Map child records
        self._add_types(db_encounter, encounter_data)
        self._add_participants(db_encounter, encounter_data)
        self._add_reason_codes(db_encounter, encounter_data)
        self._add_locations(db_encounter, encounter_data)
        self._add_diagnoses(db_encounter, encounter_data)

        return db_encounter

    # ── Helper: Add child records ──────────────────────────────────────

    def _add_types(self, db_encounter: EncounterModel, encounter_data: dict):
        types = encounter_data.get("type", [])
        if types and isinstance(types, list):
            for type_item in types:
                coding_list = type_item.get("coding", [])
                for coding in coding_list:
                    db_encounter.types.append(EncounterType(
                        coding_system=coding.get("system"),
                        coding_code=coding.get("code"),
                        coding_display=coding.get("display"),
                        text=type_item.get("text"),
                    ))

    def _add_participants(self, db_encounter: EncounterModel, encounter_data: dict):
        participants = encounter_data.get("participant", [])
        if participants and isinstance(participants, list):
            for participant in participants:
                type_list = participant.get("type", [])
                type_text = None
                if type_list:
                    type_text = ",".join(
                        [t.get("text", "") for t in type_list if t.get("text")]
                    )

                # Parse individual reference into type enum + integer ID
                individual = participant.get("individual")
                ref_type, ref_id = self._parse_individual_reference(individual)

                participant_period = participant.get("period", {})
                participant_period_start = (
                    participant_period.get("start")
                    if isinstance(participant_period, dict)
                    else None
                )
                participant_period_end = (
                    participant_period.get("end")
                    if isinstance(participant_period, dict)
                    else None
                )

                if participant_period_start and isinstance(participant_period_start, str):
                    participant_period_start = datetime.fromisoformat(
                        participant_period_start.replace("Z", "+00:00")
                    )
                if participant_period_end and isinstance(participant_period_end, str):
                    participant_period_end = datetime.fromisoformat(
                        participant_period_end.replace("Z", "+00:00")
                    )

                db_encounter.participants.append(EncounterParticipant(
                    type_text=type_text,
                    reference_type=ref_type,
                    individual_reference=ref_id,
                    period_start=participant_period_start,
                    period_end=participant_period_end,
                ))

    def _add_reason_codes(self, db_encounter: EncounterModel, encounter_data: dict):
        reason_codes = encounter_data.get("reasonCode", [])
        if reason_codes and isinstance(reason_codes, list):
            for reason in reason_codes:
                coding_list = reason.get("coding", [])
                for coding in coding_list:
                    db_encounter.reason_codes.append(EncounterReasonCode(
                        coding_system=coding.get("system"),
                        coding_code=coding.get("code"),
                        coding_display=coding.get("display"),
                        text=reason.get("text"),
                    ))

    def _add_locations(self, db_encounter: EncounterModel, encounter_data: dict):
        locations = encounter_data.get("location", [])
        if locations and isinstance(locations, list):
            for location in locations:
                location_ref = location.get("location", {})
                location_period = location.get("period", {})

                location_period_start = (
                    location_period.get("start")
                    if isinstance(location_period, dict)
                    else None
                )
                location_period_end = (
                    location_period.get("end")
                    if isinstance(location_period, dict)
                    else None
                )

                if location_period_start and isinstance(location_period_start, str):
                    location_period_start = datetime.fromisoformat(
                        location_period_start.replace("Z", "+00:00")
                    )
                if location_period_end and isinstance(location_period_end, str):
                    location_period_end = datetime.fromisoformat(
                        location_period_end.replace("Z", "+00:00")
                    )

                db_encounter.locations.append(EncounterLocation(
                    location_reference=(
                        location_ref.get("reference")
                        if isinstance(location_ref, dict)
                        else None
                    ),
                    status=location.get("status"),
                    period_start=location_period_start,
                    period_end=location_period_end,
                ))

    def _add_diagnoses(self, db_encounter: EncounterModel, encounter_data: dict):
        diagnoses = encounter_data.get("diagnosis", [])
        if diagnoses and isinstance(diagnoses, list):
            for diagnosis in diagnoses:
                condition = diagnosis.get("condition", {})
                use_data = diagnosis.get("use", {})

                db_encounter.diagnoses.append(EncounterDiagnosis(
                    condition_reference=(
                        condition.get("reference")
                        if isinstance(condition, dict)
                        else None
                    ),
                    use_text=(
                        use_data.get("text") if isinstance(use_data, dict) else None
                    ),
                    rank=str(diagnosis.get("rank")) if diagnosis.get("rank") is not None else None,
                ))

    # ── Helper: Map DB model to FHIR ──────────────────────────────────

    def _map_to_fhir(self, db_encounter: EncounterModel) -> Encounter:
        """Map DB model to FHIR R5 Encounter (fhir.resources v8.x)."""
        encounter_data = {
            "resourceType": "Encounter",
            "id": str(db_encounter.id),
            "status": db_encounter.status,
        }

        # Map class → List[CodeableConcept] in R5
        if db_encounter.class_code:
            encounter_data["class"] = [
                {"coding": [{"code": db_encounter.class_code}]}
            ]

        # Map subject — reconstruct FHIR reference from type + ID
        if db_encounter.subject_type and db_encounter.subject_id:
            encounter_data["subject"] = {
                "reference": f"{db_encounter.subject_type.value}/{db_encounter.subject_id}"
            }

        # Map priority
        if db_encounter.priority:
            encounter_data["priority"] = {"text": db_encounter.priority}

        # Map period → R5 uses "actualPeriod"
        if db_encounter.period_start or db_encounter.period_end:
            encounter_data["actualPeriod"] = {}
            if db_encounter.period_start:
                encounter_data["actualPeriod"]["start"] = db_encounter.period_start.isoformat()
            if db_encounter.period_end:
                encounter_data["actualPeriod"]["end"] = db_encounter.period_end.isoformat()

        # Map types
        type_list = []
        for type_item in db_encounter.types:
            type_data = {"coding": []}
            if type_item.coding_system or type_item.coding_code:
                type_data["coding"].append({
                    "system": type_item.coding_system,
                    "code": type_item.coding_code,
                    "display": type_item.coding_display,
                })
            if type_item.text:
                type_data["text"] = type_item.text
            if type_data["coding"] or type_data.get("text"):
                type_list.append(type_data)
        if type_list:
            encounter_data["type"] = type_list

        # Map participants — R5 uses "actor" instead of "individual"
        participant_list = []
        for participant in db_encounter.participants:
            participant_data = {}

            if participant.reference_type and participant.individual_reference:
                participant_data["actor"] = {
                    "reference": f"{participant.reference_type.value}/{participant.individual_reference}"
                }

            if participant.type_text:
                participant_data["type"] = [
                    {"text": t} for t in participant.type_text.split(",")
                ]
            if participant.period_start or participant.period_end:
                participant_data["period"] = {}
                if participant.period_start:
                    participant_data["period"]["start"] = participant.period_start.isoformat()
                if participant.period_end:
                    participant_data["period"]["end"] = participant.period_end.isoformat()
            if participant_data:
                participant_list.append(participant_data)
        if participant_list:
            encounter_data["participant"] = participant_list

        # Map diagnoses — R5: condition is List[CodeableReference], use is List[CodeableConcept]
        diagnosis_list = []
        for diagnosis in db_encounter.diagnoses:
            diagnosis_data = {}
            if diagnosis.condition_reference:
                diagnosis_data["condition"] = [
                    {"reference": {"reference": diagnosis.condition_reference}}
                ]
            if diagnosis.use_text:
                diagnosis_data["use"] = [{"text": diagnosis.use_text}]
            if diagnosis_data:
                diagnosis_list.append(diagnosis_data)
        if diagnosis_list:
            encounter_data["diagnosis"] = diagnosis_list

        # Map locations
        location_list = []
        for location in db_encounter.locations:
            location_data = {}
            if location.location_reference:
                location_data["location"] = {"reference": location.location_reference}
            if location.status:
                location_data["status"] = location.status
            if location.period_start or location.period_end:
                location_data["period"] = {}
                if location.period_start:
                    location_data["period"]["start"] = location.period_start.isoformat()
                if location.period_end:
                    location_data["period"]["end"] = location.period_end.isoformat()
            if location_data:
                location_list.append(location_data)
        if location_list:
            encounter_data["location"] = location_list

        # Map reason codes — R5: reason[].value[].concept
        reason_list = []
        for reason in db_encounter.reason_codes:
            concept = {"coding": []}
            if reason.coding_system or reason.coding_code:
                concept["coding"].append({
                    "system": reason.coding_system,
                    "code": reason.coding_code,
                    "display": reason.coding_display,
                })
            if reason.text:
                concept["text"] = reason.text
            if concept["coding"] or concept.get("text"):
                reason_list.append({"value": [{"concept": concept}]})
        if reason_list:
            encounter_data["reason"] = reason_list

        return Encounter.model_validate(encounter_data)
