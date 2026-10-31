from typing import Any

from src.infrastructure.messaging.kafka.events.ticket.ticket_assigned_event import (
    TicketAssignedEvent,
)
from src.infrastructure.messaging.kafka.handlers.ticket.shared import (
    process_notifications,
)


def build_message(event: TicketAssignedEvent) -> str:
    return (
        "A ticket has been assigned.\n\n"
        f"Ticket ID: {event.subject.id}\n"
        f"Assignment type: {event.data.assignment_type}\n"
        f"Assigned team ID: {event.data.team_id}\n"
        f"Assigned agent ID: {event.data.agent_id}\n"
        f"Assigned at: {event.occurred_at.isoformat()}"
    )


async def handle(payload: dict[str, Any]) -> None:
    event = TicketAssignedEvent.model_validate(payload)

    await process_notifications(
        event_id=event.event_id,
        event_type=event.event_type,
        recipients=[
            str(recipient.email)
            for recipient in event.data.recipients
        ],
        subject=f"[Ticket Assigned] {event.subject.id}",
        message=build_message(event),
    )
