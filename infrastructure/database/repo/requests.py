from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from . import (UserRepo,
               ChannelRepo,
               PostRepo,
               ConfigRepo)
from infrastructure.database.setup import create_engine


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def configs(self) -> ConfigRepo:
        """
        The Config repository sessions are required to manage user operations.
        """
        return ConfigRepo(self.session)

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)

    @property
    def channels(self) -> ChannelRepo:
        """
        The Channel repository sessions are required to manage channel operations.
        """
        return ChannelRepo(self.session)

    @property
    def posts(self) -> PostRepo:
        """
        The Post repository sessions are required to manage post operations.
        """
        return PostRepo(self.session)


if __name__ == "__main__":
    from infrastructure.database.setup import create_session_pool
    from tgbot.config import Config

    # async def example_usage(config: Config):
    #     """
    #     Example usage function for the RequestsRepo class.
    #     Use this function as a guide to understand how to utilize RequestsRepo for managing user data.
    #     Pass the config object to this function for initializing the database resources.
    #     :param config: The config object loaded from your configuration.
    #     """
    #     engine = await create_engine(config.db)
    #     session_pool = create_session_pool(engine)

    #     async with session_pool() as session:
    #         repo = RequestsRepo(session)

    #         # Replace user details with the actual values
    #         user = await repo.users.get_or_create_user(
    #             user_id=12356,
    #             full_name="John Doe",
    #             language="en",
    #             username="johndoe",
    #         )
