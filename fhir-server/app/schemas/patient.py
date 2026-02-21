from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# --- FHIR Data Types (Sub-models) ---

class Identifier(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None
    use: Optional[str] = Field(None, pattern="^(usual|official|temp|secondary|old)$")

class HumanName(BaseModel):
    use: Optional[str] = Field(None, pattern="^(usual|official|temp|nickname|anonymous|old|maiden)$")
    family: Optional[str] = None
    given: Optional[List[str]] = None
    text: Optional[str] = None

class Telecom(BaseModel):
    system: Optional[str] = Field(None, pattern="^(phone|fax|email|pager|url|sms|other)$")
    value: Optional[str] = None
    use: Optional[str] = Field(None, pattern="^(home|work|temp|old|mobile)$")
    rank: Optional[int] = None

class Address(BaseModel):
    use: Optional[str] = Field(None, pattern="^(home|work|temp|old|billing)$")
    type: Optional[str] = Field(None, pattern="^(postal|physical|both)$")
    line: Optional[List[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None

# --- Main Patient Model ---

class PatientCreateSchema(BaseModel):
    resourceType: str = Field("Patient", Literal=True)
    active: Optional[bool] = True
    identifier: Optional[List[Identifier]] = None
    name: Optional[List[HumanName]] = None
    telecom: Optional[List[Telecom]] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other|unknown)$")
    birthDate: Optional[date] = None
    address: Optional[List[Address]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "resourceType": "Patient",
                "active": True,
                "identifier": [
                    {
                        "system": "http://hospital.goodhealth.com/mrn",
                        "value": "MRN-123456",
                        "use": "official"
                    }
                ],
                "name": [
                    {
                        "use": "official",
                        "family": "Doe",
                        "given": ["John", "A"],
                        "text": "John A Doe"
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": "+1-555-123-4567",
                        "use": "mobile",
                        "rank": 1
                    },
                    {
                        "system": "email",
                        "value": "john.doe@example.com",
                        "use": "home"
                    }
                ],
                "gender": "male",
                "birthDate": "1985-04-12",
                "address": [
                    {
                        "use": "home",
                        "type": "both",
                        "line": ["123 Main Street", "Apt 4B"],
                        "city": "New York",
                        "state": "NY",
                        "postalCode": "10001",
                        "country": "USA"
                    }
                ]
            }
        }