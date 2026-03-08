import base64
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import ValidationError
from app.errors.infrastructure import InfrastructureError
from app.schemas.resources import PatientCreateSchema, PatientResponseSchema
from app.models.patient import (
    PatientModel,
    PatientIdentifier,
    IdentifierType,
    IdentifierTypeCoding,
    PatientIdentifierPeriod,
    PatientName,
    PatientNameGiven,
    PatientNamePrefix,
    PatientNameSuffix,
    PatientNamePeriod,
    PatientTelecom,
    PatientTelecomPeriod,
    PatientAddress,
    PatientAddressLine,
    PatientAddressPeriod,
    PatientMaritalStatus,
    PatientMaritalStatusCoding,
    PatientPhoto,
    PatientContact,
    PatientContactRelationship,
    PatientContactRelationshipCoding,
    PatientContactTelecom,
    PatientContactHumanName,
    PatientContactHumanNameGiven,
    PatientContactHumanNamePrefix,
    PatientContactHumanNameSuffix,
    PatientContactHumanNamePeriod,
    PatientContactAddress,
    PatientContactPeriod,
    PatientCommunication,
    PatientCommunicationLanguage,
    PatientCommunicationLanguageCoding,
    PatientGeneralPractitioner,
    PatientLink,
)


class PatientRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    # ── Eager-load options for all relationships ──────────────────────

    @staticmethod
    def _load_options():
        """Return selectinload options for all patient relationships."""
        return [
            selectinload(PatientModel.identifiers)
            .selectinload(PatientIdentifier.type)
            .selectinload(IdentifierType.codings),
            selectinload(PatientModel.identifiers).selectinload(
                PatientIdentifier.period
            ),
            selectinload(PatientModel.names)
            .selectinload(PatientName.given),
            selectinload(PatientModel.names)
            .selectinload(PatientName.prefix),
            selectinload(PatientModel.names)
            .selectinload(PatientName.suffix),
            selectinload(PatientModel.names)
            .selectinload(PatientName.period),
            selectinload(PatientModel.telecoms).selectinload(PatientTelecom.period),
            selectinload(PatientModel.addresses).selectinload(PatientAddress.lines),
            selectinload(PatientModel.addresses).selectinload(PatientAddress.period),
            selectinload(PatientModel.marital_status).selectinload(
                PatientMaritalStatus.codings
            ),
            selectinload(PatientModel.photos),
            selectinload(PatientModel.contacts)
            .selectinload(PatientContact.relationship_codes)
            .selectinload(PatientContactRelationship.codings),
            selectinload(PatientModel.contacts).selectinload(
                PatientContact.telecoms
            ),
            selectinload(PatientModel.contacts)
            .selectinload(PatientContact.name)
            .selectinload(PatientContactHumanName.given),
            selectinload(PatientModel.contacts)
            .selectinload(PatientContact.name)
            .selectinload(PatientContactHumanName.prefix),
            selectinload(PatientModel.contacts)
            .selectinload(PatientContact.name)
            .selectinload(PatientContactHumanName.suffix),
            selectinload(PatientModel.contacts)
            .selectinload(PatientContact.name)
            .selectinload(PatientContactHumanName.period),
            selectinload(PatientModel.contacts).selectinload(PatientContact.address),
            selectinload(PatientModel.contacts).selectinload(PatientContact.period),
            selectinload(PatientModel.communications)
            .selectinload(PatientCommunication.language)
            .selectinload(PatientCommunicationLanguage.codings),
            selectinload(PatientModel.general_practitioners),
            selectinload(PatientModel.links),
        ]

    # ── CREATE ────────────────────────────────────────────────────────

    async def create(self, patient: PatientCreateSchema) -> PatientResponseSchema:
        async with self.session_factory() as session:
            db_patient = PatientModel(
                active=patient.active,
                gender=patient.gender,
                birth_date=patient.birthDate,
                deceased_boolean=patient.deceasedBoolean,
                deceased_dateTime=patient.deceasedDateTime,
                multiple_birth_boolean=patient.multipleBirthBoolean,
                multiple_birth_integer=patient.multipleBirthInteger,
                managing_organization_id=patient.managingOrganizationId,
                orgId=1,  # TODO: derive from auth context
            )

            # Identifiers
            self._build_identifiers(db_patient, patient.identifier)

            # Names
            self._build_names(db_patient, patient.name)

            # Telecoms
            self._build_telecoms(db_patient, patient.telecom)

            # Addresses
            self._build_addresses(db_patient, patient.address)

            # Marital Status
            self._build_marital_status(db_patient, patient.maritalStatus)

            # Photos
            self._build_photos(db_patient, patient.photo)

            # Contacts
            self._build_contacts(db_patient, patient.contact)

            # Communications
            self._build_communications(db_patient, patient.communication)

            # General Practitioners
            self._build_general_practitioners(
                db_patient, patient.generalPractitioner
            )

            # Links
            self._build_links(db_patient, patient.link)

            try:
                session.add(db_patient)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

            return await self.get(db_patient.id)

    # ── UPDATE ────────────────────────────────────────────────────────

    async def update(
        self, patient_id: int, patient: PatientCreateSchema
    ) -> Optional[PatientResponseSchema]:
        async with self.session_factory() as session:
            stmt = (
                select(PatientModel)
                .where(PatientModel.id == patient_id)
                .options(*self._load_options())
            )
            result = await session.execute(stmt)
            db_patient = result.scalars().first()

            if not db_patient:
                return None

            # Update scalar fields
            db_patient.active = patient.active
            db_patient.gender = patient.gender
            db_patient.birth_date = patient.birthDate
            db_patient.deceased_boolean = patient.deceasedBoolean
            db_patient.deceased_dateTime = patient.deceasedDateTime
            db_patient.multiple_birth_boolean = patient.multipleBirthBoolean
            db_patient.multiple_birth_integer = patient.multipleBirthInteger
            db_patient.managing_organization_id = patient.managingOrganizationId

            # Clear and rebuild all child collections
            db_patient.identifiers.clear()
            db_patient.names.clear()
            db_patient.telecoms.clear()
            db_patient.addresses.clear()
            db_patient.photos.clear()
            db_patient.contacts.clear()
            db_patient.communications.clear()
            db_patient.general_practitioners.clear()
            db_patient.links.clear()

            # Clear one-to-one (marital_status)
            if db_patient.marital_status:
                await session.delete(db_patient.marital_status)
                db_patient.marital_status = None

            # Rebuild all children
            self._build_identifiers(db_patient, patient.identifier)
            self._build_names(db_patient, patient.name)
            self._build_telecoms(db_patient, patient.telecom)
            self._build_addresses(db_patient, patient.address)
            self._build_marital_status(db_patient, patient.maritalStatus)
            self._build_photos(db_patient, patient.photo)
            self._build_contacts(db_patient, patient.contact)
            self._build_communications(db_patient, patient.communication)
            self._build_general_practitioners(
                db_patient, patient.generalPractitioner
            )
            self._build_links(db_patient, patient.link)

            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

            return await self.get(patient_id)

    # ── GET ───────────────────────────────────────────────────────────

    async def get(self, patient_id: int) -> Optional[PatientResponseSchema]:
        async with self.session_factory() as session:
            stmt = (
                select(PatientModel)
                .where(PatientModel.id == patient_id)
                .options(*self._load_options())
            )
            result = await session.execute(stmt)
            db_patient = result.scalars().first()

            if not db_patient:
                return None

            return self._map_to_fhir(db_patient)

    # ── LIST ──────────────────────────────────────────────────────────

    async def list(self) -> List[PatientResponseSchema]:
        async with self.session_factory() as session:
            stmt = select(PatientModel).options(*self._load_options())
            result = await session.execute(stmt)
            db_patients = result.scalars().all()
            return [self._map_to_fhir(p) for p in db_patients]

    # ── DELETE ────────────────────────────────────────────────────────

    async def delete(self, patient_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(PatientModel).where(PatientModel.id == patient_id)
            result = await session.execute(stmt)
            db_patient = result.scalars().first()

            if not db_patient:
                return False

            try:
                await session.delete(db_patient)
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise

    # ══════════════════════════════════════════════════════════════════
    # Builder helpers — Pydantic schema → DB child models
    # ══════════════════════════════════════════════════════════════════

    @staticmethod
    def _build_identifiers(db_patient: PatientModel, identifiers):
        if not identifiers:
            return
        for ident in identifiers:
            db_ident = PatientIdentifier(
                use=ident.use,
                system=ident.system,
                value=ident.value,
                assigner=ident.assigner,
                patient=db_patient,
            )
            # type (CodeableConcept)
            if ident.type:
                db_type = IdentifierType(
                    text=ident.type.text,
                    identifier=db_ident,
                )
                if ident.type.coding:
                    for c in ident.type.coding:
                        IdentifierTypeCoding(
                            system=c.system,
                            version=c.version,
                            code=c.code,
                            display=c.display,
                            user_selected=c.userSelected,
                            type=db_type,
                        )
            # period
            if ident.period:
                PatientIdentifierPeriod(
                    start=ident.period.start,
                    end=ident.period.end,
                    identifier=db_ident,
                )

    @staticmethod
    def _build_names(db_patient: PatientModel, names):
        if not names:
            return
        for name in names:
            db_name = PatientName(
                use=name.use,
                text=name.text,
                family=name.family,
                patient=db_patient,
            )
            if name.given:
                for g in name.given:
                    PatientNameGiven(value=g, human_name=db_name)
            if name.prefix:
                for p in name.prefix:
                    PatientNamePrefix(value=p, human_name=db_name)
            if name.suffix:
                for s in name.suffix:
                    PatientNameSuffix(value=s, human_name=db_name)
            if name.period:
                PatientNamePeriod(
                    start=name.period.start,
                    end=name.period.end,
                    name=db_name,
                )

    @staticmethod
    def _build_telecoms(db_patient: PatientModel, telecoms):
        if not telecoms:
            return
        for tc in telecoms:
            db_tc = PatientTelecom(
                system=tc.system,
                value=tc.value,
                use=tc.use,
                rank=tc.rank,
                patient=db_patient,
            )
            if tc.period:
                PatientTelecomPeriod(
                    start=tc.period.start,
                    end=tc.period.end,
                    telecom=db_tc,
                )

    @staticmethod
    def _build_addresses(db_patient: PatientModel, addresses):
        if not addresses:
            return
        for addr in addresses:
            db_addr = PatientAddress(
                use=addr.use,
                type=addr.type,
                text=addr.text,
                city=addr.city,
                district=addr.district,
                state=addr.state,
                postal_code=addr.postalCode,
                country=addr.country,
                patient=db_patient,
            )
            if addr.line:
                for ln in addr.line:
                    PatientAddressLine(value=ln, address=db_addr)
            if addr.period:
                PatientAddressPeriod(
                    start=addr.period.start,
                    end=addr.period.end,
                    address=db_addr,
                )

    @staticmethod
    def _build_marital_status(db_patient: PatientModel, marital_status):
        if not marital_status:
            return
        db_ms = PatientMaritalStatus(
            text=marital_status.text,
            patient=db_patient,
        )
        if marital_status.coding:
            for c in marital_status.coding:
                PatientMaritalStatusCoding(
                    system=c.system,
                    version=c.version,
                    code=c.code,
                    display=c.display,
                    user_selected=c.userSelected,
                    marital_status=db_ms,
                )

    @staticmethod
    def _build_photos(db_patient: PatientModel, photos):
        if not photos:
            return
        for photo in photos:
            # Decode base64 data if present
            raw_data = None
            if photo.data:
                try:
                    raw_data = base64.b64decode(photo.data)
                except Exception:
                    raw_data = None

            PatientPhoto(
                content_type=photo.contentType,
                language=photo.language,
                data=raw_data,
                url=photo.url,
                size=photo.size,
                hash=photo.hash,
                title=photo.title,
                creation=photo.creation,
                patient=db_patient,
            )

    @staticmethod
    def _build_contacts(db_patient: PatientModel, contacts):
        if not contacts:
            return
        for contact in contacts:
            db_contact = PatientContact(
                gender=contact.gender,
                organization_id=None,
                patient=db_patient,
            )

            # relationship[] (CodeableConcept[])
            if contact.relationship:
                for rel in contact.relationship:
                    db_rel = PatientContactRelationship(
                        text=rel.text,
                        contact=db_contact,
                    )
                    if rel.coding:
                        for c in rel.coding:
                            PatientContactRelationshipCoding(
                                system=c.system,
                                version=c.version,
                                code=c.code,
                                display=c.display,
                                relationship=db_rel,
                            )

            # name (HumanName)
            if contact.name:
                db_cn = PatientContactHumanName(
                    use=contact.name.use,
                    text=contact.name.text,
                    family=contact.name.family,
                    contact=db_contact,
                )
                if contact.name.given:
                    for g in contact.name.given:
                        PatientContactHumanNameGiven(value=g, name=db_cn)
                if contact.name.prefix:
                    for p in contact.name.prefix:
                        PatientContactHumanNamePrefix(value=p, name=db_cn)
                if contact.name.suffix:
                    for s in contact.name.suffix:
                        PatientContactHumanNameSuffix(value=s, name=db_cn)
                if contact.name.period:
                    PatientContactHumanNamePeriod(
                        start=contact.name.period.start,
                        end=contact.name.period.end,
                        name=db_cn,
                    )

            # telecom[]
            if contact.telecom:
                for tc in contact.telecom:
                    PatientContactTelecom(
                        system=tc.system,
                        value=tc.value,
                        use=tc.use,
                        rank=tc.rank,
                        contact=db_contact,
                    )

            # address
            if contact.address:
                PatientContactAddress(
                    text=contact.address.text,
                    city=contact.address.city,
                    state=contact.address.state,
                    postal_code=contact.address.postalCode,
                    country=contact.address.country,
                    contact=db_contact,
                )

            # period
            if contact.period:
                PatientContactPeriod(
                    start=contact.period.start,
                    end=contact.period.end,
                    contact=db_contact,
                )

    @staticmethod
    def _build_communications(db_patient: PatientModel, communications):
        if not communications:
            return
        for comm in communications:
            db_comm = PatientCommunication(
                preferred=comm.preferred,
                patient=db_patient,
            )
            # language (CodeableConcept — required)
            db_lang = PatientCommunicationLanguage(
                text=comm.language.text,
                communication=db_comm,
            )
            if comm.language.coding:
                for c in comm.language.coding:
                    PatientCommunicationLanguageCoding(
                        system=c.system,
                        version=c.version,
                        code=c.code,
                        display=c.display,
                        user_selected=c.userSelected,
                        language=db_lang,
                    )

    @staticmethod
    def _build_general_practitioners(db_patient: PatientModel, gps):
        if not gps:
            return
        for gp in gps:
            PatientGeneralPractitioner(
                ref_type=gp.refType,
                ref_id=gp.refId,
                patient=db_patient,
            )

    @staticmethod
    def _build_links(db_patient: PatientModel, links):
        if not links:
            return
        for link in links:
            PatientLink(
                other_ref_type=link.other_ref_type,
                other_ref_id=link.other_ref_id,
                type=link.type,
                patient=db_patient,
            )

    # ══════════════════════════════════════════════════════════════════
    # Mapper — DB model → PatientResponseSchema
    # ══════════════════════════════════════════════════════════════════

    def _map_to_fhir(self, db_patient: PatientModel) -> PatientResponseSchema:
        data = {
            "resourceType": "Patient",
            "id": str(db_patient.id),
            "active": db_patient.active,
            "gender": db_patient.gender,
            "birthDate": db_patient.birth_date,
            "deceasedBoolean": db_patient.deceased_boolean,
            "deceasedDateTime": db_patient.deceased_dateTime,
            "multipleBirthBoolean": db_patient.multiple_birth_boolean,
            "multipleBirthInteger": db_patient.multiple_birth_integer,
        }

        # identifier[]
        if db_patient.identifiers:
            data["identifier"] = [
                _map_identifier(ident) for ident in db_patient.identifiers
            ]

        # name[]
        if db_patient.names:
            data["name"] = [_map_name(n) for n in db_patient.names]

        # telecom[]
        if db_patient.telecoms:
            data["telecom"] = [_map_telecom(tc) for tc in db_patient.telecoms]

        # address[]
        if db_patient.addresses:
            data["address"] = [_map_address(a) for a in db_patient.addresses]

        # maritalStatus
        if db_patient.marital_status:
            data["maritalStatus"] = _map_codeable_concept(db_patient.marital_status)

        # photo[]
        if db_patient.photos:
            data["photo"] = [_map_photo(p) for p in db_patient.photos]

        # contact[]
        if db_patient.contacts:
            data["contact"] = [_map_contact(c) for c in db_patient.contacts]

        # communication[]
        if db_patient.communications:
            data["communication"] = [
                _map_communication(c) for c in db_patient.communications
            ]

        # generalPractitioner[]
        if db_patient.general_practitioners:
            data["generalPractitioner"] = [
                _build_reference(gp.ref_type, gp.ref_id)
                for gp in db_patient.general_practitioners
            ]

        # managingOrganization
        if db_patient.managing_organization_id:
            data["managingOrganization"] = _build_reference(
                "Organization", db_patient.managing_organization_id
            )

        # link[]
        if db_patient.links:
            data["link"] = [_map_link(lk) for lk in db_patient.links]

        # Strip None values
        data = {k: v for k, v in data.items() if v is not None}

        try:
            return PatientResponseSchema.model_validate(data)
        except ValidationError as e:
            raise InfrastructureError(
                message="Failed to map database entity to FHIR Patient",
                cause=e,
            )


# ══════════════════════════════════════════════════════════════════════
# Module-level mapping helpers
# ══════════════════════════════════════════════════════════════════════


def _build_reference(resource_type, resource_id) -> dict:
    return {
        "reference": f"{resource_type}/{resource_id}",
        "type": resource_type,
    }


def _map_coding(db_coding) -> dict:
    d = {}
    if db_coding.system:
        d["system"] = db_coding.system
    if db_coding.version:
        d["version"] = db_coding.version
    if db_coding.code:
        d["code"] = db_coding.code
    if db_coding.display:
        d["display"] = db_coding.display
    if hasattr(db_coding, "user_selected") and db_coding.user_selected is not None:
        d["userSelected"] = db_coding.user_selected
    return d


def _map_codeable_concept(db_cc) -> dict:
    d = {}
    if db_cc.text:
        d["text"] = db_cc.text
    if db_cc.codings:
        d["coding"] = [_map_coding(c) for c in db_cc.codings]
    return d


def _map_period(db_period) -> Optional[dict]:
    if not db_period:
        return None
    d = {}
    if db_period.start:
        d["start"] = db_period.start.isoformat() if hasattr(db_period.start, "isoformat") else db_period.start
    if db_period.end:
        d["end"] = db_period.end.isoformat() if hasattr(db_period.end, "isoformat") else db_period.end
    return d if d else None


def _map_identifier(db_ident) -> dict:
    d = {}
    if db_ident.use:
        d["use"] = db_ident.use
    if db_ident.system:
        d["system"] = db_ident.system
    if db_ident.value:
        d["value"] = db_ident.value
    if db_ident.assigner:
        d["assigner"] = db_ident.assigner
    if db_ident.type:
        d["type"] = _map_codeable_concept(db_ident.type)
    period = _map_period(db_ident.period)
    if period:
        d["period"] = period
    return d


def _map_name(db_name) -> dict:
    d = {}
    if db_name.use:
        d["use"] = db_name.use
    if db_name.text:
        d["text"] = db_name.text
    if db_name.family:
        d["family"] = db_name.family
    if db_name.given:
        d["given"] = [g.value for g in db_name.given]
    if db_name.prefix:
        d["prefix"] = [p.value for p in db_name.prefix]
    if db_name.suffix:
        d["suffix"] = [s.value for s in db_name.suffix]
    period = _map_period(db_name.period)
    if period:
        d["period"] = period
    return d


def _map_telecom(db_tc) -> dict:
    d = {}
    if db_tc.system:
        d["system"] = db_tc.system
    if db_tc.value:
        d["value"] = db_tc.value
    if db_tc.use:
        d["use"] = db_tc.use
    if db_tc.rank is not None:
        d["rank"] = db_tc.rank
    period = _map_period(db_tc.period)
    if period:
        d["period"] = period
    return d


def _map_address(db_addr) -> dict:
    d = {}
    if db_addr.use:
        d["use"] = db_addr.use
    if db_addr.type:
        d["type"] = db_addr.type
    if db_addr.text:
        d["text"] = db_addr.text
    if db_addr.lines:
        d["line"] = [ln.value for ln in db_addr.lines]
    if db_addr.city:
        d["city"] = db_addr.city
    if db_addr.district:
        d["district"] = db_addr.district
    if db_addr.state:
        d["state"] = db_addr.state
    if db_addr.postal_code:
        d["postalCode"] = db_addr.postal_code
    if db_addr.country:
        d["country"] = db_addr.country
    period = _map_period(db_addr.period)
    if period:
        d["period"] = period
    return d


def _map_photo(db_photo) -> dict:
    d = {}
    if db_photo.content_type:
        d["contentType"] = db_photo.content_type
    if db_photo.language:
        d["language"] = db_photo.language
    if db_photo.data:
        d["data"] = base64.b64encode(db_photo.data).decode("utf-8")
    if db_photo.url:
        d["url"] = db_photo.url
    if db_photo.size is not None:
        d["size"] = db_photo.size
    if db_photo.hash:
        d["hash"] = db_photo.hash
    if db_photo.title:
        d["title"] = db_photo.title
    if db_photo.creation:
        d["creation"] = db_photo.creation.isoformat() if hasattr(db_photo.creation, "isoformat") else db_photo.creation
    return d


def _map_contact(db_contact) -> dict:
    d = {}
    if db_contact.relationship_codes:
        d["relationship"] = [
            _map_codeable_concept(r) for r in db_contact.relationship_codes
        ]
    if db_contact.name:
        d["name"] = _map_contact_name(db_contact.name)
    if db_contact.telecoms:
        d["telecom"] = [
            {
                k: v
                for k, v in {
                    "system": tc.system,
                    "value": tc.value,
                    "use": tc.use,
                    "rank": tc.rank,
                }.items()
                if v is not None
            }
            for tc in db_contact.telecoms
        ]
    if db_contact.address:
        addr = db_contact.address
        d["address"] = {
            k: v
            for k, v in {
                "text": addr.text,
                "city": addr.city,
                "state": addr.state,
                "postalCode": addr.postal_code,
                "country": addr.country,
            }.items()
            if v is not None
        }
    if db_contact.gender:
        d["gender"] = db_contact.gender
    if db_contact.organization_id:
        d["organization"] = _build_reference(
            "Organization", db_contact.organization_id
        )
    period = _map_period(db_contact.period)
    if period:
        d["period"] = period
    return d


def _map_contact_name(db_name) -> dict:
    d = {}
    if db_name.use:
        d["use"] = db_name.use
    if db_name.text:
        d["text"] = db_name.text
    if db_name.family:
        d["family"] = db_name.family
    if db_name.given:
        d["given"] = [g.value for g in db_name.given]
    if db_name.prefix:
        d["prefix"] = [p.value for p in db_name.prefix]
    if db_name.suffix:
        d["suffix"] = [s.value for s in db_name.suffix]
    period = _map_period(db_name.period)
    if period:
        d["period"] = period
    return d


def _map_communication(db_comm) -> dict:
    d = {}
    if db_comm.language:
        d["language"] = _map_codeable_concept(db_comm.language)
    if db_comm.preferred is not None:
        d["preferred"] = db_comm.preferred
    return d


def _map_link(db_link) -> dict:
    return {
        "other": _build_reference(db_link.other_ref_type, db_link.other_ref_id),
        "type": db_link.type,
    }
