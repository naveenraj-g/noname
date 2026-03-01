from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ── FHIR Data Types (Sub-models) ──────────────────────────────────────


class Coding(BaseModel):
    """A reference to a code defined by a terminology system (e.g., SNOMED CT, ICD-10, LOINC)."""

    system: Optional[str] = Field(
        None,
        title="Code System URI",
        description="The identification of the code system that defines the meaning of the code. Common systems include 'http://snomed.info/sct' (SNOMED CT) and 'http://loinc.org' (LOINC).",
        example="http://snomed.info/sct",
    )
    code: Optional[str] = Field(
        None,
        title="Code Value",
        description="The code from the code system that represents the concept.",
        example="185349003",
    )
    display: Optional[str] = Field(
        None,
        title="Display Text",
        description="A human-readable representation of the code for display purposes.",
        example="Consultation",
    )


class CodeableConcept(BaseModel):
    """A concept that may be defined by one or more coding systems, plus optional free text."""

    coding: Optional[List[Coding]] = Field(
        None,
        title="Codings",
        description="A list of codes from terminology systems that represent this concept. Multiple codings can represent the same concept in different code systems.",
    )
    text: Optional[str] = Field(
        None,
        title="Text Description",
        description="A human-readable plain text representation of the concept, used as a fallback when no coding is available.",
        example="Consultation",
    )


class Reference(BaseModel):
    """A FHIR reference to another resource, using the format 'ResourceType/ID'."""

    reference: Optional[str] = Field(
        None,
        title="Resource Reference",
        description="A relative reference to another FHIR resource in the format 'ResourceType/ID', e.g. 'Patient/123' or 'Practitioner/456'.",
        example="Patient/12345",
    )
    display: Optional[str] = Field(
        None,
        title="Display Text",
        description="A human-readable description of the referenced resource for display purposes.",
        example="John Doe",
    )


class Period(BaseModel):
    """A time period defined by a start and/or end datetime."""

    start: Optional[datetime] = Field(
        None,
        title="Start DateTime",
        description="The start of the period in ISO 8601 datetime format (YYYY-MM-DDTHH:MM:SSZ). Inclusive boundary.",
        example="2024-01-15T09:00:00Z",
    )
    end: Optional[datetime] = Field(
        None,
        title="End DateTime",
        description="The end of the period in ISO 8601 datetime format. If absent, the period is ongoing.",
        example="2024-01-15T09:30:00Z",
    )


class EncounterClass(BaseModel):
    """The classification of the encounter — determines the care setting."""

    code: str = Field(
        ...,
        title="Class Code",
        description="The classification code for the encounter. Common values: 'inpatient' (hospital admission), 'outpatient' (clinic visit), 'emergency' (ER visit), 'virtual' (telehealth).",
        example="outpatient",
    )


class EncounterParticipant(BaseModel):
    """A healthcare provider or person who participated in the encounter."""

    type: Optional[List[CodeableConcept]] = Field(
        None,
        title="Participant Type",
        description="The role of this participant in the encounter, e.g. 'Primary Physician', 'Consulting Physician', 'Nurse'.",
    )
    individual: Optional[Reference] = Field(
        None,
        title="Individual Reference",
        description="A FHIR reference to the Practitioner or Patient who participated, in the format 'Practitioner/ID' or 'Patient/ID'.",
    )
    period: Optional[Period] = Field(
        None,
        title="Participation Period",
        description="The time period during which this individual participated in the encounter.",
    )


class EncounterDiagnosis(BaseModel):
    """A diagnosis relevant to this encounter."""

    condition: Optional[Reference] = Field(
        None,
        title="Condition Reference",
        description="A FHIR reference to the Condition resource describing the diagnosis, in the format 'Condition/ID'.",
    )
    use: Optional[CodeableConcept] = Field(
        None,
        title="Diagnosis Role",
        description="The role this diagnosis plays in the encounter — e.g. 'admission', 'discharge', 'billing', 'chief complaint'.",
    )
    rank: Optional[int] = Field(
        None,
        title="Diagnosis Rank",
        description="Ranking of the diagnosis for this encounter. 1 = primary diagnosis, 2 = secondary, etc.",
        ge=1,
        example=1,
    )


class EncounterLocation(BaseModel):
    """A physical location where the encounter takes place."""

    location: Optional[Reference] = Field(
        None,
        title="Location Reference",
        description="A FHIR reference to the Location resource, in the format 'Location/ID' or 'Location/room-3'.",
    )
    status: Optional[Literal["planned", "active", "reserved", "completed"]] = Field(
        None,
        title="Location Status",
        description="The status of the patient's presence at the location. 'planned' = expected, 'active' = currently there, 'completed' = has left.",
        example="completed",
    )
    period: Optional[Period] = Field(
        None,
        title="Location Period",
        description="The time period during which the patient was at this location.",
    )


# ── Main Encounter Model ──────────────────────────────────────────────


class EncounterCreateSchema(BaseModel):
    """
    Schema for creating a FHIR Encounter resource.

    An Encounter is an interaction between a patient and healthcare provider(s) for the
    purpose of providing healthcare services or assessing the health status of a patient.
    This includes clinic visits, hospital admissions, emergency department visits, and
    telehealth sessions. All fields follow the HL7 FHIR R4 Encounter specification.

    Required fields: 'status' and 'class' (encounter classification).
    """

    resourceType: str = Field(
        "Encounter",
        title="Resource Type",
        description="The FHIR resource type. Must always be 'Encounter' for this schema.",
        pattern="^Encounter$",
        example="Encounter",
    )
    status: Literal[
        "planned", "in-progress", "onleave", "finished", "cancelled", "entered-in-error", "unknown"
    ] = Field(
        ...,
        title="Encounter Status",
        description="The current state of the encounter lifecycle. 'planned' for scheduled visits, 'in-progress' for active encounters, 'finished' for completed visits, 'cancelled' for cancelled appointments, 'entered-in-error' for mistaken entries.",
        example="finished",
    )
    class_fhir: EncounterClass = Field(
        ...,
        alias="class",
        title="Encounter Classification",
        description="The classification of the encounter which determines the care setting. This field uses the FHIR alias 'class'. Provide as {'code': 'outpatient'} or similar.",
    )
    type: Optional[List[CodeableConcept]] = Field(
        None,
        title="Encounter Type",
        description="The specific type of encounter — e.g. 'Consultation', 'Follow-up', 'Annual physical'. Use SNOMED CT codes when available.",
    )
    subject: Optional[Reference] = Field(
        None,
        title="Patient Reference",
        description="A FHIR reference to the Patient who is the subject of this encounter, in the format 'Patient/ID'. This is the patient being seen.",
    )
    participant: Optional[List[EncounterParticipant]] = Field(
        None,
        title="Encounter Participants",
        description="Healthcare providers who participated in the encounter. Include at least the primary attending physician.",
    )
    period: Optional[Period] = Field(
        None,
        title="Encounter Period",
        description="The start and end time of the encounter. For ongoing encounters, only 'start' is set.",
    )
    reasonCode: Optional[List[CodeableConcept]] = Field(
        None,
        title="Reason Codes",
        description="The coded reasons for the encounter — the chief complaint or presenting problem. Use SNOMED CT or ICD-10 codes.",
    )
    diagnosis: Optional[List[EncounterDiagnosis]] = Field(
        None,
        title="Encounter Diagnoses",
        description="Diagnoses relevant to this encounter. Include at least the primary/chief complaint diagnosis with rank 1.",
    )
    location: Optional[List[EncounterLocation]] = Field(
        None,
        title="Encounter Locations",
        description="Physical locations where the encounter took place — rooms, wards, beds, etc.",
    )
    priority: Optional[CodeableConcept] = Field(
        None,
        title="Encounter Priority",
        description="The priority of the encounter — indicates urgency (e.g., 'routine', 'urgent', 'emergency').",
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "resourceType": "Encounter",
                "status": "finished",
                "class": {"code": "outpatient"},
                "type": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "185349003",
                                "display": "Consultation",
                            }
                        ],
                        "text": "Consultation",
                    }
                ],
                "subject": {"reference": "Patient/12345"},
                "participant": [
                    {
                        "type": [{"text": "Primary Physician"}],
                        "individual": {"reference": "Practitioner/67890"},
                    }
                ],
                "period": {
                    "start": "2024-01-15T09:00:00Z",
                    "end": "2024-01-15T09:30:00Z",
                },
                "reasonCode": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "25064002",
                                "display": "Headache",
                            }
                        ],
                        "text": "Headache",
                    }
                ],
                "diagnosis": [
                    {
                        "condition": {"reference": "Condition/99999"},
                        "use": {"text": "Chief complaint"},
                        "rank": 1,
                    }
                ],
                "location": [
                    {
                        "location": {"reference": "Location/room-3"},
                        "status": "completed",
                    }
                ],
            }
        }
