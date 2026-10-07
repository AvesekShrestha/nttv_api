from src.application.exceptions.team_exception import TeamNotFound
from src.application.interfaces.team_repository_interface import ITeamRepository

from src.application.dto.team_dto import TeamResponseDTO, TeamCreateDTO, TeamUpdateDTO, TeamMemberResponseDTO
from src.application.shared.id_generator_interface import IIdGenerator
from src.application.team.team_service_interface import ITeamService

from src.domain.team.entity.team_member_entity import TeamMember
from src.domain.team.team_aggregate import TeamAggregate


class TeamService(ITeamService):

    def __init__(
        self,
        team_repository: ITeamRepository,
        id_generator : IIdGenerator,
    ):
        self.team_repository = team_repository
        self.id_generator = id_generator

    async def get_by_id(
        self,
        team_id: str,
    ) -> TeamResponseDTO | None:

        team = await self.team_repository.get_by_id(
            team_id=team_id,
        )

        if team is None:
            return None

        return self._to_response(team)

    async def get_all(
        self,
    ) -> list[TeamResponseDTO]:

        teams = await self.team_repository.get_all()

        return [
            self._to_response(team)
            for team in teams
        ]

    async def create(
        self,
        payload: TeamCreateDTO,
    ) -> TeamResponseDTO:

        team = TeamAggregate.create(
            id=self.id_generator.generate_team_id(),
            name=payload.name,
            description=payload.description,
            category_id=payload.category_id,
            level=payload.level,
        )

        team = await self.team_repository.add(
            aggregate=team,
        )

        return self._to_response(team)

    async def add_team_member(self, team_id: str, user_id: str) -> TeamResponseDTO:

        member : TeamMember = TeamMember(
            _id=self.id_generator.generate_team_member_id(),
            _user_id=user_id
        )

        team : TeamAggregate | None = await self.team_repository.get_by_id(team_id=team_id)
        if not team : raise TeamNotFound("Team doesn't exists")
   
        team.add_member(member=member)

        result = await self.team_repository.update(team)
        return self._to_response(team)

    async def remove_team_member(self, team_id: str, user_id: str) -> TeamResponseDTO:

        team : TeamAggregate | None = await self.team_repository.get_by_id(team_id=team_id)
        if not team : raise TeamNotFound("Team doesn't exists")
   
        team.remove_member(member_id=user_id)

        result = await self.team_repository.update(team)
        return self._to_response(team)

    async def update(
        self,
        team_id: str,
        payload: TeamUpdateDTO,
    ) -> TeamResponseDTO:

        team = await self.team_repository.get_by_id(
            team_id=team_id,
        )

        if team is None:
            raise ValueError("Team not found")

        team.change_name(payload.name)
        team.change_description(payload.description)
        team.change_category(payload.category_id)
        team.change_level(payload.level)

        team = await self.team_repository.update(
            aggregate=team,
        )

        return self._to_response(team)

    async def delete(
        self,
        team_id: str,
    ) -> None:

        team = await self.team_repository.get_by_id(
            team_id=team_id,
        )

        if team is None:
            raise ValueError("Team not found")

        await self.team_repository.delete(
            team_id=team_id,
        )

    @staticmethod
    def _to_response(
        team: TeamAggregate,
    ) -> TeamResponseDTO:

        return TeamResponseDTO(
            id=team.id,
            name=team.name,
            description=team.description,
            level=team.level,
            category_id=team.category_id,
            is_active=team.is_active,
            members=[
                TeamMemberResponseDTO(
                    id=member.id,
                    user_id=member.user_id,
                    joined_at=member.joined_at,
                    is_active=member.is_active,
                )
                for member in team.members
            ],
            created_at=team.created_at,
            updated_at=team.updated_at,
        )
