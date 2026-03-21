from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ── FHIR Data Types ────────────────────────────────────────────────────


class Coding(BaseModel):
    """A reference to a code defined by a terminology system."""

    system: Optional[str] = Field(None, example="http://snomed.info/sct")
    code: Optional[str] = Field(None, example="394814009")
    display: Optional[str] = Field(None, example="General practice")


class CodeableConcept(BaseModel):
    """A concept defined by one or more coding systems plus optional free text."""

    coding: Optional[List[Coding]] = None
    text: Optional[str] = None


class Reference(BaseModel):
    """A FHIR reference to another resource (e.g., 'Patient/123')."""

    reference: Optional[str] = Field(None, example="Patient/123")
    display: Optional[str] = Field(None, example="John Doe")


class Period(BaseModel):
    """A time period with optional start and end."""

    start: Optional[datetime] = Field(None, example="2024-06-01T09:00:00Z")
    end: Optional[datetime] = Field(None, example="2024-06-01T09:30:00Z")


class AppointmentPriority(BaseModel):
    """Priority expressed as a numeric value (0 = low priority, up to a system-defined max)."""

    value: Optional[int] = Field(None, ge=0, example=5)


# ── Backbone Elements ──────────────────────────────────────────────────


class AppointmentParticipantSchema(BaseModel):
    """A participant in the appointment — patient, practitioner, device, or location."""

    type: Optional[List[CodeableConcept]] = Field(
        None,
        title="Participant Type",
        description="Role of the participant in the appointment (e.g., ATND, PART, translator).",
    )
    actor: Optional[Reference] = Field(
        None,
        title="Actor Reference",
        description="FHIR reference to the participant. Supports Patient, Practitioner, PractitionerRole, RelatedPerson, Device, HealthcareService, Location.",
        example={"reference": "Practitioner/456", "display": "Dr. Smith"},
    )
    required: Optional[Literal["required", "optional", "information-only"]] = Field(
        None,
        title="Participant Requirement",
        description="Whether the participant is required to attend the appointment.",
        example="required",
    )
    status: Literal["accepted", "declined", "tentative", "needs-action"] = Field(
        ...,
        title="Participation Status",
        description="The acceptance status of the participant for this appointment.",
        example="accepted",
    )
    period: Optional[Period] = Field(
        None,
        title="Participation Period",
        description="The period during which this participant is involved in the appointment.",
    )


# ── Main Appointment Schema ────────────────────────────────────────────


class AppointmentCreateSchema(BaseModel):
    """
    Schema for creating a FHIR Appointment resource.

    An Appointment is a booking of a healthcare event for a patient and/or
    practitioner(s) at a specific date and time. It follows the HL7 FHIR R5
    Appointment specification.

    Required fields: `status` and `participant` (at least one participant with a status).
    """

    resourceType: str = Field(
        "Appointment",
        title="Resource Type",
        description="Must always be 'Appointment'.",
        pattern="^Appointment$",
        example="Appointment",
    )
    status: Literal[
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
    ] = Field(
        ...,
        title="Appointment Status",
        description=(
            "The lifecycle status of the appointment. "
            "'proposed' = not yet confirmed; 'pending' = awaiting confirmation; "
            "'booked' = confirmed; 'arrived' = patient has arrived; "
            "'fulfilled' = appointment has taken place; 'cancelled' = appointment was cancelled; "
            "'noshow' = patient did not arrive; 'entered-in-error' = entered mistakenly."
        ),
        example="booked",
    )
    serviceCategory: Optional[List[CodeableConcept]] = Field(
        None,
        title="Service Category",
        description="A broad categorization of the service to be performed (e.g., 'General Practice', 'Specialist').",
    )
    serviceType: Optional[List[CodeableConcept]] = Field(
        None,
        title="Service Type",
        description="The specific service to be performed (e.g., 'Consultation', 'Follow-up visit').",
    )
    specialty: Optional[List[CodeableConcept]] = Field(
        None,
        title="Specialty",
        description="The specialty of a practitioner required to perform the service.",
    )
    appointmentType: Optional[CodeableConcept] = Field(
        None,
        title="Appointment Type",
        description="The style of appointment or patient that has been booked (e.g., 'ROUTINE', 'WALKIN', 'FOLLOWUP', 'EMERGENCY').",
    )
    reason: Optional[List[CodeableConcept]] = Field(
        None,
        title="Reason",
        description="The coded reason for the appointment — the chief complaint or clinical indication.",
    )
    priority: Optional[AppointmentPriority] = Field(
        None,
        title="Priority",
        description="The priority of the appointment. Higher values represent lower priority (0 = not prioritized).",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Shown on the subject line in meeting requests and appointment reminders.",
        example="Annual wellness visit",
    )
    subject: Optional[Reference] = Field(
        None,
        title="Subject",
        description="The patient or group the appointment is for. Usually 'Patient/ID'.",
        example={"reference": "Patient/123", "display": "Jane Doe"},
    )
    start: Optional[datetime] = Field(
        None,
        title="Start DateTime",
        description="Date and time the appointment is to take place (ISO 8601).",
        example="2024-06-01T09:00:00Z",
    )
    end: Optional[datetime] = Field(
        None,
        title="End DateTime",
        description="Date and time the appointment concludes (ISO 8601).",
        example="2024-06-01T09:30:00Z",
    )
    minutesDuration: Optional[int] = Field(
        None,
        title="Duration (minutes)",
        description="Number of minutes the appointment is expected to last.",
        ge=1,
        example=30,
    )
    created: Optional[datetime] = Field(
        None,
        title="Created DateTime",
        description="The date that this appointment was initially created.",
        example="2024-05-20T10:00:00Z",
    )
    comment: Optional[str] = Field(
        None,
        title="Comment",
        description="Additional comments about the appointment for the practitioner.",
        example="Patient requested morning slot.",
    )
    patientInstruction: Optional[str] = Field(
        None,
        title="Patient Instruction",
        description="Detailed information and instructions for the patient, such as fasting requirements.",
        example="Please fast for 8 hours prior to the appointment.",
    )
    participant: List[AppointmentParticipantSchema] = Field(
        ...,
        title="Participants",
        description="List of participants involved in the appointment. At least one participant is required.",
        min_length=1,
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "resourceType": "Appointment",
                "status": "booked",
                "serviceCategory": [
                    {
                        "coding": [
                            {
                                "system": "http://example.org/service-category",
                                "code": "gp",
                                "display": "General Practice",
                            }
                        ]
                    }
                ],
                "serviceType": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "11429006",
                                "display": "Consultation",
                            }
                        ],
                        "text": "Consultation",
                    }
                ],
                "specialty": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "394814009",
                                "display": "General practice",
                            }
                        ]
                    }
                ],
                "appointmentType": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
                            "code": "FOLLOWUP",
                            "display": "A follow up visit from a previous appointment",
                        }
                    ]
                },
                "reason": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "274640006",
                                "display": "Fever with chills",
                            }
                        ],
                        "text": "Fever with chills",
                    }
                ],
                "priority": {"value": 5},
                "description": "Follow-up visit for hypertension management",
                "subject": {"reference": "Patient/123", "display": "Jane Doe"},
                "start": "2024-06-01T09:00:00Z",
                "end": "2024-06-01T09:30:00Z",
                "minutesDuration": 30,
                "created": "2024-05-20T10:00:00Z",
                "comment": "Patient prefers morning appointments",
                "patientInstruction": "Please arrive 10 minutes early to complete paperwork.",
                "participant": [
                    {
                        "actor": {"reference": "Patient/123", "display": "Jane Doe"},
                        "required": "required",
                        "status": "accepted",
                    },
                    {
                        "type": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                        "code": "ATND",
                                        "display": "attender",
                                    }
                                ]
                            }
                        ],
                        "actor": {"reference": "Practitioner/456", "display": "Dr. Smith"},
                        "required": "required",
                        "status": "accepted",
                    },
                ],
            }
        }
