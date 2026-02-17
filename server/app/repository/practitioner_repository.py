
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.practitioner import (
    PractitionerModel, PractitionerName, PractitionerIdentifier,
    PractitionerTelecom, PractitionerAddress, PractitionerQualification
)
from fhir.resources.practitioner import Practitioner

class PractitionerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, practitioner: Practitioner) -> Practitioner:
        # Create Practitioner Model
        db_practitioner = PractitionerModel(
            active=practitioner.active,
            gender=practitioner.gender,
            birth_date=practitioner.birthDate
        )
        
        # Map Identifiers
        if practitioner.identifier:
            for ident in practitioner.identifier:
                db_ident = PractitionerIdentifier(
                    system=ident.system,
                    value=ident.value,
                    use=ident.use,
                    practitioner=db_practitioner
                )
                
        # Map Names
        if practitioner.name:
            for name in practitioner.name:
                given_str = ",".join(name.given) if name.given else None
                prefix_str = ",".join(name.prefix) if name.prefix else None
                suffix_str = ",".join(name.suffix) if name.suffix else None
                db_name = PractitionerName(
                    use=name.use,
                    family=name.family,
                    given=given_str,
                    text=name.text,
                    prefix=prefix_str,
                    suffix=suffix_str,
                    practitioner=db_practitioner
                )

        # Map Telecoms
        if practitioner.telecom:
            for telecom in practitioner.telecom:
                db_telecom = PractitionerTelecom(
                    system=telecom.system,
                    value=telecom.value,
                    use=telecom.use,
                    rank=telecom.rank,
                    practitioner=db_practitioner
                )
        
        # Map Addresses
        if practitioner.address:
            for addr in practitioner.address:
                line_str = ",".join(addr.line) if addr.line else None
                db_addr = PractitionerAddress(
                    use=addr.use,
                    type=addr.type,
                    text=addr.text,
                    line=line_str,
                    city=addr.city,
                    district=addr.district,
                    state=addr.state,
                    postal_code=addr.postalCode,
                    country=addr.country,
                    practitioner=db_practitioner
                )

        # Map Qualifications
        if practitioner.qualification:
            for qual in practitioner.qualification:
                db_qual = PractitionerQualification(
                    identifier_system=qual.identifier[0].system if qual.identifier else None,
                    identifier_value=qual.identifier[0].value if qual.identifier else None,
                    code_text=qual.code.text if qual.code else None,
                    issuer=qual.issuer.display if qual.issuer else None,
                    practitioner=db_practitioner
                )

        try:
            self.session.add(db_practitioner)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        
        # Re-fetch to confirm and load relationships
        return await self.get(db_practitioner.id)

    async def get(self, practitioner_id: int) -> Optional[Practitioner]:
        stmt = (
            select(PractitionerModel)
            .where(PractitionerModel.id == practitioner_id)
            .options(
                selectinload(PractitionerModel.identifiers),
                selectinload(PractitionerModel.names),
                selectinload(PractitionerModel.telecoms),
                selectinload(PractitionerModel.addresses),
                selectinload(PractitionerModel.qualifications)
            )
        )
        result = await self.session.execute(stmt)
        db_practitioner = result.scalars().first()
        
        if not db_practitioner:
            return None
        
        return self._map_to_fhir(db_practitioner)

    async def list(self) -> List[Practitioner]:
        stmt = (
            select(PractitionerModel)
            .options(
                selectinload(PractitionerModel.identifiers),
                selectinload(PractitionerModel.names),
                selectinload(PractitionerModel.telecoms),
                selectinload(PractitionerModel.addresses),
                selectinload(PractitionerModel.qualifications)
            )
        )
        result = await self.session.execute(stmt)
        db_practitioners = result.scalars().all()
        return [self._map_to_fhir(p) for p in db_practitioners]

    async def delete(self, practitioner_id: int) -> bool:
        stmt = select(PractitionerModel).where(PractitionerModel.id == practitioner_id)
        result = await self.session.execute(stmt)
        db_practitioner = result.scalars().first()
        
        if not db_practitioner:
            return False
        
        try:
            await self.session.delete(db_practitioner)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise

    def _map_to_fhir(self, db_practitioner: PractitionerModel) -> Practitioner:
        practitioner_data = {
            "resourceType": "Practitioner",
            "id": str(db_practitioner.id),  # Convert int to str for FHIR
            "active": db_practitioner.active,
            "gender": db_practitioner.gender,
            "birthDate": db_practitioner.birth_date,
            "identifier": [],
            "name": [],
            "telecom": [],
            "address": [],
            "qualification": []
        }
        
        for ident in db_practitioner.identifiers:
            practitioner_data["identifier"].append({
                "system": ident.system,
                "value": ident.value,
                "use": ident.use
            })
            
        for name in db_practitioner.names:
            given = name.given.split(",") if name.given else []
            prefix = name.prefix.split(",") if name.prefix else []
            suffix = name.suffix.split(",") if name.suffix else []
            practitioner_data["name"].append({
                "use": name.use,
                "family": name.family,
                "given": given,
                "text": name.text,
                "prefix": prefix,
                "suffix": suffix
            })
            
        for telecom in db_practitioner.telecoms:
            practitioner_data["telecom"].append({
                "system": telecom.system,
                "value": telecom.value,
                "use": telecom.use,
                "rank": telecom.rank
            })
            
        for addr in db_practitioner.addresses:
            line = addr.line.split(",") if addr.line else []
            practitioner_data["address"].append({
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
        
        for qual in db_practitioner.qualifications:
            qual_data = {}
            if qual.identifier_system or qual.identifier_value:
                qual_data["identifier"] = [{
                    "system": qual.identifier_system,
                    "value": qual.identifier_value
                }]
            if qual.code_text:
                qual_data["code"] = {"text": qual.code_text}
            if qual.issuer:
                qual_data["issuer"] = {"display": qual.issuer}
            if qual_data:
                practitioner_data["qualification"].append(qual_data)
            
        # Remove empty lists
        practitioner_data = {k: v for k, v in practitioner_data.items() if v != [] and v is not None}
        
        return Practitioner.model_validate(practitioner_data)
