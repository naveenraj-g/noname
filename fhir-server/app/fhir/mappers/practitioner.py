from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.practitioner import PractitionerModel


def to_fhir_practitioner(practitioner: "PractitionerModel") -> dict:
    """
    Convert internal PractitionerModel (with relationships loaded) to a
    FHIR R4 Practitioner resource dict.

    Rules:
      - Uses practitioner_id (public) as the FHIR logical id — never the internal PK.
      - Comma-separated DB fields (given, prefix, suffix, address line) are split to lists.
      - None / empty values are stripped from the output.
    """
    result: dict = {
        "resourceType": "Practitioner",
        "id": str(practitioner.practitioner_id),
        "active": practitioner.active,
        "gender": practitioner.gender,
        "birthDate": practitioner.birth_date.isoformat() if practitioner.birth_date else None,
        "role": practitioner.role,
        "specialty": practitioner.specialty,
        "deceasedBoolean": practitioner.deceased_boolean,
        "deceasedDateTime": practitioner.deceased_datetime.isoformat() if practitioner.deceased_datetime else None,
    }

    # identifier
    if practitioner.identifiers:
        result["identifier"] = [
            {k: v for k, v in {"system": i.system, "value": i.value, "use": i.use}.items() if v is not None}
            for i in practitioner.identifiers
        ]

    # name
    if practitioner.given_name or practitioner.family_name:
        result["name"] = [
            {
                "use": "official",
                "family": practitioner.family_name,
                "given": [practitioner.given_name] if practitioner.given_name else [],
            }
        ]

    # telecom
    if practitioner.telecoms:
        result["telecom"] = [
            {k: v for k, v in {
                "system": t.system,
                "value": t.value,
                "use": t.use,
                "rank": t.rank,
            }.items() if v is not None}
            for t in practitioner.telecoms
        ]

    # address
    if practitioner.addresses:
        addresses = []
        for a in practitioner.addresses:
            entry = {k: v for k, v in {
                "use": a.use,
                "type": a.type,
                "text": a.text,
                "line": [ln for ln in a.line.split(",") if ln] if a.line else None,
                "city": a.city,
                "district": a.district,
                "state": a.state,
                "postalCode": a.postal_code,
                "country": a.country,
            }.items() if v}
            if entry:
                addresses.append(entry)
        if addresses:
            result["address"] = addresses

    # qualification
    if practitioner.qualifications:
        qualifications = []
        for q in practitioner.qualifications:
            entry: dict = {}
            if q.identifier_system or q.identifier_value:
                entry["identifier"] = [{
                    k: v for k, v in {
                        "system": q.identifier_system,
                        "value": q.identifier_value,
                    }.items() if v is not None
                }]
            if q.code_text:
                entry["code"] = {"text": q.code_text}
            if q.issuer:
                entry["issuer"] = {"display": q.issuer}
            if entry:
                qualifications.append(entry)
        if qualifications:
            result["qualification"] = qualifications

    # strip top-level None values
    return {k: v for k, v in result.items() if v is not None}


def to_plain_practitioner(practitioner: "PractitionerModel") -> dict:
    """
    Return the practitioner as a flat, snake_case JSON object — no FHIR conventions.
    Uses public practitioner_id as `id`.
    """
    result: dict = {
        "id": practitioner.practitioner_id,
        "given_name": practitioner.given_name,
        "family_name": practitioner.family_name,
        "active": practitioner.active,
        "gender": practitioner.gender,
        "birth_date": practitioner.birth_date.isoformat() if practitioner.birth_date else None,
        "role": practitioner.role,
        "specialty": practitioner.specialty,
        "deceased_boolean": practitioner.deceased_boolean,
        "deceased_datetime": practitioner.deceased_datetime.isoformat() if practitioner.deceased_datetime else None,
    }

    if practitioner.identifiers:
        result["identifiers"] = [
            {k: v for k, v in {
                "system": i.system,
                "value": i.value,
                "use": i.use,
            }.items() if v is not None}
            for i in practitioner.identifiers
        ]

    if practitioner.telecoms:
        result["telecoms"] = [
            {k: v for k, v in {
                "system": t.system,
                "value": t.value,
                "use": t.use,
                "rank": t.rank,
            }.items() if v is not None}
            for t in practitioner.telecoms
        ]

    if practitioner.addresses:
        result["addresses"] = [
            {k: v for k, v in {
                "use": a.use,
                "type": a.type,
                "line": a.line,
                "city": a.city,
                "district": a.district,
                "state": a.state,
                "postal_code": a.postal_code,
                "country": a.country,
            }.items() if v is not None}
            for a in practitioner.addresses
        ]

    if practitioner.qualifications:
        result["qualifications"] = [
            {k: v for k, v in {
                "identifier_system": q.identifier_system,
                "identifier_value": q.identifier_value,
                "code_text": q.code_text,
                "issuer": q.issuer,
            }.items() if v is not None}
            for q in practitioner.qualifications
        ]

    return {k: v for k, v in result.items() if v is not None}
