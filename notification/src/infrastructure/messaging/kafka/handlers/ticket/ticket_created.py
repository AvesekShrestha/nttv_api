
from src.infrastructure.messaging.kafka.events.ticket.ticket_created_event import (
    TicketCreatedEvent,
)
from src.infrastructure.messaging.kafka.handlers.ticket.shared import (
    process_notifications,
)


def build_message(event: TicketCreatedEvent) -> str:
    return (
        "A new ticket has been created.\n\n"
        f"Ticket ID: {event.subject.id}\n"
        f"Title: {event.data.title}\n"
        f"Category: {event.data.category}\n"
        f"Priority: {event.data.priority}\n"
        f"Support level: {event.data.level}\n"
        f"Created at: {event.occurred_at.isoformat()}"
    )


async def handle(payload: dict[str, object]) -> None:
    event = TicketCreatedEvent.model_validate(payload)

    await process_notifications(
        event_id=event.event_id,
        event_type=event.event_type,
        recipients=[
            str(recipient.email)
            for recipient in event.data.recipients
        ],
        subject=f"[New Ticket] {event.data.title}",
        message=build_message(event),
   )
