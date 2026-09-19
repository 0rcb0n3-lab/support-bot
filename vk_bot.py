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
                if event.type == VkEventType.MESSAGE_NEW:
                    print("Новое сообщение:")
                    if event.from_me:
                        print(f"От меня для: {event.user_id}")
                    else:
                        print(f"Для меня от: {event.user_id}")
                        try:
                            reply, is_fallback = get_dialogflow_response(
                                project_id, str(event.user_id), event.text
                            )
                        except Exception:
                            logger.exception(
                                "Ошибка при обработке сообщения от %s", event.user_id
                            )
                        else:
                            if not is_fallback:
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message=reply,
                                    random_id=0,
                                )
                    print(f"Текст: {event.text}")

        except (vk_api.VkApiError, requests.exceptions.RequestException):
            logger.exception("Сетевая ошибка, повтор через %s секунд", RETRY_DELAY_SECONDS)
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception:
            logger.exception("Бот упал, перезапуск")
            raise


if __name__ == "__main__":
    main()
