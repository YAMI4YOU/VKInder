from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import explorer_fields, group_token, access_token


class VkApi:

    def __init__(self) -> None:
        """Инициализируем работу с АПИ"""
        self.vk_group = vk_api.VkApi(token=group_token)
        self.vk_seeker = vk_api.VkApi(token=access_token)
        self.longpoll = VkLongPoll(self.vk_group)

    def listen_for_response(self) -> tuple:
        """Слушаем ответ от пользователя"""
        try:
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        text = event.text.lower()

                        return text, event
        except vk_api.ApiError as e:
            print(f"Произошла ошибка VK API: {str(e)}")
            return []

    def send_message(self, user_id: str, message: str) -> int:
        """Ответ бота"""
        try:
            res = self.vk_group.method(
                "messages.send",
                {
                    "user_id": user_id,
                    "message": message,
                    "random_id": randrange(10 ** 7),
                }
            )
            return res
        except vk_api.ApiError as e:
            print(f"Произошла ошибка VK API: {str(e)}")
            return []

    def get_user_info(self, seeker: str) -> list:
        """Собираем информацию о пользователе"""
        try:
            res = self.vk_group.method(
                "users.get",
                {
                    "user_ids": seeker,
                    "fields": explorer_fields,
                }
            )
            return res
        except vk_api.ApiError as e:
            print(f"Произошла ошибка VK API: {str(e)}")
            return []

    def search_users(
            self, bdate: int, sex: int, city_id: int, relation: int,
            count: int, offset: int) -> dict:
        """Ищем подходящие пары для пользователя"""
        try:
            res = self.vk_seeker.method(
                "users.search",
                {
                    "fields": explorer_fields,
                    "city": city_id,
                    "sex": sex,
                    "count": count,
                    "offset": offset,
                    "status": relation,
                    "birth_year": bdate,
                    "has_photo": 1
                }
            )
            return res
        except vk_api.ApiError as e:
            print(f"Произошла ошибка VK API: {str(e)}")
            return []

    def get_city_info(self, city: str) -> dict:
        """Находим id города по его названию"""
        try:
            res = self.vk_seeker.method("database.getCities", {"q": city, })
            return res
        except vk_api.ApiError as e:
            print(f"Произошла ошибка VK API: {str(e)}")
            return []

    def photos_get(self, couple_id: int) -> dict:
        """Получает информацию о фотографиях пары"""
        res = self.vk_seeker.method(
                "photos.get",
                {
                    "owner_id": couple_id,
                    "album_id": "profile",
                    "rev": 1,
                    "extended": 1
                }
            )
        return res
