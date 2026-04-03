from datetime import datetime
from typing import List, Optional
from typing_extensions import Literal
from pydantic import BaseModel, ConfigDict, Field


# ── Appointment status value set (FHIR R4) ────────────────────────────────

AppointmentStatus = Literal[
    "proposed",
    "pending",
    "booked",
    "arrived",
    "fulfilled",
    "cancelled",
    "noshow",
    "entered-in-error",
    "checked-in",
    "waitlist",
]

ParticipantStatus = Literal["accepted", "declined", "tentative", "needs-action"]
ParticipantRequired = Literal["required", "optional", "information-only"]


# ── Sub-resource input schemas ─────────────────────────────────────────────


class AppointmentParticipantInput(BaseModel):
    """A participant involved in the appointment."""

    model_config = ConfigDict(extra="forbid")
    actor: Optional[str] = Field(
        None,
        description="FHIR reference using the public resource ID, e.g. 'Practitioner/30001' or 'Patient/10001'.",
        examples=["Practitioner/30001"],
    )
    actor_display: Optional[str] = Field(None, description="Display name for the actor, e.g. 'Dr. Smith'.")
    type_code: Optional[str] = Field(None, description="Participant role code, e.g. 'ATND'.")
    type_display: Optional[str] = Field(None, description="Human-readable role label, e.g. 'attender'.")
    type_text: Optional[str] = Field(None, description="Free-text role description.")
    required: Optional[ParticipantRequired] = None
    status: ParticipantStatus = Field("needs-action", description="Participation acceptance status.")
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class AppointmentReasonInput(BaseModel):
    """A coded reason / chief complaint for the appointment."""

    model_config = ConfigDict(extra="forbid")
    coding_system: Optional[str] = None
    coding_code: Optional[str] = None
    coding_display: Optional[str] = None
    text: Optional[str] = None


# ── Appointment create / patch ─────────────────────────────────────────────


class AppointmentCreateSchema(BaseModel):
    """
    Payload for creating an Appointment.

    An Appointment is a booking of a healthcare event for a patient and/or
    practitioner(s) at a specific date and time. At least one participant is required.
    References use public IDs (e.g. Patient/10001, Practitioner/30001).
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "booked",
                "subject": "Patient/10001",
                "start": "2024-06-01T09:00:00Z",
                "end": "2024-06-01T09:30:00Z",
                "minutes_duration": 30,
                "description": "Follow-up visit for hypertension management",
                "comment": "Patient prefers morning appointments",
                "patient_instruction": "Please arrive 10 minutes early.",
                "priority_value": 5,
                "service_category_code": "gp",
                "service_category_display": "General Practice",
                "service_type_code": "11429006",
                "service_type_display": "Consultation",
                "specialty_code": "394814009",
                "specialty_display": "General practice",
                "appointment_type_code": "FOLLOWUP",
                "appointment_type_display": "A follow up visit from a previous appointment",
                "reason_codes": [
                    {
                        "coding_system": "http://snomed.info/sct",
                        "coding_code": "274640006",
                        "coding_display": "Fever with chills",
                        "text": "Fever with chills",
                    }
                ],
                "participant": [
                    {
                        "actor": "Patient/10001",
                        "actor_display": "Jane Doe",
                        "required": "required",
                        "status": "accepted",
                    },
                    {
                        "actor": "Practitioner/30001",
                        "actor_display": "Dr. Smith",
                        "type_code": "ATND",
                        "type_display": "attender",
                        "required": "required",
                        "status": "accepted",
                    },
                ],
            }
        },
    )

    status: AppointmentStatus
    subject: Optional[str] = Field(
        None,
        description="Patient reference using the public patient_id, e.g. 'Patient/10001'.",
    )
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    minutes_duration: Optional[int] = Field(None, ge=1, description="Expected duration in minutes.")
    created: Optional[datetime] = Field(None, description="Date this appointment was initially created.")
    description: Optional[str] = None
    comment: Optional[str] = None
    patient_instruction: Optional[str] = None
    priority_value: Optional[int] = Field(None, ge=0, description="Priority (0 = not prioritized, higher = more urgent).")
    service_category_code: Optional[str] = None
    service_category_display: Optional[str] = None
    service_type_code: Optional[str] = None
    service_type_display: Optional[str] = None
    specialty_code: Optional[str] = None
    specialty_display: Optional[str] = None
    appointment_type_code: Optional[str] = None
    appointment_type_display: Optional[str] = None
    reason_codes: Optional[List[AppointmentReasonInput]] = None
    participant: List[AppointmentParticipantInput] = Field(..., min_length=1)


class AppointmentPatchSchema(BaseModel):
    """
    Partial update for an Appointment.

    Allows updating scheduling and lifecycle fields. Structural data
    (participants, service fields) cannot be changed after creation.
    """

    model_config = ConfigDict(extra="forbid")

    status: Optional[AppointmentStatus] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    minutes_duration: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    comment: Optional[str] = None
    patient_instruction: Optional[str] = None
    priority_value: Optional[int] = Field(None, ge=0)


# ── FHIR response fragments (read-only) ───────────────────────────────────


class FHIRCoding(BaseModel):
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None


class FHIRCodeableConcept(BaseModel):
    coding: Optional[List[FHIRCoding]] = None
    text: Optional[str] = None


class FHIRReference(BaseModel):
    reference: Optional[str] = None
    display: Optional[str] = None


class FHIRPeriod(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class FHIRAppointmentParticipant(BaseModel):
    type: Optional[List[FHIRCodeableConcept]] = None
    actor: Optional[FHIRReference] = None
    required: Optional[str] = None
    status: str
    period: Optional[FHIRPeriod] = None


# ── Response schema ────────────────────────────────────────────────────────


class AppointmentResponseSchema(BaseModel):
    """
    FHIR R4 Appointment resource returned by all read/write endpoints.

    - `id` is the PUBLIC appointment_id (e.g. '40001') — never the internal PK.
    - References in subject and participant use public IDs (Patient/10001, Practitioner/30001).
    """

    model_config = ConfigDict(populate_by_name=True)

    resourceType: Literal["Appointment"] = "Appointment"
    id: str = Field(..., description="Public appointment identifier (e.g. '40001').")
    status: str
    subject: Optional[FHIRReference] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    minutesDuration: Optional[int] = None
    created: Optional[datetime] = None
    description: Optional[str] = None
    comment: Optional[str] = None
    patientInstruction: Optional[str] = None
    priority: Optional[int] = None
    serviceCategory: Optional[List[FHIRCodeableConcept]] = None
    serviceType: Optional[List[FHIRCodeableConcept]] = None
    specialty: Optional[List[FHIRCodeableConcept]] = None
    appointmentType: Optional[FHIRCodeableConcept] = None
    reasonCode: Optional[List[FHIRCodeableConcept]] = None
    participant: List[FHIRAppointmentParticipant]
