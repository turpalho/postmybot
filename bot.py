"""Main module for the bot."""
import asyncio
import logging
import pathlib

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import Config, load_config
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.apscheduler_middleware import SchedulerMiddleware
from tgbot.misc.logging import LoggingPackagePathFilter
from tgbot.services import broadcaster
from tgbot.handlers import routers_list

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, admin_ids: list[int]):
    """
    Send a message to the admin users when the bot is started.

    Args:
        bot (Bot): The bot instance.
        admin_ids (list[int]): The list of admin user ids.
    """
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен")


def register_global_middlewares(dp: Dispatcher,
                                config: Config,
                                scheduler: AsyncIOScheduler,
                                session_pool):
    """
    Register global middlewares for the given dispatcher.

    Args:
        dp (Dispatcher): The dispatcher instance.
        config (Config): The configuration object from the loaded configuration.
        session_pool: Session pool object for the database using SQLAlchemy.
    """
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_pool),
        SchedulerMiddleware(scheduler),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)
        dp.inline_query.outer_middleware(middleware_type)
        dp.my_chat_member.outer_middleware(middleware_type)
        # dp.chat_member.outer_middleware(middleware_type)


def setup_logging(config: Config):
    """
    Set up logging configuration for the application.

    The function sets up logging for production and development environments.
    If the environment is development, the function sets up logging to the console
    with the package path filter.
    Otherwise, the function sets up logging to the file.

    Args:
        config (Config): The configuration object.

    Example usage:
        setup_logging(config)
    """
    logger = logging.getLogger(__name__)

    if config.environment == "dev":
        # note - didn't find a way to set the filter in BasicConfig, so I used loggerDict
        package_filter = LoggingPackagePathFilter()
        loggers_names = [
            name
            for name in logging.root.manager.loggerDict] + ["root"]
        for logger_name in loggers_names:
            logging.getLogger(logger_name).addFilter(package_filter)

        # setup logging configuration for dev environment with StreamHandler
        log_format = "%(pathname)s:%(lineno)s [%(name)s]: %(message)s"
        formatter = logging.Formatter(log_format)
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(formatter)
        handlers = [log_handler]
    else:
        # define logs directory, path to logs file and create logs directory if it does not exist   # noqa: E501
        logs_directory = pathlib.Path("logs")
        logs_path = logs_directory / "logs.txt"
        pathlib.Path(logs_directory).mkdir(parents=True, exist_ok=True)

        # setup logging configuration for prod environment with FileHandler
        log_handler = logging.FileHandler(logs_path, mode="a")
        log_format = "%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"  # noqa: E501
        formatter = logging.Formatter(log_format)
        log_handler.setFormatter(formatter)
        handlers = [log_handler]
        # reduce aiogram logging level
        logging.getLogger("aiogram").setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers,
    )

    logger.info("Starting bot in %s environment", config.environment)


def get_storage(config: Config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True,
                                          with_destiny=True),
        )
    return MemoryStorage()


async def restore_config(config: Config, session_pool) -> None:
    async with session_pool() as session:
        repo = RequestsRepo(session)
        config_parameters = await repo.configs.get_config_parameters()
        if config_parameters:
            admin_ids = [int(admin_id)
                         for admin_id
                         in config_parameters.admins_ids.split(",")]
            config.tg_bot.admin_ids = admin_ids

            if config_parameters.subadmins_ids:
                subadmin_ids = [
                    int(subadmin_id)
                    for subadmin_id in config_parameters.subadmins_ids.split(",")]
                config.tg_bot.subadmins_ids = subadmin_ids
        else:
            await repo.configs.create_config(config.tg_bot.admin_ids)


async def main():
    """Start the project."""
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    config = load_config(".env")
    # setup_logging(config)
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)

    # We register regular routers
    dp.include_routers(*routers_list)

    engine = await create_engine(config.db, echo=False)
    session_pool = create_session_pool(engine)
    await restore_config(config, session_pool)

    # scheduler = AsyncIOScheduler(timezone="Europe/Berlin")
    scheduler = AsyncIOScheduler()
    scheduler.start()
    register_global_middlewares(dp, config, scheduler, session_pool)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot,
                           allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот был запущен!")
