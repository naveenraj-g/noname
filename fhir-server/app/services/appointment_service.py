from fhir.resources.appointment import Appointment
from app.repository.appointment_repository import AppointmentRepository


class AppointmentService:
    def __init__(self, repository: AppointmentRepository):
        self.repository = repository

    async def create_appointment(self, appointment_data: dict) -> Appointment:
        appointment_data.pop("id", None)
        return await self.repository.create(appointment_data)

    async def update_appointment(self, appointment_id: int, appointment_data: dict) -> Appointment:
        appointment_data.pop("id", None)
        return await self.repository.update(appointment_id, appointment_data)

    async def get_appointment(self, appointment_id: int) -> Appointment:
        return await self.repository.get(appointment_id)

    async def list_appointments(self) -> list[Appointment]:
        return await self.repository.list()

    async def delete_appointment(self, appointment_id: int) -> bool:
        return await self.repository.delete(appointment_id)
