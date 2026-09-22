import asyncio
import logging
import os

from environs import Env

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import ErrorEvent, Message

from dialogflow_handler import get_dialogflow_response
from tg_logging import TelegramLogsHandler

logger = logging.getLogger(__name__)

RETRY_DELAY_SECONDS = 5


async def main() -> None:
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.getLogger("aiogram").setLevel(logging.WARNING)

    tg_bot_token = env.str("TG_BOT_TOKEN")
    tg_chat_id = env.str("TG_CHAT_ID")

    tg_logs_handler = TelegramLogsHandler(tg_bot_token, tg_chat_id)
    tg_logs_handler.setLevel(logging.ERROR)
    tg_logs_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    logger.addHandler(tg_logs_handler)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    bot = Bot(token=tg_bot_token)
    dp = Dispatcher()

    @dp.errors()
    async def on_aiogram_error(event: ErrorEvent) -> None:
        logger.exception("Ошибка при обработке апдейта: %s", event.exception)

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        logger.info("User %s started the bot", message.from_user.id)
        await message.answer("Здравствуйте")

    @dp.message()
    async def dialogflow_reply(message: Message) -> None:
        try:
            reply, _ = get_dialogflow_response(
                project_id,
                str(message.from_user.id),
                message.text,
                "ru-RU",
            )
        except Exception:
            logger.exception("Ошибка при обработке сообщения от %s", message.from_user.id)
        else:
            if reply:
                await message.answer(reply)

    while True:
        try:
            await dp.start_polling(bot)
        except Exception:
            logger.exception("Бот упал, перезапуск")
            await asyncio.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
