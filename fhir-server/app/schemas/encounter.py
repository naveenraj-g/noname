from datetime import datetime
from typing import List, Optional
from typing_extensions import Literal
from pydantic import BaseModel, ConfigDict, Field

from app.models.encounter.enums import (
    EncounterStatus,
    EncounterClass,
    EncounterPriority,
    EncounterDiagnosisUse,
    EncounterLocationStatus,
    EncounterBasedOnReferenceType,
    EncounterParticipantReferenceType,
    EncounterSubjectReferenceType,
)


# ── Sub-resource input schemas ─────────────────────────────────────────────


class EncounterTypeInput(BaseModel):
    """One entry in Encounter.type (a coded concept for the encounter's clinical category)."""

    model_config = ConfigDict(extra="forbid")
    coding_system: Optional[str] = Field(None, description="Terminology system URI, e.g. 'http://snomed.info/sct'.")
    coding_code: Optional[str] = Field(None, description="Code value, e.g. '185349003'.")
    coding_display: Optional[str] = Field(None, description="Human-readable code label.")
    text: Optional[str] = Field(None, description="Plain-text description of the encounter type.")


class EncounterParticipantInput(BaseModel):
    """A person who participated in the encounter (provider, patient, etc.)."""

    model_config = ConfigDict(extra="forbid")
    type_text: Optional[str] = Field(
        None,
        description="Participant role, e.g. 'Primary Physician'. Comma-separate multiple roles.",
    )
    individual: Optional[str] = Field(
        None,
        description="FHIR reference using the public resource ID, e.g. 'Practitioner/30001'.",
        examples=["Practitioner/30001"],
    )
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class EncounterReasonCodeInput(BaseModel):
    """A coded reason / chief complaint for the encounter."""

    model_config = ConfigDict(extra="forbid")
    coding_system: Optional[str] = None
    coding_code: Optional[str] = None
    coding_display: Optional[str] = None
    text: Optional[str] = None


class EncounterDiagnosisInput(BaseModel):
    """A diagnosis relevant to this encounter."""

    model_config = ConfigDict(extra="forbid")
    condition_reference: Optional[str] = Field(
        None, description="Reference to the Condition, e.g. 'Condition/99999'."
    )
    use_text: Optional[EncounterDiagnosisUse] = Field(
        None, description="Role of this diagnosis: admission | discharge | billing | other."
    )
    rank: Optional[int] = Field(None, ge=1, description="1 = primary diagnosis.")


class EncounterLocationInput(BaseModel):
    """A physical location involved in the encounter."""

    model_config = ConfigDict(extra="forbid")
    location_reference: Optional[str] = Field(
        None, description="Reference to the Location, e.g. 'Location/room-3'."
    )
    status: Optional[EncounterLocationStatus] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class EncounterBasedOnInput(BaseModel):
    """A request that this encounter fulfils (e.g. a ServiceRequest or CarePlan)."""

    model_config = ConfigDict(extra="forbid")
    reference: str = Field(
        ...,
        description="FHIR reference, e.g. 'ServiceRequest/1234' or 'CarePlan/456'.",
        examples=["ServiceRequest/1234"],
    )
    display: Optional[str] = Field(None, description="Human-readable label for the referenced resource.")


# ── Encounter create / patch ───────────────────────────────────────────────


class EncounterCreateSchema(BaseModel):
    """
    Payload for creating a complete Encounter event.

    All data is submitted as a single document; there are no sub-resource
    endpoints. References use public IDs (e.g. Patient/10001, Practitioner/30001).
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "completed",
                "class_code": "ambulatory",
                "subject": "Patient/10001",
                "subject_display": "John Doe",
                "period_start": "2026-04-01T09:00:00Z",
                "period_end": "2026-04-01T09:30:00Z",
                "priority": "routine",
                "type": [
                    {
                        "coding_system": "http://snomed.info/sct",
                        "coding_code": "185349003",
                        "coding_display": "Consultation",
                        "text": "Consultation",
                    }
                ],
                "participant": [
                    {
                        "type_text": "Primary Physician",
                        "individual": "Practitioner/30001",
                        "period_start": "2026-04-01T09:00:00Z",
                        "period_end": "2026-04-01T09:30:00Z",
                    }
                ],
                "reason_codes": [
                    {
                        "coding_system": "http://snomed.info/sct",
                        "coding_code": "25064002",
                        "coding_display": "Headache",
                        "text": "Headache",
                    }
                ],
                "diagnoses": [
                    {
                        "condition_reference": "Condition/99999",
                        "use_text": "admission",
                        "rank": 1,
                    }
                ],
                "locations": [
                    {"location_reference": "Location/room-3", "status": "completed"}
                ],
                "based_on": [
                    {"reference": "ServiceRequest/1234", "display": "Annual check-up request"}
                ],
            }
        },
    )

    status: EncounterStatus
    class_code: EncounterClass = Field(
        ...,
        description="Encounter class: ambulatory | inpatient | emergency | virtual | observation | home_health.",
    )
    subject: Optional[str] = Field(
        None,
        description="Patient reference using the public patient_id, e.g. 'Patient/10001'.",
    )
    subject_display: Optional[str] = Field(
        None, description="Human-readable display name for the subject, e.g. 'John Doe'."
    )
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    priority: Optional[EncounterPriority] = Field(
        None,
        description="Urgency: routine | urgent | stat | asap.",
    )
    type: Optional[List[EncounterTypeInput]] = None
    participant: Optional[List[EncounterParticipantInput]] = None
    reason_codes: Optional[List[EncounterReasonCodeInput]] = None
    diagnoses: Optional[List[EncounterDiagnosisInput]] = None
    locations: Optional[List[EncounterLocationInput]] = None
    based_on: Optional[List[EncounterBasedOnInput]] = None


class EncounterPatchSchema(BaseModel):
    """
    Partial update for an Encounter.

    Only lifecycle fields are patchable after creation.
    """

    model_config = ConfigDict(extra="forbid")

    status: Optional[EncounterStatus] = None
    period_end: Optional[datetime] = Field(
        None, description="Close the encounter by setting the period end time."
    )
    priority: Optional[EncounterPriority] = None


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


class FHIREncounterParticipant(BaseModel):
    type: Optional[List[FHIRCodeableConcept]] = None
    individual: Optional[FHIRReference] = None
    period: Optional[FHIRPeriod] = None


class FHIREncounterDiagnosis(BaseModel):
    condition: Optional[FHIRReference] = None
    use: Optional[FHIRCodeableConcept] = None
    rank: Optional[int] = None


class FHIREncounterLocation(BaseModel):
    location: Optional[FHIRReference] = None
    status: Optional[str] = None
    period: Optional[FHIRPeriod] = None


# ── Response schemas ───────────────────────────────────────────────────────


class EncounterResponseSchema(BaseModel):
    """
    FHIR R4 Encounter resource returned by all read/write endpoints.

    - `id` is the PUBLIC encounter_id (e.g. '20001') — never the internal PK.
    - References in subject and participant use public IDs (Patient/10001, Practitioner/30001).
    """

    model_config = ConfigDict(populate_by_name=True)

    resourceType: Literal["Encounter"] = "Encounter"
    id: str = Field(..., description="Public encounter identifier (e.g. '20001').")
    status: Optional[str] = None
    # FHIR R4: class is a single Coding (not a list)
    encounter_class: Optional[FHIRCoding] = Field(None, alias="class")
    type: Optional[List[FHIRCodeableConcept]] = None
    subject: Optional[FHIRReference] = None
    participant: Optional[List[FHIREncounterParticipant]] = None
    period: Optional[FHIRPeriod] = None
    reasonCode: Optional[List[FHIRCodeableConcept]] = None
    diagnosis: Optional[List[FHIREncounterDiagnosis]] = None
    location: Optional[List[FHIREncounterLocation]] = None
    priority: Optional[FHIRCodeableConcept] = None
    basedOn: Optional[List[FHIRReference]] = None
