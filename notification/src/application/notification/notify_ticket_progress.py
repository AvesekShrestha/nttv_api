from datetime import datetime
from typing import Literal

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


TicketProgressEventType = Literal[
    "ticket.acknowledged",
    "ticket.completed",
]


class NotifyTicketProgress:
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
        event_type: TicketProgressEventType,
        occurred_at: datetime,
        ticket_id: str,
        actor_user_id: str,
        source_topic: str = "ticket.events",
    ) -> bool:
        if event_type == "ticket.acknowledged":
            title = "Ticket acknowledged"
            introduction = "Your ticket has been acknowledged."

        elif event_type == "ticket.completed":
            title = "Ticket completed"
            introduction = (
                "Your ticket has been marked as completed."
            )

        else:
            raise ValueError(
                "Unsupported ticket progress event type"
            )

        if not actor_user_id.strip():
            raise ValueError("Actor user ID is required")

        ticket = await self.ticket_client.get_ticket(ticket_id)

        recipient = InboxRecipient(
            user_id=ticket.created_by,
            title=title,
            message=(
                f"{introduction}\n\n"
                f"Ticket: {ticket.title}\n"
                f"Ticket ID: {ticket.id}\n"
                f"Agent ID: {actor_user_id}\n"
                f"Updated at: {occurred_at.isoformat()}"
            ),
            requires_action=False,
            send_email=False,
        )

        return await self.inbox_repository.record_event(
            RecordTicketEventRequest(
                source_topic=source_topic,
                event_id=event_id,
                event_type=event_type,
                occurred_at=occurred_at,
                ticket_id=ticket.id,
                recipients=(recipient,),
            )
        )
