import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


def mess_to_vk(title, content, text, feedback):
    vk_session = vk_api.VkApi(
        token='c1e9a18c2f9cc98787897315236570bc32299f98f74c50c4be5233a31cf21e3a391a1d69fc6d32e88dc06')

    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    vk.messages.send(user_id="322151958", random_id=get_random_id(),
                     message=f'''Просмотрите новую заявку на песню!
название песни: {title}

идея:
{content}

текст песни:
{text}

контакты:
{feedback}''')
