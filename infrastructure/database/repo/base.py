from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo:
    """
    A class representing a base repository for handling database operations.

    Attributes:
        session (AsyncSession): The database session used by the repository.

    """

    # todo - add type hints for the attribute
    model = None

    def __init__(self, session):
        self.session: AsyncSession = session

    async def get_or_none(self, **kwargs):
        """
        Retrieves a single object from the database based on the provided filters.

        Args:
            **kwargs: Arbitrary keyword arguments to filter the object.

        Returns:
            The object if found, None otherwise.

        """
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
