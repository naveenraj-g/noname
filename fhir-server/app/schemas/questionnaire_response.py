from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from datetime import datetime, date


# ── FHIR Data Types ─────────────────────────────────────────────────────────


class Coding(BaseModel):
    system: Optional[str] = Field(None, example="http://snomed.info/sct")
    code: Optional[str] = Field(None, example="394814009")
    display: Optional[str] = Field(None, example="General practice")


class Reference(BaseModel):
    reference: Optional[str] = Field(None, example="Patient/123")
    display: Optional[str] = Field(None, example="John Doe")


class Quantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None


# ── Answer Value Types ───────────────────────────────────────────────────────


class AnswerSchema(BaseModel):
    """
    A single answer value within a QuestionnaireResponse item.
    Exactly one value[x] field should be set.
    """

    valueBoolean: Optional[bool] = Field(None, description="Boolean answer value")
    valueDecimal: Optional[float] = Field(None, description="Decimal answer value")
    valueInteger: Optional[int] = Field(None, description="Integer answer value")
    valueDate: Optional[str] = Field(None, description="Date answer value (YYYY-MM-DD)", example="2024-06-01")
    valueDateTime: Optional[datetime] = Field(None, description="DateTime answer value")
    valueTime: Optional[str] = Field(None, description="Time answer value (HH:MM:SS)", example="09:00:00")
    valueString: Optional[str] = Field(None, description="String answer value")
    valueUri: Optional[str] = Field(None, description="URI answer value")
    valueCoding: Optional[Coding] = Field(None, description="Coded answer value")
    valueQuantity: Optional[Quantity] = Field(None, description="Quantity answer value")
    valueReference: Optional[Reference] = Field(None, description="Reference answer value")

    # nested items within an answer (for conditional groups)
    item: Optional[List["ItemSchema"]] = Field(None, description="Nested items within this answer")


# ── Item (recursive backbone element) ────────────────────────────────────────


class ItemSchema(BaseModel):
    """
    A group or question item within the QuestionnaireResponse.
    Items can be nested to represent grouped questions.
    """

    linkId: str = Field(
        ...,
        description="Pointer to specific item from Questionnaire. Required.",
        example="1.1",
    )
    definition: Optional[str] = Field(
        None,
        description="ElementDefinition — details for the item.",
    )
    text: Optional[str] = Field(
        None,
        description="Name for group or question text.",
        example="What is your date of birth?",
    )
    answer: Optional[List[AnswerSchema]] = Field(
        None,
        description="The response(s) to the question.",
    )
    item: Optional[List["ItemSchema"]] = Field(
        None,
        description="Nested items for groups or conditional follow-up questions.",
    )


AnswerSchema.model_rebuild()
ItemSchema.model_rebuild()


# ── Main Schema ───────────────────────────────────────────────────────────────


class QuestionnaireResponseCreateSchema(BaseModel):
    """
    Schema for creating a FHIR QuestionnaireResponse resource.

    A QuestionnaireResponse is a completed or in-progress set of answers
    to questions from a Questionnaire. It follows the HL7 FHIR R5
    QuestionnaireResponse specification.

    Required fields: `questionnaire` and `status`.
    """

    resourceType: str = Field(
        "QuestionnaireResponse",
        pattern="^QuestionnaireResponse$",
        example="QuestionnaireResponse",
    )
    questionnaire: str = Field(
        ...,
        description="The Questionnaire that defines and organizes these questions (canonical URL or id).",
        example="http://example.org/fhir/Questionnaire/phq-9",
    )
    status: Literal["in-progress", "completed", "amended", "entered-in-error", "stopped"] = Field(
        ...,
        description=(
            "The lifecycle status of the response. "
            "'in-progress' = being filled out; 'completed' = fully completed; "
            "'amended' = corrected after completion; 'entered-in-error' = recorded in error; "
            "'stopped' = collection was stopped before completion."
        ),
        example="completed",
    )
    subject: Optional[Reference] = Field(
        None,
        description="The subject of the questionnaire response — typically a Patient.",
        example={"reference": "Patient/123", "display": "Jane Doe"},
    )
    encounter: Optional[Reference] = Field(
        None,
        description="The Encounter during which this response was created.",
        example={"reference": "Encounter/456"},
    )
    authored: Optional[datetime] = Field(
        None,
        description="The date/time the answers were gathered.",
        example="2024-06-01T09:00:00Z",
    )
    author: Optional[Reference] = Field(
        None,
        description="Who recorded the answers (Practitioner, Patient, etc.).",
        example={"reference": "Practitioner/789", "display": "Dr. Smith"},
    )
    source: Optional[Reference] = Field(
        None,
        description="Who answered the questions (if different from author).",
        example={"reference": "Patient/123"},
    )
    item: Optional[List[ItemSchema]] = Field(
        None,
        description="The groups and questions that make up the response.",
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "resourceType": "QuestionnaireResponse",
                "questionnaire": "http://example.org/fhir/Questionnaire/phq-9",
                "status": "completed",
                "subject": {"reference": "Patient/123", "display": "Jane Doe"},
                "encounter": {"reference": "Encounter/456"},
                "authored": "2024-06-01T09:00:00Z",
                "author": {"reference": "Practitioner/789", "display": "Dr. Smith"},
                "item": [
                    {
                        "linkId": "1",
                        "text": "Over the last 2 weeks, how often have you felt down, depressed, or hopeless?",
                        "answer": [
                            {"valueCoding": {"system": "http://loinc.org", "code": "LA6568-5", "display": "Not at all"}}
                        ],
                    },
                    {
                        "linkId": "2",
                        "text": "Mental health group",
                        "item": [
                            {
                                "linkId": "2.1",
                                "text": "Do you have difficulty concentrating?",
                                "answer": [{"valueBoolean": False}],
                            }
                        ],
                    },
                ],
            }
        }
