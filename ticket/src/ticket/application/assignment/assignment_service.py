from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.domain.assignment.assignment_type import AssignmentType
from ticket.application.assignment.dto.assignment_dto import (
    AgentRecipientResponseDTO,
    InitialAssignmentCreateDTO,
    TeamRecipientResponseDTO,
    AssignmentResponseDTO,
    InitialAssignmentCreateDTO,
    ReassignmentDTO
)
from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate
from ticket.domain.assignment.entity.team_recipient_entity import TeamRecipientEntity
from ticket.domain.assignment.entity.agent_recipient_entity import AgentRecipientEntity

from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.interfaces.assignment_repository_interface import IAssignmentRepository
from ticket.application.shared.id_generator_interface import IIdGenerator

class AssignmentService(IAssignmentService):

    def __init__(
        self,
        assignment_respository : IAssignmentRepository,
        id_generator : IIdGenerator,
        datetime_provider : IDateTimeProvider
    ): 
        self.assignment_repository = assignment_respository
        self.id_generator = id_generator
        self.datetime_provider = datetime_provider

    async def get_by_id(self, assignment_id: str) -> AssignmentResponseDTO:

        result = await self.assignment_repository.get_by_id(assignment_id=assignment_id)

        if result is None: 
            raise ValueError("No such assignement")

        return self._to_response(result)



    async def  create_initial_assignment(self, payload: InitialAssignmentCreateDTO, current_user_id: str):
        assignment : AssignmentAggregate = AssignmentAggregate.create(
            id=self.id_generator.generate_ticket_assignment_id(),
            ticket_id=payload.ticket_id,
            assigned_by=current_user_id,
            assignment_type=AssignmentType.from_string("INITIAL"),
            assigned_at=self.datetime_provider.now(),
            primary_agent_id=payload.primary_agent_id
        )

        agents = [
            AgentRecipientEntity(
                _id=self.id_generator.generate_agent_recipient_id(),
                _agent_id=agent.agent_id
            ) for team in payload.teams
            for agent in team.agents
        ]

        recipients = [
            TeamRecipientEntity(
                _id=self.id_generator.generate_team_recipient_id(),
                _team_id=team.team_id,
                _agents=agents
            ) for team in payload.teams
        ]

        assignment.add_team_recipient(recipients=recipients)

        result = await self.assignment_repository.add(assignment=assignment)

        return self._to_response(result)

    async def create_reassignment(self, payload: ReassignmentDTO, current_user_id : str) -> AssignmentResponseDTO:

        assignment : AssignmentAggregate = AssignmentAggregate.create(
            id=self.id_generator.generate_ticket_assignment_id(),
            ticket_id=payload.ticket_id,
            assigned_by=current_user_id,
            assignment_type=AssignmentType.from_string(payload.assignment_type),
            assigned_at=self.datetime_provider.now(),
        )

        agents = [
            AgentRecipientEntity(
                _id=self.id_generator.generate_agent_recipient_id(),
                _agent_id=agent.agent_id
            ) for team in payload.teams
            for agent in team.agents
        ]

        recipients = [
            TeamRecipientEntity(
                _id=self.id_generator.generate_team_recipient_id(),
                _team_id=team.team_id,
                _agents=agents
            ) for team in payload.teams
        ]

        assignment.add_team_recipient(recipients=recipients)

        result = await self.assignment_repository.add(assignment=assignment)

        return self._to_response(result)

    async def acknowledge(self, assignment_id: str, agent_id: str) -> AssignmentResponseDTO:

        assignment : AssignmentAggregate | None = await self.assignment_repository.get_by_id(assignment_id=assignment_id)

        if assignment is None : raise ValueError("No such assignment exists")

        assignment.acknowledge(at=self.datetime_provider.now())
        result = await self.assignment_repository.update(assignment)

        return self._to_response(result)

    async def claim(self, assignment_id: str, agent_id: str) -> AssignmentResponseDTO:

        assignment : AssignmentAggregate | None = await self.assignment_repository.get_by_id(assignment_id=assignment_id)

        if assignment is None : raise ValueError("No such assignment exists")

        assignment.claim(agent_id=agent_id, at=self.datetime_provider.now())
        result = await self.assignment_repository.update(assignment)
        return self._to_response(result)

    async def start(self, assignment_id: str, agent_id: str) -> AssignmentResponseDTO:

        assignment : AssignmentAggregate | None = await self.assignment_repository.get_by_id(assignment_id=assignment_id)

        if assignment is None : raise ValueError("No such assignment exists")
        assignment.mark_started(self.datetime_provider.now())

        result = await self.assignment_repository.update(assignment)
        return self._to_response(result)

    async def complete(self, assignment_id: str, agent_id: str) -> AssignmentResponseDTO:
        assignment : AssignmentAggregate | None = await self.assignment_repository.get_by_id(assignment_id=assignment_id)

        if assignment is None : raise ValueError("No such assignment exists")
        assignment.mark_completed(self.datetime_provider.now())

        result = await self.assignment_repository.update(assignment)
        return self._to_response(result)

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
            acknowledgment_deadline_at=aggregate.acknowledgment_deadline_at,
            resolution_deadline_at=aggregate.resolution_deadline_at,
            acknowledgment_sla_breached_at=aggregate.acknowledgment_sla_breached_at,
            resolution_sla_breached_at=aggregate.resolution_sla_breached_at,
            started_at=aggregate.started_at,
            completed_at=aggregate.completed_at,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
