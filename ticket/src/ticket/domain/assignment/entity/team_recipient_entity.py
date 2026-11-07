from dataclasses import dataclass, field
from datetime import datetime

from ticket.domain.shared.entity import Entity
from ticket.domain.assignment.entity.agent_recipient_entity import (
    AgentRecipientEntity,
)
from ticket.domain.assignment.exceptions.agent_exceptions import (
    AgentAlreadyExists,
)
from ticket.application.assignment.exceptions.index import AgentNotFound


@dataclass
class TeamRecipientEntity(Entity[str]):
    _assignment_id: str
    _team_id: str
    _created_at: datetime | None = None
    _agents: list[AgentRecipientEntity] = field(default_factory=list)

    @property
    def assignment_id(self) -> str:
        return self._assignment_id

    @property
    def team_id(self) -> str:
        return self._team_id

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def agents(self) -> list[AgentRecipientEntity]:
        return self._agents.copy()

    def add_agents(
        self,
        agents: list[AgentRecipientEntity],
    ) -> None:
        existing_agent_ids = {
            agent.agent_id
            for agent in self._agents
        }

        incoming_agent_ids = set()

        for agent in agents:
            if agent.team_recipient_id != self.id:
                raise AgentNotFound(
                    "Agent recipient belongs to a different team recipient"
                )

            if (
                agent.agent_id in existing_agent_ids
                or agent.agent_id in incoming_agent_ids
            ):
                raise AgentAlreadyExists(
                    "Agent already exists in this team recipient"
                )

            incoming_agent_ids.add(agent.agent_id)

        self._agents.extend(agents)

    def get_agent(
        self,
        agent_id: str,
    ) -> AgentRecipientEntity | None:
        return next(
            (
                agent
                for agent in self._agents
                if agent.agent_id == agent_id
            ),
            None,
        )

    def remove_agent(self, agent_id: str) -> None:
        agent = self.get_agent(agent_id)

        if agent is None:
            raise AgentNotFound(
                "Agent does not exist in this team recipient"
            )

        self._agents.remove(agent)

    @staticmethod
    def create(
        id: str,
        assignment_id: str,
        team_id: str,
        created_at: datetime | None = None,
    ) -> "TeamRecipientEntity":
        return TeamRecipientEntity(
            _id=id,
            _assignment_id=assignment_id,
            _team_id=team_id,
            _created_at=created_at,
        )
