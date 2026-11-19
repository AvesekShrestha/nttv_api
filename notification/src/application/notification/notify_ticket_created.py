from datetime import datetime

from src.application.dto.inbox_notification_dto import (
    InboxRecipient,
    RecordTicketEventRequest,
)
from src.application.interfaces.inbox_repository_interface import (
    InboxRepositoryInterface,
)
from src.application.shared.ticket_client_interface import (
    TicketClientInterface,
)


class NotifyTicketCreated:
    def __init__(
        self,
        ticket_client: TicketClientInterface,
        inbox_repository: InboxRepositoryInterface,
    ):
        self.ticket_client = ticket_client
        self.inbox_repository = inbox_repository

    async def execute(
        self,
        *,
        event_id: str,
        occurred_at: datetime,
        ticket_id: str,
        source_topic: str = "ticket.events",
    ) -> bool:
        ticket = await self.ticket_client.get_ticket(ticket_id)

        recipient = InboxRecipient(
            user_id=ticket.created_by,
            title="Ticket created",
            message=(
                "Your ticket has been created.\n\n"
                f"Ticket: {ticket.title}\n"
                f"Ticket ID: {ticket.id}\n"
                f"Created at: {occurred_at.isoformat()}"
            ),
            requires_action=False,
            send_email=False,
        )

        return await self.inbox_repository.record_event(
            RecordTicketEventRequest(
                source_topic=source_topic,
                event_id=event_id,
                event_type="ticket.created",
                occurred_at=occurred_at,
                ticket_id=ticket.id,
                recipients=(recipient,),
            )
        )
