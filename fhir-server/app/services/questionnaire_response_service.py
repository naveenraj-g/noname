from fhir.resources.questionnaireresponse import QuestionnaireResponse
from app.repository.questionnaire_response_repository import QuestionnaireResponseRepository


class QuestionnaireResponseService:
    def __init__(self, repository: QuestionnaireResponseRepository):
        self.repository = repository

    async def create_questionnaire_response(self, data: dict) -> QuestionnaireResponse:
        data.pop("id", None)
        return await self.repository.create(data)

    async def update_questionnaire_response(self, qr_id: int, data: dict) -> QuestionnaireResponse:
        data.pop("id", None)
        return await self.repository.update(qr_id, data)

    async def get_questionnaire_response(self, qr_id: int) -> QuestionnaireResponse:
        return await self.repository.get(qr_id)

    async def list_questionnaire_responses(self) -> list[QuestionnaireResponse]:
        return await self.repository.list()

    async def delete_questionnaire_response(self, qr_id: int) -> bool:
        return await self.repository.delete(qr_id)
