from src.domain.category.category_aggregrate import CategoryAggregrate
from src.infrastructure.persistence.sqlalchemy.models.category_model import Category


class CategoryMapper:

    @staticmethod
    def to_domain(model: Category) -> CategoryAggregrate:
        return CategoryAggregrate(
            _id=model.id,
            _name=model.name,
            _description=model.description,
            _is_active=model.is_active,
            _created_at=model.created_at,
            _updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(aggregate: CategoryAggregrate) -> Category:
        return Category(
            id=aggregate.id,
            name=aggregate.name,
            description=aggregate.description,
            is_active=aggregate.is_active,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
