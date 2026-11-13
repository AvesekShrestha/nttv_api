from datetime import timedelta

from sqlalchemy.sql.functions import now

from ticket.application.assignment.dto.assignment_query_dto import AssignmentQueryDTO
from ticket.application.assignment.dto.claim_eligibility_dto import ClaimEligibilityResponse
from ticket.application.events.ticket_dispatched_event import TicketDispatchedEvent
from ticket.application.events.ticket_forwarded_event import TicketForwardedEvent
from ticket.application.interfaces.outbox_repository_interface import IOutboxRepository
from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate
from ticket.domain.assignment.assignment_status import AssignmentStatus
from ticket.domain.assignment.assignment_type import AssignmentType
from ticket.domain.assignment.entity.agent_recipient_entity import AgentRecipientEntity
from ticket.domain.assignment.entity.team_recipient_entity import TeamRecipientEntity
from ticket.domain.assignment.exceptions.assignment_exception import AssignmentNotFound, IneligibleRecipient, InvalidReassignmentRequest
from ticket.domain.outbox.entity.outbox_event_entity import OutboxEvent
from ticket.domain.rotation.round_robin_aggregate import RoundRobinAggregate
from ticket.domain.rotation.round_robin_scope import RoundRobinScope
from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity
from ticket.domain.ticket.ticket_activity_type import TicketActivityType
from ticket.domain.ticket.ticket_aggregate import TicketAggregrate

from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.interfaces.assignment_repository_interface import IAssignmentRepository
from ticket.application.interfaces.ticket_repository_interface import ITicketRepository
from ticket.application.shared.id_generator_interface import IIdGenerator
from ticket.application.exceptions.ticket_exception import TicketNotFound
from ticket.application.assignment.exceptions.index import AlreadyDispatched, TeamNotFound, AgentNotFound
from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.application.assignment.dto.assignment_dto import (
    AgentRecipientResponseDTO,
    TeamAssignmentDTO,
    TeamRecipientResponseDTO,
    AssignmentResponseDTO,
    ReassignmentDTO
)
from ticket.application.shared.unit_of_work_interface import IUnitOfWork
from ticket.application.shared.organization_client_interface import IOrganizationClient
from ticket.application.assignment.dto.team_data_dto import TeamDetailResponseDTO
from ticket.application.interfaces.round_robin_repository_interface import IRoundRobinRepository

from ticket.config import settings

class AssignmentService(IAssignmentService):

    def __init__(
        self,
        assignment_repository : IAssignmentRepository,
        ticket_repository : ITicketRepository,
        round_robin_repository : IRoundRobinRepository,
        outbox_repository : IOutboxRepository,
        organization_client : IOrganizationClient,
        id_generator : IIdGenerator,
        datetime_provider : IDateTimeProvider,
        unit_of_work : IUnitOfWork

    ): 
        self.assignment_repository = assignment_repository
        self.ticket_repository = ticket_repository
        self.outbox_repository = outbox_repository
        self.round_robin_repository = round_robin_repository
        self.organization_client = organization_client
        self.id_generator = id_generator
        self.datetime_provider = datetime_provider
        self.unit_of_work = unit_of_work

    async def _select_next(
        self,
        scope_type: RoundRobinScope,
        scope_id: str,
        candidates: list[str],
    ) -> str:

        if not candidates:
            raise IneligibleRecipient("No eligible candidates available")

        rotation: RoundRobinAggregate | None = (
            await self.round_robin_repository.get_by_scope(
                scope_type=scope_type,
                scope_id=scope_id,
            )
        )

        is_new = rotation is None

        if is_new:
            rotation = RoundRobinAggregate.create(
                id=self.id_generator.generate_random_id(),
                scope_type=scope_type,
                scope_id=scope_id,
            )

        selected_id = rotation.select_next(candidates)

        if is_new:
            await self.round_robin_repository.add(rotation)
        else:
            await self.round_robin_repository.update(rotation)

        return selected_id

    async def _validate_reassignment_targets(
        self,
        teams: list[TeamAssignmentDTO],
    ) -> None:
        team_ids = [team.team_id for team in teams]

        if len(team_ids) != len(set(team_ids)):
            raise InvalidReassignmentRequest(
                "Duplicate team IDs are not allowed"
            )

        for team_data in teams:
            if len(team_data.agent_ids) != len(set(team_data.agent_ids)):
                raise InvalidReassignmentRequest(
                    f"Duplicate agents found in team {team_data.team_id}"
                )

        organization_teams = await self.organization_client.get_teams_by_id(
            team_ids
        )

        teams_map = {
            team.id: team
            for team in organization_teams
        }

        for team_data in teams:

            team = teams_map.get(team_data.team_id)

            if team is None:
                raise TeamNotFound(team_data.team_id)

            if not team.is_active:
                raise IneligibleRecipient(
                    f"Team {team.id} is inactive"
                )

            active_agent_ids = {
                member.user_id
                for member in team.members
                if member.is_active
            }

            for agent_id in team_data.agent_ids:

                if agent_id not in active_agent_ids:
                    raise IneligibleRecipient(
                        f"Agent {agent_id} is not an active member "
                        f"of team {team_data.team_id}"
                    )

    async def _create_reassignment(
        self,
        ticket_id: str,
        request: ReassignmentDTO,
        actor_id: str,
        assignment_type: AssignmentType,
        activity_type: TicketActivityType,
    ):
        ticket = await self.ticket_repository.get_by_id(ticket_id)

        if ticket is None:
            raise TicketNotFound(ticket_id)

        current_assignment_id = ticket.current_assignment_id

        if current_assignment_id is None:
            raise AssignmentNotFound(
                "Ticket does not have an active assignment"
            )

        current_assignment = await self.assignment_repository.get_by_id(
            current_assignment_id
        )

        if current_assignment is None:
            raise AssignmentNotFound(current_assignment_id)

        if current_assignment.responsible_agent_id != actor_id :
            raise IneligibleRecipient("You don't have ticket claim to perform this action")

        await self._validate_reassignment_targets(request.teams)

        assignment_id = self.id_generator.generate_ticket_assignment_id()
        now = self.datetime_provider.now()

        new_assignment = AssignmentAggregate.create(
            id=assignment_id,
            ticket_id=ticket_id,
            assignment_type=assignment_type,
            assigned_at=now,
            assigned_by=actor_id,
            acknowledgment_deadline_at=now + timedelta(minutes=settings.ACKNOWLEDGEMENT_DEADLINE_IN_HOURS),
            resolution_deadline_at=now + timedelta(minutes=settings.RESOLUTION_DEADLINE_IN_HOURS))
        for team_data in request.teams:

            team_recipient_id = self.id_generator.generate_team_recipient_id()

            team_recipient = TeamRecipientEntity.create(
                id=team_recipient_id,
                assignment_id=assignment_id,
                team_id=team_data.team_id,
                created_at=now,
            )

            for agent_id in team_data.agent_ids:

                agent_recipient_id = self.id_generator.generate_agent_recipient_id()
                agent_recipient = AgentRecipientEntity.create(
                    id=agent_recipient_id,
                    team_recipient_id=team_recipient_id,
                    agent_id=agent_id,
                    can_claim=True,
                    created_at=now
                )

                team_recipient.add_agents([agent_recipient])

            new_assignment.add_team_recipient([team_recipient])

        current_assignment.mark_superseded(
            at=now
        )

        ticket.reassign(
            assignment_id=new_assignment.id,
        )

        activity_id : str = self.id_generator.generate_ticket_activities_id()
        ticket.record_activity(
            activity_id=activity_id,
            activity_type=activity_type,
            actor_id=actor_id,
            created_at=now
        )

        event_data : TicketForwardedEvent = TicketForwardedEvent(
            ticket_id=ticket_id,
            assignment_id=assignment_id
        )

        if assignment_type == AssignmentType.FORWARD : 
            event = OutboxEvent.create(
                key=actor_id,
                event_id=self.id_generator.generate_event_id(),
                event_type="ticket.forwarded",
                occurred_at=self.datetime_provider.now(),
                data=event_data.model_dump(mode="json")
            )
            await self.outbox_repository.add(event=event)

        if assignment_type == AssignmentType.ESCALATION:
            event = OutboxEvent.create(
                key=actor_id,
                event_id=self.id_generator.generate_event_id(),
                event_type="ticket.escalated",
                occurred_at=self.datetime_provider.now(),
                data=event_data.model_dump(mode="json")
            )

            await self.outbox_repository.add(event=event)

        await self.assignment_repository.update(current_assignment)
        await self.assignment_repository.add(new_assignment)
        await self.ticket_repository.update(ticket)

        await self.unit_of_work.commit()

        return new_assignment


    async def get_by_id(self, assignment_id: str) -> AssignmentResponseDTO:

        result = await self.assignment_repository.get_by_id(assignment_id=assignment_id)

        if result is None: 
            raise ValueError("No such assignement")

        return self._to_response(result)

    async def get_by_ticket_id(self, ticket_id: str) -> list[AssignmentResponseDTO]:

        result = await self.assignment_repository.get_by_ticket_id(ticket_id=ticket_id)

        return [
            self._to_response(aggregate=aggregate)
            for aggregate in result
        ]

    async def get_all(self, query: AssignmentQueryDTO) -> PaginatedResponse[AssignmentResponseDTO]:

        result = await self.assignment_repository.get_all(query=query)
        return PaginatedResponse(
            items=[
                self._to_response(assignment)
                for assignment in result.items
            ],
            total=result.total,
            page=result.page,
            limit=result.limit
        )

    async def dispatch(
        self,
        ticket_id: str,
    ) -> AssignmentResponseDTO:

        ticket: TicketAggregrate | None = (
            await self.ticket_repository.get_by_id(
                ticket_id=ticket_id
            )
        )

        if ticket is None:
            raise TicketNotFound(
                f"Ticket with id: {ticket_id} not found"
            )

        if ticket.has_initial_assignment():
            raise AlreadyDispatched(
                "Ticket has already been dispatched"
            )

        teams: list[TeamDetailResponseDTO] = (
            await self.organization_client.get_teams_by_category(
                category_id=ticket.category_id
            )
        )

        eligible_teams = [
            team
            for team in teams
            if team.is_active
            and any(member.is_active for member in team.members)
        ]

        if not eligible_teams:
            raise TeamNotFound("No eligible teams found")

        selected_team_id = await self._select_next(
            scope_type=RoundRobinScope.TEAM,
            scope_id=ticket.category_id,
            candidates=[
                team.id
                for team in eligible_teams
            ],
        )

        selected_team = next(
            team
            for team in eligible_teams
            if team.id == selected_team_id
        )

        eligible_members = [
            member
            for member in selected_team.members
            if member.is_active
        ]

        if not eligible_members:
            raise AgentNotFound(
                "No eligible agents found in selected team"
            )

        primary_agent_id = await self._select_next(
            scope_type=RoundRobinScope.AGENT,
            scope_id=selected_team_id,
            candidates=[
                member.user_id
                for member in eligible_members
            ],
        )

        now = self.datetime_provider.now()
        assignment_id = (
            self.id_generator.generate_ticket_assignment_id()
        )
        assignment = AssignmentAggregate.create(
            id=assignment_id,
            ticket_id=ticket.id,
            assignment_type=AssignmentType.SYSTEM,
            assigned_at=now,
            assigned_by=None,
            acknowledgment_deadline_at=(
                now + timedelta(
                    minutes=settings.ACKNOWLEDGEMENT_DEADLINE_IN_HOURS
                )
            ),
            resolution_deadline_at=(
                now + timedelta(
                    minutes=settings.RESOLUTION_DEADLINE_IN_HOURS
                )
            ),
            primary_agent_id=primary_agent_id,
            responsible_agent_id=primary_agent_id,
        )

        team_recipient_id = (
            self.id_generator.generate_team_recipient_id()
        )
        team_recipient = TeamRecipientEntity.create(
            id=team_recipient_id,
            assignment_id=assignment_id,
            team_id=selected_team_id,
            created_at=now,
        )

        agent_recipients = []

        for member in eligible_members:
            agent_recipient = AgentRecipientEntity.create(
                id=self.id_generator.generate_agent_recipient_id(),
                team_recipient_id=team_recipient_id,
                agent_id=member.user_id,
                can_claim=(member.user_id == primary_agent_id),
                created_at=now
            )

            agent_recipients.append(agent_recipient)

        team_recipient.add_agents(
            agents=agent_recipients
        )

        assignment.add_team_recipient(
            recipients=[team_recipient]
        )

        await self.assignment_repository.add(
            aggregate=assignment
        )

        ticket.record_activity(
            activity_id=(
                self.id_generator.generate_ticket_activities_id()
            ),
            activity_type=TicketActivityType.DISPATCHED,
            actor_id=None,
            created_at=now
        )

        ticket.dispatch(
            assignment_id=assignment_id
        )

        event_data : TicketDispatchedEvent = TicketDispatchedEvent(
            ticket_id=ticket_id,
            assignment_id=assignment_id
        )

        event = OutboxEvent.create(
            key=ticket_id,
            event_id=self.id_generator.generate_event_id(),
            event_type="ticket.dispatched",
            occurred_at=now,
            data=event_data.model_dump(mode="json")
        )

        await self.ticket_repository.update(ticket)
        await self.outbox_repository.add(event=event)

        await self.unit_of_work.commit()

        return self._to_response(assignment)


    async def forward(self, ticket_id : str, actor_id : str, payload: ReassignmentDTO) -> AssignmentResponseDTO:
        result = await self._create_reassignment(
            ticket_id=ticket_id,
            request=payload,
            actor_id=actor_id,
            assignment_type=AssignmentType.FORWARD,
            activity_type=TicketActivityType.FORWARDED
        )


        return self._to_response(result)

    async def escalate(self, ticket_id : str, actor_id : str, payload: ReassignmentDTO) -> AssignmentResponseDTO:
        result = await self._create_reassignment(
            ticket_id=ticket_id,
            request=payload,
            actor_id=actor_id,
            assignment_type=AssignmentType.ESCALATION,
            activity_type=TicketActivityType.ESCALATED
        )
        return self._to_response(result)

    async def claim_eligibility(self, assignment_id : str, agent_id : str) -> ClaimEligibilityResponse:

        assignment = await self.assignment_repository.get_by_id(
            assignment_id
        )

        if assignment is None:
            raise AssignmentNotFound(
                f"Assignment {assignment_id} not found"
            )

        can_claim = assignment.can_be_claimed_by(agent_id)

        return ClaimEligibilityResponse(
            can_claim=can_claim
        )

    @staticmethod
    def _to_response(
        aggregate: AssignmentAggregate,
    ) -> AssignmentResponseDTO:
        return AssignmentResponseDTO(
            id=aggregate.id,
            ticket_id=aggregate.ticket_id,
            assigned_by=aggregate.assigned_by,
            assignment_type=aggregate.assignment_type,
            status=aggregate.status,
            primary_agent_id=aggregate.primary_agent_id,
            responsible_agent_id=aggregate.responsible_agent_id,
            team_recipients=[
                TeamRecipientResponseDTO(
                    id=team.id,
                    team_id=team.team_id,
                    agents=[
                        AgentRecipientResponseDTO(
                            id=agent.id,
                            agent_id=agent.agent_id,
                            can_claim=agent.can_claim,
                            notified_at=agent.notified_at,
                            acknowledged_at=agent.acknowledged_at,
                            claimed_at=agent.claimed_at,
                        )
                        for agent in team.agents
                    ],
                )
                for team in aggregate.team_recipients
            ],
            assigned_at=aggregate.assigned_at,
            acknowledged_at=aggregate.acknowledged_at,
            acknowledgment_deadline_at=aggregate.acknowledgment_deadline_at,
            resolution_deadline_at=aggregate.resolution_deadline_at,
            acknowledgment_sla_breached_at=aggregate.acknowledgment_sla_breached_at,
            resolution_sla_breached_at=aggregate.resolution_sla_breached_at,
            completed_at=aggregate.completed_at,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
