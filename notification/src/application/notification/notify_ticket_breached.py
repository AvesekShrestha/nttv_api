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


class NotifyTicketBreached:
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
        assignment_id: str,
        source_topic: str = "ticket.events",
    ) -> bool:
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

        owner_id = (
            assignment.responsible_agent_id
            or assignment.primary_agent_id
        )

        if owner_id is not None and owner_id not in eligibility:
            raise ValueError(
                "Responsible or primary agent is missing from recipients"
            )

        recipients = []

        for agent_id, can_claim in sorted(eligibility.items()):
            requires_action = (
                agent_id == owner_id
                if owner_id is not None
                else can_claim
            )

            message = (
                "An SLA deadline has been breached "
                "for a ticket in your assignment."
            )

            if requires_action:
                message += (
                    "\nPlease review the ticket "
                    "and take the appropriate action."
                )

            recipients.append(
                InboxRecipient(
                    user_id=agent_id,
                    title="Ticket SLA breached",
                    message=(
                        f"{message}\n\n"
                        f"Ticket: {ticket.title}\n"
                        f"Ticket ID: {ticket.id}\n"
                        f"Assignment ID: {assignment.id}\n"
                        f"Event time: {occurred_at.isoformat()}"
                    ),
                    requires_action=requires_action,
                    send_email=requires_action,
                )
            )

        return await self.inbox_repository.record_event(
            RecordTicketEventRequest(
                source_topic=source_topic,
                event_id=event_id,
                event_type="ticket.breached",
                occurred_at=occurred_at,
                ticket_id=ticket.id,
                assignment_id=assignment.id,
                recipients=tuple(recipients),
            )
        )
