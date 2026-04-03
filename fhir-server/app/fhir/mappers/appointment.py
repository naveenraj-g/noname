from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.appointment import AppointmentModel


def to_fhir_appointment(appointment: "AppointmentModel") -> dict:
    """
    Convert AppointmentModel (with relationships loaded) to a FHIR R4 Appointment dict.

    Rules:
      - Uses appointment_id (public) as the FHIR logical id — never the internal PK.
      - priority is an unsignedInt in FHIR R4 (not an object).
      - None / empty values are stripped from the output.
    """
    result: dict = {
        "resourceType": "Appointment",
        "id": str(appointment.appointment_id),
        "status": appointment.status,
    }

    if appointment.start:
        result["start"] = appointment.start.isoformat()
    if appointment.end:
        result["end"] = appointment.end.isoformat()
    if appointment.minutes_duration is not None:
        result["minutesDuration"] = appointment.minutes_duration
    if appointment.created:
        result["created"] = appointment.created.isoformat()
    if appointment.description:
        result["description"] = appointment.description
    if appointment.patient_instruction:
        result["patientInstruction"] = appointment.patient_instruction
    if appointment.comment:
        result["comment"] = appointment.comment
    if appointment.priority_value is not None:
        result["priority"] = appointment.priority_value  # R4: unsignedInt
    if appointment.subject_reference:
        result["subject"] = {"reference": appointment.subject_reference}

    # Coded concept fields
    if appointment.service_category_code:
        coding = {k: v for k, v in {
            "code": appointment.service_category_code,
            "display": appointment.service_category_display,
        }.items() if v}
        result["serviceCategory"] = [{"coding": [coding]}]

    if appointment.service_type_code:
        coding = {k: v for k, v in {
            "code": appointment.service_type_code,
            "display": appointment.service_type_display,
        }.items() if v}
        result["serviceType"] = [{"coding": [coding]}]

    if appointment.specialty_code:
        coding = {k: v for k, v in {
            "code": appointment.specialty_code,
            "display": appointment.specialty_display,
        }.items() if v}
        result["specialty"] = [{"coding": [coding]}]

    if appointment.appointment_type_code:
        coding = {k: v for k, v in {
            "code": appointment.appointment_type_code,
            "display": appointment.appointment_type_display,
        }.items() if v}
        result["appointmentType"] = {"coding": [coding]}

    # reasonCode (FHIR R4)
    if appointment.reason_codes:
        reason_list = []
        for r in appointment.reason_codes:
            entry: dict = {}
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

    # participant (required by FHIR spec)
    participant_list = []
    for p in appointment.participants:
        entry: dict = {"status": p.status}

        if p.actor_reference:
            actor: dict = {"reference": p.actor_reference}
            if p.actor_display:
                actor["display"] = p.actor_display
            entry["actor"] = actor

        if p.type_code or p.type_text:
            type_entry: dict = {}
            if p.type_code:
                type_entry["coding"] = [{k: v for k, v in {
                    "code": p.type_code,
                    "display": p.type_display,
                }.items() if v}]
            if p.type_text:
                type_entry["text"] = p.type_text
            entry["type"] = [type_entry]

        if p.required:
            entry["required"] = p.required

        if p.period_start or p.period_end:
            period: dict = {}
            if p.period_start:
                period["start"] = p.period_start.isoformat()
            if p.period_end:
                period["end"] = p.period_end.isoformat()
            entry["period"] = period

        participant_list.append(entry)

    result["participant"] = participant_list

    return {k: v for k, v in result.items() if v is not None}


def to_plain_appointment(appointment: "AppointmentModel") -> dict:
    """
    Return the appointment as a flat snake_case JSON object — no FHIR conventions.
    Uses public appointment_id as `id`.
    """
    result: dict = {
        "id": appointment.appointment_id,
        "status": appointment.status,
    }

    if appointment.subject_reference:
        result["subject"] = appointment.subject_reference
    if appointment.start:
        result["start"] = appointment.start.isoformat()
    if appointment.end:
        result["end"] = appointment.end.isoformat()
    if appointment.minutes_duration is not None:
        result["minutes_duration"] = appointment.minutes_duration
    if appointment.created:
        result["created"] = appointment.created.isoformat()
    if appointment.description:
        result["description"] = appointment.description
    if appointment.comment:
        result["comment"] = appointment.comment
    if appointment.patient_instruction:
        result["patient_instruction"] = appointment.patient_instruction
    if appointment.priority_value is not None:
        result["priority_value"] = appointment.priority_value
    if appointment.service_category_code:
        result["service_category_code"] = appointment.service_category_code
    if appointment.service_category_display:
        result["service_category_display"] = appointment.service_category_display
    if appointment.service_type_code:
        result["service_type_code"] = appointment.service_type_code
    if appointment.service_type_display:
        result["service_type_display"] = appointment.service_type_display
    if appointment.specialty_code:
        result["specialty_code"] = appointment.specialty_code
    if appointment.specialty_display:
        result["specialty_display"] = appointment.specialty_display
    if appointment.appointment_type_code:
        result["appointment_type_code"] = appointment.appointment_type_code
    if appointment.appointment_type_display:
        result["appointment_type_display"] = appointment.appointment_type_display

    if appointment.reason_codes:
        result["reason_codes"] = [
            {k: v for k, v in {
                "coding_system": r.coding_system,
                "coding_code": r.coding_code,
                "coding_display": r.coding_display,
                "text": r.text,
            }.items() if v is not None}
            for r in appointment.reason_codes
        ]

    if appointment.participants:
        result["participants"] = [
            {k: v for k, v in {
                "actor": p.actor_reference,
                "actor_display": p.actor_display,
                "type_code": p.type_code,
                "type_display": p.type_display,
                "type_text": p.type_text,
                "required": p.required,
                "status": p.status,
                "period_start": p.period_start.isoformat() if p.period_start else None,
                "period_end": p.period_end.isoformat() if p.period_end else None,
            }.items() if v is not None}
            for p in appointment.participants
        ]

    return result
