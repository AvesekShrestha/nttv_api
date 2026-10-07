from src.domain.shared.level import Level
from src.domain.team.team_aggregate import TeamAggregate
from src.domain.team.entity.team_member_entity import TeamMember
from src.infrastructure.persistence.sqlalchemy.models.team_model import Team
from src.infrastructure.persistence.sqlalchemy.models.team_member_model import TeamMember as TeamMemberModel



class TeamMapper:

    @staticmethod
    def member_to_domain(
        model: TeamMemberModel,
    ) -> TeamMember:

        return TeamMember(
            _id=model.id,
            _user_id=model.user_id,
            _joined_at=model.joined_at,
            _is_active=model.is_active,
        )

    @staticmethod
    def member_to_model(
        member: TeamMember,
        team_id: str,
    ) -> TeamMemberModel:

        return TeamMemberModel(
            id=member.id,
            team_id=team_id,
            user_id=member.user_id,
            joined_at=member.joined_at,
            is_active=member.is_active,
        )

    @staticmethod
    def to_domain(
        model: Team,
    ) -> TeamAggregate:

        return TeamAggregate(
            _id=model.id,
            _name=model.name,
            _description=model.description,
            _level=Level.from_string(model.level),
            _is_active=model.is_active,
            _category_id=model.category_id,
            _members=[
                TeamMapper.member_to_domain(member)
                for member in model.members
            ],
            _created_at=model.created_at,
            _updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(
        aggregate: TeamAggregate,
    ) -> Team:

        return Team(
            id=aggregate.id,
            name=aggregate.name,
            description=aggregate.description,
            level=aggregate.level.value,
            is_active=aggregate.is_active,
            category_id=aggregate.category_id,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
            members=[
                TeamMapper.member_to_model(
                    member=member,
                    team_id=aggregate.id,
                )
                for member in aggregate.members
            ],
        )
