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


class NotifyTicketDispatched:
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

        agent_ids = {
            agent.agent_id
            for team in assignment.team_recipients
            for agent in team.agents
        }

        if not agent_ids:
            raise ValueError(
                "Assignment has no recipient agents"
            )

        if assignment.primary_agent_id not in agent_ids:
            raise ValueError(
                "Primary agent is missing from assignment recipients"
            )

        recipients = []

        for agent_id in sorted(agent_ids):
            is_primary = agent_id == assignment.primary_agent_id

            if is_primary:
                title = "Ticket assigned to you"
                introduction = (
                    "A ticket has been assigned to you. "
                    "Please acknowledge it."
                )
            else:
                title = "Ticket assigned to your team"
                introduction = (
                    "A ticket has been assigned to your team.\n"
                    f"Primary agent: {assignment.primary_agent_id}"
                )

            recipients.append(
                InboxRecipient(
                    user_id=agent_id,
                    title=title,
                    message=(
                        f"{introduction}\n\n"
                        f"Ticket: {ticket.title}\n"
                        f"Ticket ID: {ticket.id}\n"
                        f"Assignment ID: {assignment.id}"
                    ),
                    requires_action=is_primary,
                    send_email=is_primary,
                )
            )

        return await self.inbox_repository.record_event(
            RecordTicketEventRequest(
                source_topic=source_topic,
                event_id=event_id,
                event_type="ticket.dispatched",
                occurred_at=occurred_at,
                ticket_id=ticket.id,
                assignment_id=assignment.id,
                recipients=tuple(recipients),
            )
        )
