import time
import vk
import listener
from threading import Thread
import db as db_connection
import create_db

APP_ID = '8158966'

# инициализация
# возможно следует переделать вк в класс

# чекаем бд, если пустая бд - создаем пустые таблицы
create_db.recreate_db_if_needed()

vk_client = vk.initialize_vk_client()
longpoll = vk.get_longpoll_from_vk(vk_client)


access_token = ''
user_data = ''
# присутствует временно
# удалить сразу после функций записи/чтения токена из бд
tmp_token = ''
# ---
#

# стандартные кнопки для сообщения
kb_candidate_commands = vk.create_basic_keyboard()

help_message = 'Напишите команду "ищи людей" для начала поиска "кандидатов"'


def show_authorization_message(vk_cl, user_id, start_message=False):
    vk.write_msg(vk_cl, user_id,
                 f"{'Привет, д' if start_message else 'Д'}ля использования бота нужно пройти аутентификацию, ее можно пройти тут:\n"
                 f"https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups,offline&response_type=token&v=5.52\n"
                 f"После получения токена отправь его мне (лучше полную ссылку в браузерной строке)"
                 )


while True:
    time.sleep(5)

    for event in longpoll.listen():
        if vk.is_event_equal_new_message(event.type):
            if event.to_me:

                # кто к нам обращается ---
                # TODO: каждый раз обращаться в бд не есть разумным, нужно подумать об альтернативе
                # TODO Sergey: вроде бы поправил все, но все же чекни ли все ок с строкой ниже
                user_data = db_connection.get_user_data_from_db(event.user_id)
                if not user_data:  # if data not existed then
                    user_data = vk.get_user_data(vk_client, event.user_id)
                    db_connection.add_new_user_to_db(user_data)
                # --- кто к нам обращается

                request = event.text.lower()
                entered_access_token = request.find('access_token')
                # TODO: прикрутить кнопки

                if request == "start":
                    # event.user_id = ид юзера (вк), его можно использовать для поиска
                    # т.е. если пользователь без токена пишет "старт"
                    if user_data['user_token']:
                        vk.write_msg(vk_client, event.user_id, help_message)
                    else:
                        show_authorization_message(vk_client, event.user_id, True)

                elif request == "ищи людей":

                    # если был получен ранее нормальный токен
                    if user_data['user_token']:
                        vk_personal = vk_client = vk.initialize_vk_client(user_data['user_token'])
                        result = vk.search_people(vk_personal, user_data)
                        # вот мы нашли людей, в теории тут нужно что-то с ими делать (пока не придумал)
                        # TODO: доработать механизм
                        current_user = result['items'][1]
                        # !метод работает только с персональным токеном
                        message = vk.make_message_about_another_user(current_user)
                        str_attachments = vk.find_photos(current_user['id'], vk_personal)
                        # тут короче фигня какая-то
                        # после получения vk_personal vk_client ломается
                        # поэтому я его тут повторно инициализирую
                        # TODO: найти альтернативу строчке ниже
                        vk_client = vk.initialize_vk_client()
                        # TODO: прикрепить кнопки (в тек момент там только 1 кнопка и то не та что нужно)
                        # TODO: доработать "отклик" при нажатии на кнопки
                        vk.write_msg(vk_client, event.user_id, message,
                                     {
                                         'attachment': str_attachments,
                                         'keyboard': kb_candidate_commands.get_keyboard()
                                     })
                        # сейчас вывожу просто первого юзера чисто разработать механизм
                        # TODO: придумать алгоритм вывода "кандидатов"
                    else:
                        show_authorization_message(vk_client, event.user_id)

                elif entered_access_token >= 0:  # -1 если не найден "аксес_токен"
                    # entered_access_token = позиция начала "аксес_токен"
                    start = entered_access_token + len('access_token=')
                    end = request.find('&', entered_access_token)
                    if 82 < len(access_token) < 87:
                        access_token = request[start:(end if end else 0)]
                        db_connection.update_user_token(event.user_id, access_token)
                        vk.write_msg(vk_client, event.user_id, "Токен успешно сохранён!")
                    # else:
                    #     vk.write_msg(vk_client, event.user_id, help_message)
                elif 82 < len(request) < 87:
                    # вероятнее всего человек написал только токен
                    # у моего токена была длина 85, я хз он меняется там или нет, поэтому взял с зазором
                    access_token = request
                    db_connection.update_user_token(event.user_id, access_token)
                    vk.write_msg(vk_client, event.user_id, "Токен успешно сохранён!")
                # удалить при готовности
                elif request == 'restart':
                    pass
                # --- удалить
                else:
                    vk.write_msg(vk_client, event.user_id, help_message)
