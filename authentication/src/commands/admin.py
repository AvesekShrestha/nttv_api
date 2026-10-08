import asyncio
import getpass

from src.config.container import container

from src.infrastructure.persistence.sqlalchemy.database import session_factory

from src.domain.users.user_role import UserRole
from src.domain.users.user_aggregrate import UserAggregrate


async def create_admin() -> None:
    username = input("Username: ").strip()
    email = input("Email: ").strip()

    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return


    async with session_factory() as session:
        container.session.override(session)

        user_repository = container.user_repository()
        hasher = container.hasher()
        id_generator = container.id_genertor()

        existing_user = await user_repository.get_by_email(email)

        if existing_user is not None:
            print(f"User with email '{email}' already exists.")
            return

        password_hash = await hasher.hash(password)

        user = UserAggregrate.create(
            id=id_generator.generate_user_id(),
            username=username,
            email=email,
            password=password_hash,
            role=UserRole.ADMIN
        )

        await user_repository.add(user)

        await session.commit()

        print(f"Admin '{username}' created successfully.")


if __name__ == "__main__":
    asyncio.run(create_admin())
