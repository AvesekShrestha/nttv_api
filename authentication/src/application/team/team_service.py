from src.application.exceptions.category_exception import CategoryDoesNotExists
from src.application.exceptions.team_exception import TeamNotFound
from src.application.exceptions.user_exception import UserNotFound
from src.application.interfaces.category_repository_interface import ICategoryRepository
from src.application.interfaces.team_repository_interface import ITeamRepository

from src.application.dto.team_dto import TeamDetailResponseDTO, TeamResponseDTO, TeamCreateDTO, TeamUpdateDTO, TeamMemberResponseDTO
from src.application.interfaces.user_repository_interface import IUserRepository
from src.application.shared.id_generator_interface import IIdGenerator
from src.application.shared.unit_of_work_interface import IUnitOfWork
from src.application.team.team_service_interface import ITeamService

from src.domain.team.entity.team_member_entity import TeamMember
from src.domain.team.team_aggregate import TeamAggregate


class TeamService(ITeamService):

    def __init__(
        self,
        team_repository: ITeamRepository,
        category_repository: ICategoryRepository,
        user_repository: IUserRepository,
        id_generator : IIdGenerator,
        unit_of_work : IUnitOfWork
    ):
        self.team_repository = team_repository
        self.category_repository = category_repository
        self.user_repository = user_repository
        self.id_generator = id_generator
        self.unit_of_work = unit_of_work

    async def get_by_id(
        self,
        team_id: str,
    ) -> TeamDetailResponseDTO | None:

        team = await self.team_repository.get_by_id(
            team_id=team_id,
        )

        if team is None:
            return None

        return self._to_detail_response(team)

    async def get_all(
        self,
    ) -> list[TeamDetailResponseDTO]:

        teams = await self.team_repository.get_all()

        return [
            self._to_detail_response(team)
            for team in teams
        ]

    async def create(
        self,
        payload: TeamCreateDTO,
    ) -> TeamResponseDTO:

        category_exists = await self.category_repository.get_by_id(category_id=payload.category_id)
        if not category_exists: raise CategoryDoesNotExists(f"Category with id : {payload.category_id} doesnot exists")

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

        await self.unit_of_work.commit()
        return self._to_response(team)

    async def add_team_member(self, team_id: str, user_id: str) -> TeamDetailResponseDTO:

        exists = await self.user_repository.get_by_id(user_id=user_id)
        if not exists: 
            raise UserNotFound(f"User with id : {user_id} doesnot exists")

        member : TeamMember = TeamMember(
            _id=self.id_generator.generate_team_member_id(),
            _user_id=user_id
        )

        team : TeamAggregate | None = await self.team_repository.get_by_id(team_id=team_id)
        if not team : raise TeamNotFound("Team doesn't exists")
   
        team.add_member(member=member)

        result = await self.team_repository.update(team)

        await self.unit_of_work.commit()
        return self._to_detail_response(team)

    async def remove_team_member(self, team_id: str, user_id: str) -> TeamDetailResponseDTO:

        team : TeamAggregate | None = await self.team_repository.get_by_id(team_id=team_id)
        if not team : raise TeamNotFound("Team doesn't exists")
   
        team.remove_member(member_id=user_id)

        result = await self.team_repository.update(team)

        await self.unit_of_work.commit()
        return self._to_detail_response(team)

    async def update(
        self,
        team_id: str,
        payload: TeamUpdateDTO,
    ) -> TeamDetailResponseDTO:

        team = await self.team_repository.get_by_id(
            team_id=team_id,
        )

        if team is None:
            raise TeamNotFound(f"Team doesn't exists with id {team_id}")

        if payload.name : 
            team.change_name(payload.name)

        if payload.description :
            team.change_description(payload.description)

        if payload.category_id:
            team.change_category(payload.category_id)

        if payload.level :
            team.change_level(payload.level)

        team = await self.team_repository.update(
            aggregate=team,
        )

        await self.unit_of_work.commit()
        return self._to_detail_response(team)

    async def delete(
        self,
        team_id: str,
    ) -> bool:

        team = await self.team_repository.get_by_id(
            team_id=team_id,
        )

        if team is None:
            raise ValueError("Team not found")

        await self.team_repository.delete(
            team_id=team_id,
        )

        await self.unit_of_work.commit()
        return True

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
            created_at=team.created_at,
            updated_at=team.updated_at,
        )

    @staticmethod
    def _to_detail_response(
        team: TeamAggregate,
    ) -> TeamDetailResponseDTO:

        return TeamDetailResponseDTO(
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
