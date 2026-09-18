import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from environs import Env


def main():
    env = Env()
    env.read_env()

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
                    user_id=event.user_id, message=event.text, random_id=0
                )
            print(f"Текст: {event.text}")


if __name__ == "__main__":
    main()
