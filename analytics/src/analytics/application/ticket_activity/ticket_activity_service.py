from analytics.application.ticket_activity.dto.ticket_activity_dto import (
    TicketActivityResponseDTO,
)
from analytics.application.ticket_activity.ticket_activity_service_interface import (
    ITicketActivityService,
)
from analytics.application.interfaces.ticket_activity_repository_interface import (
    ITicketActivityRepository,
)


class TicketActivityService(ITicketActivityService):
    def __init__(
        self,
        ticket_activity_repository: ITicketActivityRepository,
    ):
        self._ticket_activity_repository = ticket_activity_repository

    async def get_activities_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[TicketActivityResponseDTO]:
        entities = await self._ticket_activity_repository.get_by_ticket_id(ticket_id)
        return [
            TicketActivityResponseDTO(
                id=e.id,
                source_event_id=e.source_event_id,
                ticket_id=e.ticket_id,
                assignment_id=e.assignment_id,
                actor_id=e.actor_id,
                agent_id=e.agent_id,
                team_id=e.team_id,
                activity_type=e.activity_type,
                occurred_at=e.occurred_at,
            )
            for e in entities
        ]
