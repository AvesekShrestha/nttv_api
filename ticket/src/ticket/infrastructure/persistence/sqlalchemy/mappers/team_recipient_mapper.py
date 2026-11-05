from ticket.domain.assignment.entity.team_recipient_entity import TeamRecipientEntity
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_team_recipient_model import AssignmentTeamRecipient
from ticket.infrastructure.persistence.sqlalchemy.mappers.agent_recipient_mapper import AgentRecipientMapper


class TeamRecipientMapper:

    @staticmethod
    def to_model(
        aggregate: TeamRecipientEntity,
    ) -> AssignmentTeamRecipient:

        return AssignmentTeamRecipient(
            id=aggregate.id,
            assignment_id=aggregate.assignment_id,
            team_id=aggregate.team_id,

            created_at=aggregate.created_at,

            agent_recipients=[
                AgentRecipientMapper.to_model(agent)
                for agent in aggregate.agents
            ],
        )

    @staticmethod
    def to_domain(
        model: AssignmentTeamRecipient,
    ) -> TeamRecipientEntity:

        return TeamRecipientEntity(
            _id=model.id,
            _assignment_id=model.assignment_id,
            _team_id=model.team_id,

            _agents=[
                AgentRecipientMapper.to_domain(agent)
                for agent in model.agent_recipients
            ],
            _created_at=model.created_at,
        )

