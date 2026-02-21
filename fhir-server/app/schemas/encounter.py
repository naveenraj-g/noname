from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- FHIR Data Types (Sub-models) ---

class Coding(BaseModel):
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None

class CodeableConcept(BaseModel):
    coding: Optional[List[Coding]] = None
    text: Optional[str] = None

class Reference(BaseModel):
    reference: Optional[str] = None  # e.g., "Patient/123" or "Practitioner/456"
    display: Optional[str] = None

class Period(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None

class EncounterClass(BaseModel):
    code: str  # inpatient, outpatient, emergency, etc.

class EncounterParticipant(BaseModel):
    type: Optional[List[CodeableConcept]] = None
    individual: Optional[Reference] = None
    period: Optional[Period] = None

class EncounterDiagnosis(BaseModel):
    condition: Optional[Reference] = None
    use: Optional[CodeableConcept] = None
    rank: Optional[int] = None

class EncounterLocation(BaseModel):
    location: Optional[Reference] = None
    status: Optional[str] = Field(None, pattern="^(planned|active|reserved|completed)$")
    period: Optional[Period] = None

# --- Main Encounter Model ---

class EncounterCreateSchema(BaseModel):
    resourceType: str = Field("Encounter", pattern="^Encounter$")
    status: str = Field(..., pattern="^(planned|in-progress|onleave|finished|cancelled|entered-in-error|unknown)$")
    class_fhir: EncounterClass = Field(..., alias="class")
    type: Optional[List[CodeableConcept]] = None
    subject: Optional[Reference] = None  # Usually a Patient reference
    participant: Optional[List[EncounterParticipant]] = None
    period: Optional[Period] = None
    reasonCode: Optional[List[CodeableConcept]] = None
    diagnosis: Optional[List[EncounterDiagnosis]] = None
    location: Optional[List[EncounterLocation]] = None
    priority: Optional[CodeableConcept] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "resourceType": "Encounter",
                "status": "finished",
                "class": {
                    "code": "outpatient"
                },
                "type": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "185349003",
                                "display": "Consultation"
                            }
                        ],
                        "text": "Consultation"
                    }
                ],
                "subject": {
                    "reference": "Patient/12345"
                },
                "participant": [
                    {
                        "type": [
                            {
                                "text": "Primary Physician"
                            }
                        ],
                        "individual": {
                            "reference": "Practitioner/67890"
                        }
                    }
                ],
                "period": {
                    "start": "2024-01-15T09:00:00Z",
                    "end": "2024-01-15T09:30:00Z"
                },
                "reasonCode": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "25064002",
                                "display": "Headache"
                            }
                        ],
                        "text": "Headache"
                    }
                ],
                "diagnosis": [
                    {
                        "condition": {
                            "reference": "Condition/99999"
                        },
                        "use": {
                            "text": "Chief complaint"
                        },
                        "rank": 1
                    }
                ],
                "location": [
                    {
                        "location": {
                            "reference": "Location/room-3"
                        },
                        "status": "completed"
                    }
                ]
            }
        }
