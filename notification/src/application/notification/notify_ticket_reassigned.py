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


ReassignmentEventType = Literal[
    "ticket.forwarded",
    "ticket.escalated",
]


class NotifyTicketReassigned:
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
        event_type: ReassignmentEventType,
        occurred_at: datetime,
        ticket_id: str,
        assignment_id: str,
        source_topic: str = "ticket.events",
    ) -> bool:
        if event_type not in (
            "ticket.forwarded",
            "ticket.escalated",
        ):
            raise ValueError(
                "Unsupported reassignment event type"
            )

        ticket = await self.ticket_client.get_ticket(ticket_id)

        assignment = await self.ticket_client.get_assignment(
            assignment_id
        )

        if assignment.ticket_id != ticket.id:
            raise ValueError(
                "Assignment does not belong to this ticket"
            )

        eligibility: dict[str, bool] = {}

        for team in assignment.team_recipients:
            for agent in team.agents:
                eligibility[agent.agent_id] = (
                    eligibility.get(agent.agent_id, False)
                    or agent.can_claim
                )

        if not eligibility:
            raise ValueError(
                "Assignment has no recipient agents"
            )

        action = (
            "forwarded"
            if event_type == "ticket.forwarded"
            else "escalated"
        )

        recipients = []

        for agent_id, can_claim in sorted(eligibility.items()):
            message = (
                f"A ticket has been {action} to your team."
            )

            if can_claim:
                message += (
                    "\nOpen the ticket to review and claim it."
                )

            recipients.append(
                InboxRecipient(
                    user_id=agent_id,
                    title=f"Ticket {action} to your team",
                    message=(
                        f"{message}\n\n"
                        f"Ticket: {ticket.title}\n"
                        f"Ticket ID: {ticket.id}\n"
                        f"Assignment ID: {assignment.id}"
                    ),
                    requires_action=can_claim,
                    send_email=can_claim,
                )
            )

        return await self.inbox_repository.record_event(
            RecordTicketEventRequest(
                source_topic=source_topic,
                event_id=event_id,
                event_type=event_type,
                occurred_at=occurred_at,
                ticket_id=ticket.id,
                assignment_id=assignment.id,
                recipients=tuple(recipients),
            )
        )
