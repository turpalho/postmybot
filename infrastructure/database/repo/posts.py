import logging
import os
from typing import TYPE_CHECKING, Optional

from sqlalchemy import delete, select, update, ScalarResult
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import Post, Image
from infrastructure.database.repo.base import BaseRepo



class PostRepo(BaseRepo):
    model = Post

    async def get_or_create_post(
        self,
        title: str,
        user_id: int,
        text: Optional[str] = None,
        image_urls: Optional[list[str]] = None,
    ):
        """
        Creates a new post in the database and returns the post object.

        Args:
            title (str): The unique heading of the post.
            user_id (int): The unique identifier of the user who created the post.
            text (Optional[str]): The text content of the post.
            image_urls (Optional[list[str]]): URLs of images attached to the post.

        Returns:
            Post: The Post object.
        """
        post_values = {
            "title": title,
            "user_id": user_id,
            "text": text,
            "images": [
                {"url": url} for url in image_urls
            ] if image_urls else None
        }

        insert_stmt = (
            insert(self.model)
            .values(**post_values)
            .on_conflict_do_update(
                index_elements=[Post.title],
                set_=dict(
                    title=title,
                ),
            )
            .returning(Post)
        )

        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def add_post(self,
                       text: str,
                       user_id: int,
                       channel_id: int,
                       image_urls: list[str]) -> None:

        post = Post(user_id=user_id,
                    text=text,
                    channel_id=channel_id)

        for image_url in image_urls:
            image = Image(url=image_url)
            post.images.append(image)

        self.session.add(post)
        await self.session.commit()

    async def get_all_posts(self,
                            user_id: int) -> ScalarResult[Post]:
        stmt = select(Post).where(
            Post.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_post(self, post_id: int) -> Post | None:
        stmt = select(Post).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_post_with_images(self, post_id: int) -> Post | None:
        stmt = select(Post).where(
            Post.id == post_id).options(selectinload(Post.images))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_post(self, post_id: int) -> None:
        post = await self.get_post_with_images(post_id)
        if post:
            for image in post.images:
                if image.url:
                    try:
                        os.remove(image.url)
                    except FileNotFoundError:
                        logging.info("IMAGE IS NOT FOUND")
                    except Exception as e:
                        logging.info(f"IMAGE DELETE ERROR: {e}")

            stmt = delete(Post).where(Post.id == post_id)
            await self.session.execute(stmt)
            await self.session.commit()
        return