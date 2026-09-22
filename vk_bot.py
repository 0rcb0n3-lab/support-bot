import logging
import os
import time

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from environs import Env

from dialogflow_handler import get_dialogflow_response
from tg_logging import TelegramLogsHandler

logger = logging.getLogger(__name__)

RETRY_DELAY_SECONDS = 5


def send_reply(vk, project_id, user_id, text):
    try:
        reply, is_fallback = get_dialogflow_response(project_id, f"vk-{user_id}", text)
    except Exception:
        logger.exception("Ошибка при обработке сообщения от %s", user_id)
    else:
        if not is_fallback:
            vk.messages.send(user_id=user_id, message=reply, random_id=0)


def handle_event(project_id, vk, event):
    if event.type != VkEventType.MESSAGE_NEW:
        return

    print("Новое сообщение:")
    if event.from_me:
        print(f"От меня для: {event.user_id}")
    else:
        print(f"Для меня от: {event.user_id}")
        send_reply(vk, project_id, event.user_id, event.text)
    print(f"Текст: {event.text}")


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    tg_logs_handler = TelegramLogsHandler(
        env.str("TG_BOT_TOKEN"), env.str("TG_CHAT_ID")
    )
    tg_logs_handler.setLevel(logging.ERROR)
    tg_logs_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    logger.addHandler(tg_logs_handler)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    vk_session = vk_api.VkApi(token=env.str("VK_GROUP_TOKEN"))
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("Бот запущен")

    while True:
        try:
            for event in longpoll.listen():
                handle_event(project_id, vk, event)

        except (vk_api.VkApiError, requests.exceptions.RequestException):
            logger.exception("Сетевая ошибка, повтор через %s секунд", RETRY_DELAY_SECONDS)
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception:
            logger.exception("Бот упал, перезапуск")
            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    main()
