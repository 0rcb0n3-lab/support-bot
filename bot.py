import asyncio
import logging

from environs import Env

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message


async def main() -> None:
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.getLogger("aiogram").setLevel(logging.WARNING)

    bot = Bot(token=env.str("TG_BOT_TOKEN"))
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        logging.info("User %s started the bot", message.from_user.id)
        await message.answer("Здравствуйте")

    @dp.message()
    async def echo(message: Message) -> None:
        await message.answer(message.text)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
