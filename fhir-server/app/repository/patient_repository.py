
from copy import Error
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.patient import PatientModel, PatientName, PatientIdentifier, PatientTelecom, PatientAddress
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address

class PatientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, patient: Patient) -> Patient:
        # Create Patient Model
        db_patient = PatientModel(
            active=patient.active,
            gender=patient.gender,
            birth_date=patient.birthDate,
            deceased_boolean=patient.deceasedBoolean
        )
        
        # Map Identifiers
        if patient.identifier:
            for ident in patient.identifier:
                db_ident = PatientIdentifier(
                    system=ident.system,
                    value=ident.value,
                    use=ident.use,
                    patient=db_patient
                )
                # No need to add to session explicitly if attached to patient
                
        # Map Names
        if patient.name:
            for name in patient.name:
                given_str = ",".join(name.given) if name.given else None
                db_name = PatientName(
                    use=name.use,
                    family=name.family,
                    given=given_str,
                    text=name.text,
                    patient=db_patient
                )

        # Map Telecoms
        if patient.telecom:
            for telecom in patient.telecom:
                db_telecom = PatientTelecom(
                    system=telecom.system,
                    value=telecom.value,
                    use=telecom.use,
                    rank=telecom.rank,
                    patient=db_patient
                )
        
        # Map Addresses
        if patient.address:
            for addr in patient.address:
                line_str = ",".join(addr.line) if addr.line else None
                db_addr = PatientAddress(
                    use=addr.use,
                    type=addr.type,
                    text=addr.text,
                    line=line_str,
                    city=addr.city,
                    district=addr.district,
                    state=addr.state,
                    postal_code=addr.postalCode,
                    country=addr.country,
                    patient=db_patient
                )

        try:
            self.session.add(db_patient)
            await self.session.commit()
        except Exception:
            await self.session.rollback()    
            raise
        
        # Re-fetch to confirm and load relationships
        return await self.get(db_patient.id)

    async def get(self, patient_id: int) -> Optional[Patient]:
        stmt = (
            select(PatientModel)
            .where(PatientModel.id == patient_id)
            .options(
                selectinload(PatientModel.identifiers),
                selectinload(PatientModel.names),
                selectinload(PatientModel.telecoms),
                selectinload(PatientModel.addresses)
            )
        )
        result = await self.session.execute(stmt)
        db_patient = result.scalars().first()
        
        if not db_patient:
            return None
        
        return self._map_to_fhir(db_patient)

    async def list(self) -> List[Patient]:
        stmt = (
            select(PatientModel)
            .options(
                selectinload(PatientModel.identifiers),
                selectinload(PatientModel.names),
                selectinload(PatientModel.telecoms),
                selectinload(PatientModel.addresses)
            )
        )
        result = await self.session.execute(stmt)
        db_patients = result.scalars().all()
        return [self._map_to_fhir(p) for p in db_patients]

    async def delete(self, patient_id: int) -> bool:
        stmt = select(PatientModel).where(PatientModel.id == patient_id)
        result = await self.session.execute(stmt)
        db_patient = result.scalars().first()
        
        if not db_patient:
            return False
        
        try:
            await self.session.delete(db_patient)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise


    def _map_to_fhir(self, db_patient: PatientModel) -> Patient:
        patient_data = {
            "resourceType": "Patient",
            "id": str(db_patient.id),  # Convert int to str for FHIR
            "active": db_patient.active,
            "gender": db_patient.gender,
            "birthDate": db_patient.birth_date,
            "deceasedBoolean": db_patient.deceased_boolean,
            "identifier": [],
            "name": [],
            "telecom": [],
            "address": []
        }
        
        for ident in db_patient.identifiers:
            patient_data["identifier"].append({
                "system": ident.system,
                "value": ident.value,
                "use": ident.use
            })
            
        for name in db_patient.names:
            given = name.given.split(",") if name.given else []
            patient_data["name"].append({
                "use": name.use,
                "family": name.family,
                "given": given,
                "text": name.text
            })
            
        for telecom in db_patient.telecoms:
            patient_data["telecom"].append({
                "system": telecom.system,
                "value": telecom.value,
                "use": telecom.use,
                "rank": telecom.rank
            })
            
        for addr in db_patient.addresses:
            line = addr.line.split(",") if addr.line else []
            patient_data["address"].append({
                "use": addr.use,
                "type": addr.type,
                "text": addr.text,
                "line": line,
                "city": addr.city,
                "district": addr.district,
                "state": addr.state,
                "postalCode": addr.postal_code,
                "country": addr.country
            })
            
        # Remove empty lists to avoid cluttering or validation issues if strictly needed
        # But fhir.resources handles empty lists gracefully usually, or we can filter
        patient_data = {k: v for k, v in patient_data.items() if v != [] and v is not None}
        
        return Patient.model_validate(patient_data)
