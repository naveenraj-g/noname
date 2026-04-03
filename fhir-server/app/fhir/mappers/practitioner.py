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
    }

    # identifier
    if practitioner.identifiers:
        result["identifier"] = [
            {k: v for k, v in {"system": i.system, "value": i.value, "use": i.use}.items() if v is not None}
            for i in practitioner.identifiers
        ]

    # name
    if practitioner.names:
        names = []
        for n in practitioner.names:
            entry: dict = {}
            if n.use:
                entry["use"] = n.use
            if n.family:
                entry["family"] = n.family
            if n.given:
                entry["given"] = [g for g in n.given.split(",") if g]
            if n.text:
                entry["text"] = n.text
            if n.prefix:
                entry["prefix"] = [p for p in n.prefix.split(",") if p]
            if n.suffix:
                entry["suffix"] = [s for s in n.suffix.split(",") if s]
            if entry:
                names.append(entry)
        if names:
            result["name"] = names

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
        "active": practitioner.active,
        "gender": practitioner.gender,
        "birth_date": practitioner.birth_date.isoformat() if practitioner.birth_date else None,
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

    if practitioner.names:
        result["names"] = [
            {k: v for k, v in {
                "use": n.use,
                "family": n.family,
                "given": [g for g in n.given.split(",") if g] if n.given else None,
                "text": n.text,
                "prefix": [p for p in n.prefix.split(",") if p] if n.prefix else None,
                "suffix": [s for s in n.suffix.split(",") if s] if n.suffix else None,
            }.items() if v}
            for n in practitioner.names
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
