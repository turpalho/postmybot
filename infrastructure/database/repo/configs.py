from typing import Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update

from infrastructure.database.models import Config
from infrastructure.database.repo.base import BaseRepo


class ConfigRepo(BaseRepo):
    model = Config

    async def create_config(
        self,
        admins_ids: list
    ):
        """
        Creates a new config in the database and returns the config object.

        Args:
            admins_ids (list): The unique ids list.

        Returns:
            Config: The Config object.
        """
        new_str = str(admins_ids)[1:-1]
        self.session.add(Config(id=1, admins_ids=new_str))
        await self.session.commit()
        return

    async def get_config_parameters(self) -> Config:
        stmt = select(Config).where(Config.id == 1)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def update_admin_ids(self, admins_ids: list) -> None:
        admins_ids = str(admins_ids)[1:-1]
        stmt = update(Config).where(
            Config.id == 1).values(admins_ids=admins_ids)
        await self.session.execute(stmt)
        await self.session.commit()
        return

    async def update_subadmin_ids(self, subadmins_ids: list) -> None:
        subadmins_ids = str(subadmins_ids)[1:-1]
        stmt = update(Config).where(
            Config.id == 1).values(subadmins_ids=subadmins_ids)
        await self.session.execute(stmt)
        await self.session.commit()
        return