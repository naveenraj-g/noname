from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.encounter import EncounterModel


def to_fhir_encounter(encounter: "EncounterModel") -> dict:
    """
    Convert EncounterModel (with relationships loaded) to a FHIR R4 Encounter dict.

    Rules:
      - Uses encounter_id (public) as the FHIR logical id — never the internal PK.
      - subject / participant individual are reconstructed from stored type enum + public ID.
      - None / empty values are stripped from the output.
    """
    result: dict = {
        "resourceType": "Encounter",
        "id": str(encounter.encounter_id),
        "status": encounter.status,
    }

    # class — FHIR R4: single Coding (not a list)
    if encounter.class_code:
        result["class"] = {"code": encounter.class_code}

    # subject
    if encounter.subject_type and encounter.subject_id:
        result["subject"] = {
            "reference": f"{encounter.subject_type.value}/{encounter.subject_id}"
        }

    # period
    if encounter.period_start or encounter.period_end:
        period: dict = {}
        if encounter.period_start:
            period["start"] = encounter.period_start.isoformat()
        if encounter.period_end:
            period["end"] = encounter.period_end.isoformat()
        result["period"] = period

    # priority
    if encounter.priority:
        result["priority"] = {"text": encounter.priority}

    # type
    if encounter.types:
        type_list = []
        for t in encounter.types:
            entry: dict = {}
            coding = {k: v for k, v in {
                "system": t.coding_system,
                "code": t.coding_code,
                "display": t.coding_display,
            }.items() if v}
            if coding:
                entry["coding"] = [coding]
            if t.text:
                entry["text"] = t.text
            if entry:
                type_list.append(entry)
        if type_list:
            result["type"] = type_list

    # participant
    if encounter.participants:
        participant_list = []
        for p in encounter.participants:
            entry = {}
            if p.type_text:
                entry["type"] = [{"text": t} for t in p.type_text.split(",") if t.strip()]
            if p.reference_type and p.individual_reference:
                entry["individual"] = {
                    "reference": f"{p.reference_type.value}/{p.individual_reference}"
                }
            if p.period_start or p.period_end:
                period = {}
                if p.period_start:
                    period["start"] = p.period_start.isoformat()
                if p.period_end:
                    period["end"] = p.period_end.isoformat()
                entry["period"] = period
            if entry:
                participant_list.append(entry)
        if participant_list:
            result["participant"] = participant_list

    # reasonCode
    if encounter.reason_codes:
        reason_list = []
        for r in encounter.reason_codes:
            entry = {}
            coding = {k: v for k, v in {
                "system": r.coding_system,
                "code": r.coding_code,
                "display": r.coding_display,
            }.items() if v}
            if coding:
                entry["coding"] = [coding]
            if r.text:
                entry["text"] = r.text
            if entry:
                reason_list.append(entry)
        if reason_list:
            result["reasonCode"] = reason_list

    # diagnosis
    if encounter.diagnoses:
        diagnosis_list = []
        for d in encounter.diagnoses:
            entry = {}
            if d.condition_reference:
                entry["condition"] = {"reference": d.condition_reference}
            if d.use_text:
                entry["use"] = {"text": d.use_text}
            if d.rank:
                entry["rank"] = int(d.rank)
            if entry:
                diagnosis_list.append(entry)
        if diagnosis_list:
            result["diagnosis"] = diagnosis_list

    # location
    if encounter.locations:
        location_list = []
        for loc in encounter.locations:
            entry = {}
            if loc.location_reference:
                entry["location"] = {"reference": loc.location_reference}
            if loc.status:
                entry["status"] = loc.status
            if loc.period_start or loc.period_end:
                period = {}
                if loc.period_start:
                    period["start"] = loc.period_start.isoformat()
                if loc.period_end:
                    period["end"] = loc.period_end.isoformat()
                entry["period"] = period
            if entry:
                location_list.append(entry)
        if location_list:
            result["location"] = location_list

    return {k: v for k, v in result.items() if v is not None}


def to_plain_encounter(encounter: "EncounterModel") -> dict:
    """
    Return the encounter as a flat snake_case JSON object — no FHIR conventions.
    Uses public encounter_id as `id`.
    """
    result: dict = {
        "id": encounter.encounter_id,
        "status": encounter.status,
        "class_code": encounter.class_code,
        "priority": encounter.priority,
    }

    if encounter.subject_type and encounter.subject_id:
        result["subject"] = f"{encounter.subject_type.value}/{encounter.subject_id}"

    if encounter.period_start:
        result["period_start"] = encounter.period_start.isoformat()
    if encounter.period_end:
        result["period_end"] = encounter.period_end.isoformat()

    if encounter.types:
        result["types"] = [
            {k: v for k, v in {
                "coding_system": t.coding_system,
                "coding_code": t.coding_code,
                "coding_display": t.coding_display,
                "text": t.text,
            }.items() if v is not None}
            for t in encounter.types
        ]

    if encounter.participants:
        result["participants"] = [
            {k: v for k, v in {
                "type_text": p.type_text,
                "individual": (
                    f"{p.reference_type.value}/{p.individual_reference}"
                    if p.reference_type and p.individual_reference else None
                ),
                "period_start": p.period_start.isoformat() if p.period_start else None,
                "period_end": p.period_end.isoformat() if p.period_end else None,
            }.items() if v is not None}
            for p in encounter.participants
        ]

    if encounter.reason_codes:
        result["reason_codes"] = [
            {k: v for k, v in {
                "coding_system": r.coding_system,
                "coding_code": r.coding_code,
                "coding_display": r.coding_display,
                "text": r.text,
            }.items() if v is not None}
            for r in encounter.reason_codes
        ]

    if encounter.diagnoses:
        result["diagnoses"] = [
            {k: v for k, v in {
                "condition_reference": d.condition_reference,
                "use_text": d.use_text,
                "rank": int(d.rank) if d.rank else None,
            }.items() if v is not None}
            for d in encounter.diagnoses
        ]

    if encounter.locations:
        result["locations"] = [
            {k: v for k, v in {
                "location_reference": loc.location_reference,
                "status": loc.status,
                "period_start": loc.period_start.isoformat() if loc.period_start else None,
                "period_end": loc.period_end.isoformat() if loc.period_end else None,
            }.items() if v is not None}
            for loc in encounter.locations
        ]

    return {k: v for k, v in result.items() if v is not None}
