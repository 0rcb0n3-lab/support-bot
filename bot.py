import asyncio
import logging
import os

from environs import Env

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from google.cloud import dialogflow


def get_dialogflow_response(project_id: str, session_id: str, text: str, language_code="ru") -> str:
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text


async def main() -> None:
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.getLogger("aiogram").setLevel(logging.WARNING)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    bot = Bot(token=env.str("TG_BOT_TOKEN"))
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        logging.info("User %s started the bot", message.from_user.id)
        await message.answer("Здравствуйте")

    @dp.message()
    async def dialogflow_reply(message: Message) -> None:
        reply = get_dialogflow_response(
            project_id,
            str(message.from_user.id),
            message.text,
            "ru-RU",
        )
        if reply:
            await message.answer(reply)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
