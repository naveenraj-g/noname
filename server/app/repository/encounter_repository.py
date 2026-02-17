
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.encounter import (
    EncounterModel, EncounterType, EncounterParticipant,
    EncounterDiagnosis, EncounterLocation, EncounterReasonCode
)
from fhir.resources.encounter import Encounter

class EncounterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, encounter: Encounter) -> Encounter:
        # Create Encounter Model
        db_encounter = EncounterModel(
            id=encounter.id,
            status=encounter.status,
            class_code=encounter.class_fhir.code if encounter.class_fhir else None,
            priority=encounter.priority.text if encounter.priority else None,
            subject_reference=encounter.subject.reference if encounter.subject else None,
            period_start=encounter.period.start if encounter.period else None,
            period_end=encounter.period.end if encounter.period else None
        )
        
        # Map Types
        if encounter.type:
            for type_item in encounter.type:
                for coding in (type_item.coding or []):
                    db_type = EncounterType(
                        coding_system=coding.system,
                        coding_code=coding.code,
                        coding_display=coding.display,
                        text=type_item.text,
                        encounter=db_encounter
                    )
                
        # Map Participants
        if encounter.participant:
            for participant in encounter.participant:
                type_text = None
                if participant.type:
                    type_text = ",".join([t.text for t in participant.type if t.text])
                
                db_participant = EncounterParticipant(
                    type_text=type_text,
                    individual_reference=participant.individual.reference if participant.individual else None,
                    period_start=participant.period.start if participant.period else None,
                    period_end=participant.period.end if participant.period else None,
                    encounter=db_encounter
                )
        
        # Map Diagnoses
        if encounter.diagnosis:
            for diagnosis in encounter.diagnosis:
                db_diagnosis = EncounterDiagnosis(
                    condition_reference=diagnosis.condition.reference if diagnosis.condition else None,
                    use_text=diagnosis.use.text if diagnosis.use else None,
                    rank=str(diagnosis.rank) if diagnosis.rank else None,
                    encounter=db_encounter
                )
        
        # Map Locations
        if encounter.location:
            for location in encounter.location:
                db_location = EncounterLocation(
                    location_reference=location.location.reference if location.location else None,
                    status=location.status,
                    period_start=location.period.start if location.period else None,
                    period_end=location.period.end if location.period else None,
                    encounter=db_encounter
                )
        
        # Map Reason Codes
        if encounter.reasonCode:
            for reason_code in encounter.reasonCode:
                for coding in (reason_code.coding or []):
                    db_reason = EncounterReasonCode(
                        coding_system=coding.system,
                        coding_code=coding.code,
                        coding_display=coding.display,
                        text=reason_code.text,
                        encounter=db_encounter
                    )

        try:
            self.session.add(db_encounter)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        
        return await self.get(encounter.id)

    async def get(self, encounter_id: str) -> Optional[Encounter]:
        stmt = (
            select(EncounterModel)
            .where(EncounterModel.id == encounter_id)
            .options(
                selectinload(EncounterModel.types),
                selectinload(EncounterModel.participants),
                selectinload(EncounterModel.diagnoses),
                selectinload(EncounterModel.locations),
                selectinload(EncounterModel.reason_codes)
            )
        )
        result = await self.session.execute(stmt)
        db_encounter = result.scalars().first()
        
        if not db_encounter:
            return None
        
        return self._map_to_fhir(db_encounter)

    async def list(self) -> List[Encounter]:
        stmt = (
            select(EncounterModel)
            .options(
                selectinload(EncounterModel.types),
                selectinload(EncounterModel.participants),
                selectinload(EncounterModel.diagnoses),
                selectinload(EncounterModel.locations),
                selectinload(EncounterModel.reason_codes)
            )
        )
        result = await self.session.execute(stmt)
        db_encounters = result.scalars().all()
        return [self._map_to_fhir(e) for e in db_encounters]

    async def delete(self, encounter_id: str) -> bool:
        stmt = select(EncounterModel).where(EncounterModel.id == encounter_id)
        result = await self.session.execute(stmt)
        db_encounter = result.scalars().first()
        
        if not db_encounter:
            return False
        
        try:
            await self.session.delete(db_encounter)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise

    def _map_to_fhir(self, db_encounter: EncounterModel) -> Encounter:
        encounter_data = {
            "resourceType": "Encounter",
            "id": db_encounter.id,
            "status": db_encounter.status,
            "type": [],
            "participant": [],
            "diagnosis": [],
            "location": [],
            "reasonCode": []
        }
        
        # Map class
        if db_encounter.class_code:
            encounter_data["class"] = {"code": db_encounter.class_code}
        
        # Map subject
        if db_encounter.subject_reference:
            encounter_data["subject"] = {"reference": db_encounter.subject_reference}
        
        # Map period
        if db_encounter.period_start or db_encounter.period_end:
            encounter_data["period"] = {}
            if db_encounter.period_start:
                encounter_data["period"]["start"] = db_encounter.period_start.isoformat()
            if db_encounter.period_end:
                encounter_data["period"]["end"] = db_encounter.period_end.isoformat()
        
        # Map types
        for type_item in db_encounter.types:
            type_data = {"coding": []}
            if type_item.coding_system or type_item.coding_code:
                type_data["coding"].append({
                    "system": type_item.coding_system,
                    "code": type_item.coding_code,
                    "display": type_item.coding_display
                })
            if type_item.text:
                type_data["text"] = type_item.text
            if type_data["coding"] or type_data.get("text"):
                encounter_data["type"].append(type_data)
        
        # Map participants
        for participant in db_encounter.participants:
            participant_data = {}
            if participant.individual_reference:
                participant_data["individual"] = {"reference": participant.individual_reference}
            if participant.type_text:
                participant_data["type"] = [{"text": t} for t in participant.type_text.split(",")]
            if participant.period_start or participant.period_end:
                participant_data["period"] = {}
                if participant.period_start:
                    participant_data["period"]["start"] = participant.period_start.isoformat()
                if participant.period_end:
                    participant_data["period"]["end"] = participant.period_end.isoformat()
            if participant_data:
                encounter_data["participant"].append(participant_data)
        
        # Map diagnoses
        for diagnosis in db_encounter.diagnoses:
            diagnosis_data = {}
            if diagnosis.condition_reference:
                diagnosis_data["condition"] = {"reference": diagnosis.condition_reference}
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
                reason_data["coding"].append({
                    "system": reason.coding_system,
                    "code": reason.coding_code,
                    "display": reason.coding_display
                })
            if reason.text:
                reason_data["text"] = reason.text
            if reason_data["coding"] or reason_data.get("text"):
                encounter_data["reasonCode"].append(reason_data)
        
        # Remove empty lists
        encounter_data = {k: v for k, v in encounter_data.items() if v != [] and v is not None}
        
        return Encounter.model_validate(encounter_data)
