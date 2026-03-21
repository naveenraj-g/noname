from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from fhir.resources.questionnaireresponse import QuestionnaireResponse

from app.models.questionnaire_response import (
    QuestionnaireResponseModel,
    QuestionnaireResponseItemModel,
    QuestionnaireResponseAnswerModel,
)


class QuestionnaireResponseRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(self, data: dict) -> QuestionnaireResponse:
        async with self.session_factory() as session:
            db_qr = self._build_model(data)
            session.add(db_qr)
            await session.commit()
            await session.refresh(db_qr)
            return await self.get(db_qr.id)

    async def update(self, qr_id: int, data: dict) -> Optional[QuestionnaireResponse]:
        async with self.session_factory() as session:
            stmt = (
                select(QuestionnaireResponseModel)
                .where(QuestionnaireResponseModel.id == qr_id)
                .options(selectinload(QuestionnaireResponseModel.items))
            )
            result = await session.execute(stmt)
            db_qr = result.scalars().first()

            if not db_qr:
                return None

            # Delete all existing items (cascade deletes answers and sub_items)
            for item in db_qr.items:
                await session.delete(item)
            await session.flush()

            # Update scalar fields
            db_qr.questionnaire = data.get("questionnaire", db_qr.questionnaire)
            db_qr.status = data.get("status", db_qr.status)
            db_qr.subject_reference = self._ref(data.get("subject"))
            db_qr.subject_display = self._ref_display(data.get("subject"))
            db_qr.encounter_reference = self._ref(data.get("encounter"))
            db_qr.authored = self._parse_dt(data.get("authored"))
            db_qr.author_reference = self._ref(data.get("author"))
            db_qr.author_display = self._ref_display(data.get("author"))
            db_qr.source_reference = self._ref(data.get("source"))
            db_qr.source_display = self._ref_display(data.get("source"))

            # Re-create items
            for item_data in data.get("item", []):
                db_qr.items.append(self._build_item(item_data, qr_id))

            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise

            return await self.get(qr_id)

    async def get(self, qr_id: int) -> Optional[QuestionnaireResponse]:
        async with self.session_factory() as session:
            db_qr = await self._load(session, qr_id)
            if not db_qr:
                return None
            return self._map_to_fhir(db_qr)

    async def list(self) -> List[QuestionnaireResponse]:
        async with self.session_factory() as session:
            stmt = select(QuestionnaireResponseModel).options(
                selectinload(QuestionnaireResponseModel.items).selectinload(
                    QuestionnaireResponseItemModel.answers
                ),
                selectinload(QuestionnaireResponseModel.items).selectinload(
                    QuestionnaireResponseItemModel.sub_items
                ).selectinload(QuestionnaireResponseItemModel.answers),
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._map_to_fhir(r) for r in rows]

    async def delete(self, qr_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(QuestionnaireResponseModel).where(QuestionnaireResponseModel.id == qr_id)
            result = await session.execute(stmt)
            db_qr = result.scalars().first()

            if not db_qr:
                return False

            try:
                await session.delete(db_qr)
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                raise

    # ── Internal helpers ─────────────────────────────────────────────────────

    async def _load(self, session: AsyncSession, qr_id: int) -> Optional[QuestionnaireResponseModel]:
        stmt = (
            select(QuestionnaireResponseModel)
            .where(QuestionnaireResponseModel.id == qr_id)
            .options(
                selectinload(QuestionnaireResponseModel.items).selectinload(
                    QuestionnaireResponseItemModel.answers
                ),
                selectinload(QuestionnaireResponseModel.items).selectinload(
                    QuestionnaireResponseItemModel.sub_items
                ).selectinload(QuestionnaireResponseItemModel.answers),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    # ── Build model from dict ─────────────────────────────────────────────────

    def _build_model(self, data: dict) -> QuestionnaireResponseModel:
        db_qr = QuestionnaireResponseModel(
            questionnaire=data.get("questionnaire"),
            status=data.get("status"),
            subject_reference=self._ref(data.get("subject")),
            subject_display=self._ref_display(data.get("subject")),
            encounter_reference=self._ref(data.get("encounter")),
            authored=self._parse_dt(data.get("authored")),
            author_reference=self._ref(data.get("author")),
            author_display=self._ref_display(data.get("author")),
            source_reference=self._ref(data.get("source")),
            source_display=self._ref_display(data.get("source")),
        )
        for item_data in data.get("item", []):
            db_qr.items.append(self._build_item(item_data, None))
        return db_qr

    def _build_item(
        self,
        data: dict,
        response_id: Optional[int],
        parent_item_id: Optional[int] = None,
    ) -> QuestionnaireResponseItemModel:
        db_item = QuestionnaireResponseItemModel(
            response_id=response_id,
            parent_item_id=parent_item_id,
            link_id=data.get("linkId"),
            text=data.get("text"),
            definition=data.get("definition"),
        )
        for answer_data in data.get("answer", []):
            db_item.answers.append(self._build_answer(answer_data))

        for sub_item_data in data.get("item", []):
            db_item.sub_items.append(self._build_item(sub_item_data, response_id))

        return db_item

    def _build_answer(self, data: dict) -> QuestionnaireResponseAnswerModel:
        db_answer = QuestionnaireResponseAnswerModel(value_type="unknown")

        if data.get("valueBoolean") is not None:
            db_answer.value_type = "boolean"
            db_answer.value_boolean = data["valueBoolean"]
        elif data.get("valueDecimal") is not None:
            db_answer.value_type = "decimal"
            db_answer.value_decimal = data["valueDecimal"]
        elif data.get("valueInteger") is not None:
            db_answer.value_type = "integer"
            db_answer.value_integer = data["valueInteger"]
        elif data.get("valueDate") is not None:
            db_answer.value_type = "date"
            db_answer.value_string = str(data["valueDate"])
        elif data.get("valueDateTime") is not None:
            db_answer.value_type = "dateTime"
            db_answer.value_datetime = self._parse_dt(data["valueDateTime"])
        elif data.get("valueTime") is not None:
            db_answer.value_type = "time"
            db_answer.value_string = str(data["valueTime"])
        elif data.get("valueString") is not None:
            db_answer.value_type = "string"
            db_answer.value_string = data["valueString"]
        elif data.get("valueUri") is not None:
            db_answer.value_type = "uri"
            db_answer.value_string = data["valueUri"]
        elif data.get("valueCoding") is not None:
            db_answer.value_type = "coding"
            coding = data["valueCoding"]
            if isinstance(coding, dict):
                db_answer.value_coding_system = coding.get("system")
                db_answer.value_coding_code = coding.get("code")
                db_answer.value_coding_display = coding.get("display")
        elif data.get("valueQuantity") is not None:
            db_answer.value_type = "quantity"
            qty = data["valueQuantity"]
            if isinstance(qty, dict):
                db_answer.value_quantity_value = qty.get("value")
                db_answer.value_quantity_unit = qty.get("unit")
                db_answer.value_quantity_system = qty.get("system")
                db_answer.value_quantity_code = qty.get("code")
        elif data.get("valueReference") is not None:
            db_answer.value_type = "reference"
            ref = data["valueReference"]
            if isinstance(ref, dict):
                db_answer.value_reference = ref.get("reference")
                db_answer.value_reference_display = ref.get("display")

        return db_answer

    # ── Map DB model to FHIR ──────────────────────────────────────────────────

    def _map_to_fhir(self, db: QuestionnaireResponseModel) -> QuestionnaireResponse:
        data: dict = {
            "resourceType": "QuestionnaireResponse",
            "id": str(db.id),
            "questionnaire": db.questionnaire,
            "status": db.status,
        }

        if db.subject_reference:
            data["subject"] = {"reference": db.subject_reference}
            if db.subject_display:
                data["subject"]["display"] = db.subject_display

        if db.encounter_reference:
            data["encounter"] = {"reference": db.encounter_reference}

        if db.authored:
            data["authored"] = db.authored.isoformat()

        if db.author_reference:
            data["author"] = {"reference": db.author_reference}
            if db.author_display:
                data["author"]["display"] = db.author_display

        if db.source_reference:
            data["source"] = {"reference": db.source_reference}
            if db.source_display:
                data["source"]["display"] = db.source_display

        # Build top-level items (those with no parent)
        top_level = [i for i in db.items if i.parent_item_id is None]
        if top_level:
            data["item"] = [self._map_item(i) for i in top_level]

        return QuestionnaireResponse.model_validate(data)

    def _map_item(self, db_item: QuestionnaireResponseItemModel) -> dict:
        item_data: dict = {"linkId": db_item.link_id}

        if db_item.text:
            item_data["text"] = db_item.text
        if db_item.definition:
            item_data["definition"] = db_item.definition

        if db_item.answers:
            item_data["answer"] = [self._map_answer(a) for a in db_item.answers]

        if db_item.sub_items:
            item_data["item"] = [self._map_item(sub) for sub in db_item.sub_items]

        return item_data

    def _map_answer(self, db_answer: QuestionnaireResponseAnswerModel) -> dict:
        vt = db_answer.value_type
        answer_data: dict = {}

        if vt == "boolean":
            answer_data["valueBoolean"] = db_answer.value_boolean
        elif vt == "decimal":
            answer_data["valueDecimal"] = db_answer.value_decimal
        elif vt == "integer":
            answer_data["valueInteger"] = db_answer.value_integer
        elif vt == "date":
            answer_data["valueDate"] = db_answer.value_string
        elif vt == "dateTime":
            answer_data["valueDateTime"] = db_answer.value_datetime.isoformat() if db_answer.value_datetime else None
        elif vt == "time":
            answer_data["valueTime"] = db_answer.value_string
        elif vt == "string":
            answer_data["valueString"] = db_answer.value_string
        elif vt == "uri":
            answer_data["valueUri"] = db_answer.value_string
        elif vt == "coding":
            answer_data["valueCoding"] = {
                "system": db_answer.value_coding_system,
                "code": db_answer.value_coding_code,
                "display": db_answer.value_coding_display,
            }
        elif vt == "quantity":
            answer_data["valueQuantity"] = {
                "value": db_answer.value_quantity_value,
                "unit": db_answer.value_quantity_unit,
                "system": db_answer.value_quantity_system,
                "code": db_answer.value_quantity_code,
            }
        elif vt == "reference":
            answer_data["valueReference"] = {"reference": db_answer.value_reference}
            if db_answer.value_reference_display:
                answer_data["valueReference"]["display"] = db_answer.value_reference_display

        return answer_data

    # ── Static helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _parse_dt(value) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return None

    @staticmethod
    def _ref(ref_data) -> Optional[str]:
        if isinstance(ref_data, dict):
            return ref_data.get("reference")
        return None

    @staticmethod
    def _ref_display(ref_data) -> Optional[str]:
        if isinstance(ref_data, dict):
            return ref_data.get("display")
        return None
