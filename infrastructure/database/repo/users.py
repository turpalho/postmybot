from typing import Optional

from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    model = User

    async def get_or_create_user(
        self,
        user_id: int,
        username: Optional[str],
        tg_first_name: str = None,
        tg_last_name: str = None,
        tg_username: str = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.

        Args:
            user_id (int): The unique identifier of the user.
            username (Optional[str]): The username of the user.
            tg_first_name (str): The first name of the user.
            tg_last_name (str): The last name of the user.
            tg_username (str): The username of the user.

        Returns:
            User: The User object.
        """
        user_values = {
            "user_id": user_id,
            "username": username,
            "tg_first_name": tg_first_name,
            "tg_last_name": tg_last_name,
            "tg_username": tg_username,
        }

        insert_stmt = (
            insert(self.model)
            .values(**user_values)
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_=dict(
                    username=username,
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()
