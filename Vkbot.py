import vk_api
from config import count
from config import (
    explorer_scopes, explorer_data,
    all_partner_data, male_sex_terms,female_sex_terms,potential_relationships
)
from database import add_pair, check_pair_exist, create_database
from VkApi import VkApi


class VkBot(VkApi):

    def get_seeker_information(self) -> list:

        seeker, vk_event = self.listen_for_response()
        res = self.get_user_info(seeker)
        if not res:
            self.send_message(
                vk_event.user_id,
                "Извините, но указанный идентификатор не найден. Пожалуйста, проверьте правильность введенных данных "
                "и попробуйте еще раз. "
            )
            return self.get_seeker_information()

        return res

    def get_city_information(self) -> dict:
        """
        Повторно спрашиваем пользователя при неправильном вводе про город.

        """
        city, vk_event = self.listen_for_response()
        res = self.get_city_info(city)
        if res["count"] == 0:
            self.send_message(
                vk_event.user_id,
                "К сожалению, информация о таком городе недоступна"
            )
            res = self.get_city_information()

        return res

    def validate_birthdate(self) -> str:

        date, vk_event = self.listen_for_response()
        try:
            date = int(date)
        except ValueError:
            self.send_message(
                vk_event.user_id,
                "Введите полный год рождения в формате ГГГГ"
            )
            date = self.validate_birthdate()

        if date not in range(1900, 2023):
            self.send_message(
                vk_event.user_id,
                "Пожалуйста, введите год рождения в формате ГГГГ (например, 1990)"
            )
            date = self.validate_birthdate()

        return date

    def validate_gender(self) -> str:

        sex, vk_event = self.listen_for_response()
        if sex in female_sex_terms:
            sex = "1"
        elif sex in male_sex_terms:
            sex = "2"
        else:
            self.send_message(
                vk_event.user_id,
                "Пожалуйста, введите пол::\n1 - женский\n2 - мужской"
            )
            sex = self.validate_gender()

        return sex

    def validate_relationship_status(self) -> str:

        relation, vk_event = self.listen_for_response()
        if relation in potential_relationships:
            return relation

        self.send_message(
            vk_event.user_id,
            "Пожалуйста, введите цифру от 0 до 8 включительно, в соответствии с указанными выше вариантами"
        )
        relation = self.validate_relationship_status()

        return relation

    def validate_information_completeness(
            self, seeker_scopes: list, info: list,
            vk_event: vk_api.longpoll.Event) -> dict:

        for elem in seeker_scopes:
            if elem in info[0].keys():
                if elem == "bdate":

                    if len(info[0]["bdate"].split(".")) < 3:
                        self.send_message(
                            vk_event.user_id,
                            "Извините за недостаток информации. Пожалуйста, предоставьте дополнительные детали или "
                            "уточните, что именно вам требуется, чтобы я мог помочь вам правильно "
                        )
                        self.send_message(
                            vk_event.user_id,
                            "Введите полный год рождения (например: 1990)"
                        )
                        explorer_data["bdate"] = self.validate_birthdate()
                    else:
                        explorer_data["bdate"] = info[0]["bdate"].split(".")[2]

                elif elem == "sex":
                    explorer_data["sex"] = info[0].get("sex")

                elif elem == "city":
                    explorer_data["city_id"] = info[0].get("city").get("id")
                    explorer_data["city"] = info[0].get("city").get("title")

                elif elem == "relation":
                    explorer_data["relation"] = info[0].get("relation")

            else:
                self.send_message(vk_event.user_id, "Не хватает информации!")
                if elem == "bdate":
                    self.send_message(
                        vk_event.user_id,
                        "Введите полный год рождения (например: 1977)"
                    )
                    explorer_data["bdate"] = self.validate_birthdate()

                elif elem == "sex":
                    self.send_message(
                        vk_event.user_id,
                        "Введите пол\n1 - женский\n2 - мужской"
                    )
                    explorer_data["sex"] = self.validate_gender()

                elif elem == "city":
                    self.send_message(vk_event.user_id, "Пожалуйста, введите название города:")
                    city_info = self.get_city_information()
                    explorer_data["city"] = city_info["items"][0]["title"]
                    explorer_data["city_id"] = city_info["items"][0]["id"]

                elif elem == "relation":
                    self.send_message(
                        vk_event.user_id,
                        """Введите cемейное положение:
                        1 — не женат/не замужем
                        2 — есть друг/есть подруга
                        3 — помолвлен/помолвлена
                        4 — женат/замужем
                        5 — всё сложно
                        6 — в активном поиске
                        7 — влюблён/влюблена
                        8 — в гражданском браке
                        0 — не указано"""
                    )
                    explorer_data["relation"] = self.validate_relationship_status()

        return explorer_data

    def find_matching_couples(
            self, bdate: int, sex: int, city_id: int, relation: str,
            count: int,offset: int) -> list:
        """Находим подходящих людей"""
        if int(sex) == 1:
            sex = 2
        else:
            sex = 1
        couples = self.search_users(bdate, sex, city_id, relation, count, offset)

        all_partner_data = []
        for elem in couples["items"]:
            couple_info_temp = {"first_name": elem["first_name"], "last_name": elem["last_name"], "id": elem["id"]}
            all_partner_data.append(couple_info_temp)

        return all_partner_data

    def show_couple_information(self, couple_info: dict) -> str:
        """Собираем пользователю информацию о подходящей паре"""
        try:
            res = (
                f"{couple_info['first_name']} {couple_info['last_name']}\n"
                f"https://vk.com/id{couple_info['id']}"
            )

            return res
        except vk_api.ApiError as e:
            print(f"Произошла ошибка VK API: {str(e)}")
            return []

    def get_photos(self, couple_id: int) -> str:

        try:
            photos_info = self.photos_get(couple_id)
        except vk_api.exceptions.ApiError:
            return "closed profile"  # У этого человека закрытый профиль

        photos_amount = photos_info["count"]
        photos_info_dict = dict()
        photo_urls_list = list()

        if photos_amount < 3:
            return "low_anount"  # У этого человека кол-во фото меньше 3
        elif photos_amount > 50:
            photos_amount = 50

        for i in range(photos_amount):
            photos_info_dict[photos_info["items"][i]["id"]] = (
                    photos_info["items"][i]["likes"]["count"]
                    + photos_info["items"][i]["comments"]["count"]
            )

        sorted_photos_dict = dict(
            sorted(photos_info_dict.items(), key=lambda x: -x[1])
        )
        photos_ids = list(sorted_photos_dict.keys())

        for i in range(3):
            photo_id = photos_ids[i]
            photo_url = (
                f"https://vk.com/id{couple_id}?"
                f"z=photo{couple_id}_{photo_id}"
                f"%2Falbum{couple_id}_0%2Frev"
            )
            photo_urls_list.append(photo_url)
            photo_urls_str = "\n".join(photo_urls_list)

        return photo_urls_str

    def search_for_user_input(self) -> str:
        """
        Отправляет напоминание, что может сделать юзер во время поиска пары.

        """
        user_answer, vk_event = self.listen_for_response()
        if user_answer == "далее":
            return "next"
        elif user_answer == "остановить":
            return "stop"
        else:
            self.send_message(
                vk_event.user_id,
                'Извините за неудобство. Давайте продолжим. Пожалуйста, продолжайте со следующим шагом,'
                'написав "далее". Сообщите "остановить", если хотите прекратить общение '
            )
            res = self.search_for_user_input()

        return res

    def vkbot_logic(self) -> None:

        request, vk_event = self.listen_for_response()

        if request == "привет":

            self.send_message(vk_event.user_id, f"Хай, {vk_event.user_id}")
            self.send_message(
                vk_event.user_id,
                """Вот мои команды:
                Найди пару - начать поиск пары
                Пока - завершить работу
                """)

            create_database()

        elif request == "пока":
            # Прощаемся с ботом и завершаем его работу
            # Для возобновления работы необходимо повторно запустить скрипт
            self.send_message(vk_event.user_id, "Пока((")
            quit()

        elif request == "найди пару":
            # Обнуляем предыдущий поиск.
            # Уже выданные пользователи сохранены в БД.
            couple_info_list = list()
            offset = 0  # Смещение для следующего запроса

            # Собираем информацию от пользователя
            self.send_message(
                vk_event.user_id,
                "Введите id пользователя"
            )
            resp = self.get_seeker_information()

            # Проверяем чего не хватает
            self.validate_information_completeness(explorer_scopes, resp, vk_event)
            self.send_message(vk_event.user_id, "Информации достаточно,чтобы найти пару")

            # Ищем пользователю подходящих людей предоставленной информации
            while len(couple_info_list) < count:
                couple_info_list += self.find_matching_couples(
                    explorer_data["bdate"],
                    explorer_data["sex"],
                    explorer_data["city_id"],
                    explorer_data["relation"],
                    count,
                    offset
                )
                offset += count

            for elem in couple_info_list:

                if check_pair_exist(elem.get("id")):
                    self.send_message(
                        vk_event.user_id,
                        "Этот человек уже был. Продолжим поиск..."
                    )
                    continue
                else:
                    add_pair(elem.get("id"))

                # Выдаём результат
                show_str = self.show_couple_information(elem)
                self.send_message(vk_event.user_id, f"{show_str}")
                res_get_photos = self.get_photos(elem.get('id'))
                if res_get_photos == "closed profile":
                    self.send_message(
                        vk_event.user_id,
                        "У этого человека закрытый профиль, но он подходит. \
                        Может быть захотите связаться с ним?.."
                    )
                    continue
                elif res_get_photos == "low_anount":
                    self.send_message(
                        vk_event.user_id,
                        "У этого человека недостаточно фотографий профиля."
                    )
                    continue
                else:
                    self.send_message(vk_event.user_id, f"{res_get_photos}")

                # Спрашиваем выдавать ли ещё результаты
                self.send_message(
                    vk_event.user_id,
                    "Хотите увидеть следующего человека? Напишите: далее"
                )
                self.send_message(
                    vk_event.user_id,
                    "Если хотите на этом закончить, напишите: остановить"
                )
                res = self.search_for_user_input()
                if res == "next":
                    continue
                elif res == "stop":
                    break

            self.send_message(
                vk_event.user_id,
                "Возвращайтесь в любое время, и я с удовольствием буду помогать вам. Удачи!"
            )

        else:
            self.send_message(vk_event.user_id, "Не понял вашего ответа...")
            self.send_message(vk_event.user_id, """Вот мои команды:
            Найди пару - начать поиск пары
            Пока - завершить работу 
            """)