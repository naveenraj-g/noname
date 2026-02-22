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
from app.models.enum import ParticipantReferenceType
from fhir.resources.encounter import Encounter
from datetime import datetime


class EncounterRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(self, encounter_data: dict) -> Encounter:
        async with self.session_factory() as session:
            # Extract patient_id from subject reference (expecting format: Patient/123)
            patient_id = None
            subject = encounter_data.get("subject")
            if subject and subject.get("reference"):
                ref_parts = subject["reference"].split("/")
                if len(ref_parts) == 2 and ref_parts[0] == "Patient":
                    try:
                        patient_id = int(ref_parts[1])  # Convert to int
                    except ValueError:
                        raise ValueError(
                            f"Invalid patient ID in subject reference: {ref_parts[1]}"
                        )

            if not patient_id:
                raise ValueError(
                    "Encounter must have a valid Patient subject reference"
                )

            # Extract class_code
            class_data = encounter_data.get("class", {})
            class_code = (
                class_data.get("code") if isinstance(class_data, dict) else None
            )

            # Extract period and parse datetime strings
            period = encounter_data.get("period", {})
            period_start = period.get("start") if isinstance(period, dict) else None
            period_end = period.get("end") if isinstance(period, dict) else None

            # Parse datetime strings to datetime objects
            if period_start and isinstance(period_start, str):
                period_start = datetime.fromisoformat(
                    period_start.replace("Z", "+00:00")
                )
            if period_end and isinstance(period_end, str):
                period_end = datetime.fromisoformat(period_end.replace("Z", "+00:00"))

            # Extract priority
            priority_data = encounter_data.get("priority")
            priority_text = (
                priority_data.get("text") if isinstance(priority_data, dict) else None
            )

            # Create Encounter Model
            db_encounter = EncounterModel(
                status=encounter_data.get("status"),
                class_code=class_code,
                priority=priority_text,
                patient_id=patient_id,
                period_start=period_start,
                period_end=period_end,
            )

            # Map Types
            types = encounter_data.get("type", [])
            if types and isinstance(types, list):
                for type_item in types:
                    coding_list = type_item.get("coding", [])
                    for coding in coding_list:
                        db_type = EncounterType(
                            coding_system=coding.get("system"),
                            coding_code=coding.get("code"),
                            coding_display=coding.get("display"),
                            text=type_item.get("text"),
                            encounter=db_encounter,
                        )

            # Map Participants
            participants = encounter_data.get("participant", [])
            if participants and isinstance(participants, list):
                for participant in participants:
                    type_list = participant.get("type", [])
                    type_text = None
                    if type_list:
                        type_text = ",".join(
                            [t.get("text", "") for t in type_list if t.get("text")]
                        )

                    # Parse individual reference
                    reference_type = None
                    participant_patient_id = None
                    participant_practitioner_id = None

                    individual = participant.get("individual")
                    if individual and individual.get("reference"):
                        ref_parts = individual["reference"].split("/")
                        if len(ref_parts) == 2:
                            resource_type, resource_id = ref_parts
                            try:
                                # Convert resource_id to int
                                resource_id_int = int(resource_id)
                                if resource_type == "Patient":
                                    reference_type = ParticipantReferenceType.PATIENT
                                    participant_patient_id = resource_id_int
                                elif resource_type == "Practitioner":
                                    reference_type = (
                                        ParticipantReferenceType.PRACTITIONER
                                    )
                                    participant_practitioner_id = resource_id_int
                            except ValueError:
                                # Skip invalid IDs
                                pass

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

                    # Parse datetime strings
                    if participant_period_start and isinstance(
                        participant_period_start, str
                    ):
                        participant_period_start = datetime.fromisoformat(
                            participant_period_start.replace("Z", "+00:00")
                        )
                    if participant_period_end and isinstance(
                        participant_period_end, str
                    ):
                        participant_period_end = datetime.fromisoformat(
                            participant_period_end.replace("Z", "+00:00")
                        )

                    db_participant = EncounterParticipant(
                        type_text=type_text,
                        reference_type=reference_type,
                        patient_id=participant_patient_id,
                        practitioner_id=participant_practitioner_id,
                        period_start=participant_period_start,
                        period_end=participant_period_end,
                        encounter=db_encounter,
                    )

            # Map Reason Codes
            reason_codes = encounter_data.get("reasonCode", [])
            if reason_codes and isinstance(reason_codes, list):
                for reason in reason_codes:
                    coding_list = reason.get("coding", [])
                    for coding in coding_list:
                        db_reason = EncounterReasonCode(
                            coding_system=coding.get("system"),
                            coding_code=coding.get("code"),
                            coding_display=coding.get("display"),
                            text=reason.get("text"),
                            encounter=db_encounter,
                        )

            # Map Locations
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

                    # Parse datetime strings
                    if location_period_start and isinstance(location_period_start, str):
                        location_period_start = datetime.fromisoformat(
                            location_period_start.replace("Z", "+00:00")
                        )
                    if location_period_end and isinstance(location_period_end, str):
                        location_period_end = datetime.fromisoformat(
                            location_period_end.replace("Z", "+00:00")
                        )

                    db_location = EncounterLocation(
                        location_reference=(
                            location_ref.get("reference")
                            if isinstance(location_ref, dict)
                            else None
                        ),
                        status=location.get("status"),
                        period_start=location_period_start,
                        period_end=location_period_end,
                        encounter=db_encounter,
                    )

            # Map Diagnosis
            diagnoses = encounter_data.get("diagnosis", [])
            if diagnoses and isinstance(diagnoses, list):
                for diagnosis in diagnoses:
                    condition = diagnosis.get("condition", {})
                    use_data = diagnosis.get("use", {})

                    db_diagnosis = EncounterDiagnosis(
                        condition_reference=(
                            condition.get("reference")
                            if isinstance(condition, dict)
                            else None
                        ),
                        use_text=(
                            use_data.get("text") if isinstance(use_data, dict) else None
                        ),
                        rank=diagnosis.get("rank"),
                        encounter=db_encounter,
                    )

            session.add(db_encounter)
            await session.commit()
            await session.refresh(db_encounter)

            return await self.get(db_encounter.id)

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

    def _map_to_fhir(self, db_encounter: EncounterModel) -> Encounter:
        encounter_data = {
            "resourceType": "Encounter",
            "id": str(db_encounter.id),  # Convert int to str for FHIR
            "status": db_encounter.status,
            "type": [],
            "participant": [],
            "diagnosis": [],
            "location": [],
            "reasonCode": [],
        }

        # Map class
        if db_encounter.class_code:
            encounter_data["class"] = {"code": db_encounter.class_code}

        # Map subject (Patient reference)
        if db_encounter.patient_id:
            encounter_data["subject"] = {
                "reference": f"Patient/{db_encounter.patient_id}"
            }

        # Map period
        if db_encounter.period_start or db_encounter.period_end:
            encounter_data["period"] = {}
            if db_encounter.period_start:
                encounter_data["period"][
                    "start"
                ] = db_encounter.period_start.isoformat()
            if db_encounter.period_end:
                encounter_data["period"]["end"] = db_encounter.period_end.isoformat()

        # Map types
        for type_item in db_encounter.types:
            type_data = {"coding": []}
            if type_item.coding_system or type_item.coding_code:
                type_data["coding"].append(
                    {
                        "system": type_item.coding_system,
                        "code": type_item.coding_code,
                        "display": type_item.coding_display,
                    }
                )
            if type_item.text:
                type_data["text"] = type_item.text
            if type_data["coding"] or type_data.get("text"):
                encounter_data["type"].append(type_data)

        # Map participants
        for participant in db_encounter.participants:
            participant_data = {}

            # Reconstruct individual reference from reference_type and foreign keys
            if (
                participant.reference_type == ParticipantReferenceType.PATIENT
                and participant.patient_id
            ):
                participant_data["individual"] = {
                    "reference": f"Patient/{participant.patient_id}"
                }
            elif (
                participant.reference_type == ParticipantReferenceType.PRACTITIONER
                and participant.practitioner_id
            ):
                participant_data["individual"] = {
                    "reference": f"Practitioner/{participant.practitioner_id}"
                }

            if participant.type_text:
                participant_data["type"] = [
                    {"text": t} for t in participant.type_text.split(",")
                ]
            if participant.period_start or participant.period_end:
                participant_data["period"] = {}
                if participant.period_start:
                    participant_data["period"][
                        "start"
                    ] = participant.period_start.isoformat()
                if participant.period_end:
                    participant_data["period"][
                        "end"
                    ] = participant.period_end.isoformat()
            if participant_data:
                encounter_data["participant"].append(participant_data)

        # Map diagnoses
        for diagnosis in db_encounter.diagnoses:
            diagnosis_data = {}
            if diagnosis.condition_reference:
                diagnosis_data["condition"] = {
                    "reference": diagnosis.condition_reference
                }
            if diagnosis.use_text:
                diagnosis_data["use"] = {"text": diagnosis.use_text}
            if diagnosis.rank:
                diagnosis_data["rank"] = int(diagnosis.rank)
            if diagnosis_data:
                encounter_data["diagnosis"].append(diagnosis_data)

        # Map locations
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
                encounter_data["location"].append(location_data)

        # Map reason codes
        for reason in db_encounter.reason_codes:
            reason_data = {"coding": []}
            if reason.coding_system or reason.coding_code:
                reason_data["coding"].append(
                    {
                        "system": reason.coding_system,
                        "code": reason.coding_code,
                        "display": reason.coding_display,
                    }
                )
            if reason.text:
                reason_data["text"] = reason.text
            if reason_data["coding"] or reason_data.get("text"):
                encounter_data["reasonCode"].append(reason_data)

        # Remove empty lists
        encounter_data = {
            k: v for k, v in encounter_data.items() if v != [] and v is not None
        }

        # return Encounter.model_validate(encounter_data)
        return encounter_data
