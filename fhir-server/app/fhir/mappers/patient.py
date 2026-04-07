from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.patient import PatientModel


def to_fhir_patient(patient: "PatientModel") -> dict:
    """
    Convert internal PatientModel (with relationships loaded) to a
    FHIR R4 Patient resource dict.

    Rules:
      - Uses patient_id (public) as the FHIR logical id — never the internal PK.
      - All sub-resources are mapped from normalised relationship tables.
      - None / empty values are stripped from the output.
    """
    result: dict = {
        "resourceType": "Patient",
        "id": str(patient.patient_id),
        "active": patient.active,
        "gender": patient.gender,
        "birthDate": patient.birth_date.isoformat() if patient.birth_date else None,
        "deceasedBoolean": patient.deceased_boolean,
        "deceasedDateTime": patient.deceased_datetime.isoformat() if patient.deceased_datetime else None,
    }

    # name
    if patient.given_name or patient.family_name:
        result["name"] = [
            {
                "use": "official",
                "family": patient.family_name,
                "given": [patient.given_name] if patient.given_name else [],
            }
        ]

    # identifier
    if patient.identifiers:
        result["identifier"] = [
            {k: v for k, v in {"system": i.system, "value": i.value}.items() if v is not None}
            for i in patient.identifiers
        ]

    # telecom
    if patient.telecoms:
        result["telecom"] = [
            {k: v for k, v in {"system": t.system, "value": t.value, "use": t.use}.items() if v is not None}
            for t in patient.telecoms
        ]

    # address
    if patient.addresses:
        result["address"] = [
            {k: v for k, v in {
                "line": [a.line] if a.line else [],
                "city": a.city,
                "state": a.state,
                "postalCode": a.postal_code,
                "country": a.country,
            }.items() if v}
            for a in patient.addresses
        ]

    # strip top-level None values
    return {k: v for k, v in result.items() if v is not None}


def to_plain_patient(patient: "PatientModel") -> dict:
    """
    Return the patient as a flat, snake_case JSON object — no FHIR conventions.
    Uses public patient_id as `id`. All sub-resources keep their DB field names.
    """
    result: dict = {
        "id": patient.patient_id,
        "given_name": patient.given_name,
        "family_name": patient.family_name,
        "gender": patient.gender,
        "birth_date": patient.birth_date.isoformat() if patient.birth_date else None,
        "active": patient.active,
        "deceased_boolean": patient.deceased_boolean,
        "deceased_datetime": patient.deceased_datetime.isoformat() if patient.deceased_datetime else None,
    }

    if patient.identifiers:
        result["identifiers"] = [
            {k: v for k, v in {"system": i.system, "value": i.value}.items() if v is not None}
            for i in patient.identifiers
        ]

    if patient.telecoms:
        result["telecoms"] = [
            {k: v for k, v in {
                "system": t.system,
                "value": t.value,
                "use": t.use,
            }.items() if v is not None}
            for t in patient.telecoms
        ]

    if patient.addresses:
        result["addresses"] = [
            {k: v for k, v in {
                "line": a.line,
                "city": a.city,
                "state": a.state,
                "postal_code": a.postal_code,
                "country": a.country,
            }.items() if v is not None}
            for a in patient.addresses
        ]

    return {k: v for k, v in result.items() if v is not None}
