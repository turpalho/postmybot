from typing import Optional

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo


async def get_or_create_user(
    user_id: int,
    username: str,
    tg_first_name: str,
    tg_last_name: str,
    tg_username: str,
    repository: RequestsRepo,
) -> tuple[User, bool]:
    """
    Returns the user object if it exists in the database, otherwise creates a new user and returns it.

    Args:
        user_id (int): The unique identifier of the user.
        username (str): The username of the user.
        tg_first_name (str): The first name of the user from Telegram update.
        tg_last_name (str): The last name of the user from Telegram update.
        tg_username (str): The username of the user from Telegram update.
        tg_language_code (Optional[str]): The language code of the user from Telegram update.
        repository (RequestsRepo): The instance of the RequestsRepo class.
    """
    user = await repository.users.get_or_none(user_id=user_id)
    if not user:
        user = await repository.users.get_or_create_user(
            user_id, username, tg_first_name, tg_last_name, tg_username
        )
        return user, True
    return user, False
