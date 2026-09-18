import os

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from environs import Env

from dialogflow_handler import get_dialogflow_response


def main():
    env = Env()
    env.read_env()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = env.str("DIALOGFLOW_PROJECT_ID")

    vk_session = vk_api.VkApi(token=env.str("VK_GROUP_TOKEN"))
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print("Новое сообщение:")
            if event.from_me:
                print(f"От меня для: {event.user_id}")
            else:
                print(f"Для меня от: {event.user_id}")
                vk.messages.send(
                    user_id=event.user_id,
                    message=get_dialogflow_response(project_id, str(event.user_id), event.text),
                    random_id=0,
                )
            print(f"Текст: {event.text}")


if __name__ == "__main__":
    main()
