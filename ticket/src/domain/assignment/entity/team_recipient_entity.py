from dataclasses import dataclass, field

from domain.shared.entity import Entity
from src.domain.assignment.entity.agent_recipient_entity import AgentRecipientEntity


@dataclass
class TeamRecipientEntity(Entity[str]):
    _team_id: str
    _agents: list[AgentRecipientEntity] = field(default_factory=list)

    @property
    def team_id(self) -> str:
        return self._team_id

    @property
    def agents(self) -> list[AgentRecipientEntity]:
        return self._agents.copy()

    def add_agent(self, agent: AgentRecipientEntity) -> None:
        if any(a.agent_id == agent.agent_id for a in self._agents):
            raise ValueError(
                "Agent already exists in this team recipient"
            )

        self._agents.append(agent)

    def get_agent(self, agent_id: str) -> AgentRecipientEntity | None:
        return next(
            (
                agent
                for agent in self._agents
                if agent.agent_id == agent_id
            ),
            None,
        )
