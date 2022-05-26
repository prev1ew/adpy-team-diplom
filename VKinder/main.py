import vk
import db as db_connection
import create_db
from settings import APP_ID


cache_file = dict()
# инициализация
# возможно следует переделать вк в класс

# чекаем бд, если пустая бд - создаем пустые таблицы
create_db.recreate_db_if_needed()

vk_client = vk.initialize_vk_client()
# vk_api = vk_client.get_api()
longpoll = vk.get_longpoll_from_vk(vk_client)

# стандартные кнопки для сообщения
kb_candidate_commands = vk.create_basic_keyboard()

help_message = 'Напишите команду "ищи людей" для начала поиска "кандидатов"'


def show_authorization_message(vk_cl, user_id, start_message=False):
    vk.write_msg(vk_cl, user_id,
                 f"{'Привет, д' if start_message else 'Д'}ля использования бота нужно пройти аутентификацию, ее можно пройти тут:\n"
                 f"https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups,offline&response_type=token&v=5.52\n"
                 f"После получения токена отправь его мне (лучше полную ссылку в браузерной строке)"
                 )


def make_msg_favorites(item_list):
    returning_value = ''
    for item in item_list:
        returning_value += vk.make_message_about_another_user(item) + '\n'
    return returning_value if returning_value else "Тут пока пусто, но это никогда не поздно исправить)"


def show_commands(vk_cl, user_id):
    vk.write_msg(vk_cl, user_id,
                 "Команды:\n"
                 "В избранное - добавить в избранное\n"
                 "Избранное - показать список избранного\n"
                 "Следующий - показать следующего")


while True:

    for event in longpoll.listen():
        if vk.is_event_equal_new_message(event.type):
            if event.to_me:

                # кто к нам обращается ---
                user_data = db_connection.get_user_data_from_db(event.user_id)
                if not user_data:  # if data not existed then
                    user_data = vk.get_user_data(vk_client, event.user_id)
                    db_connection.add_new_user_to_db(user_data)
                # --- кто к нам обращается

                request = event.text.lower()
                entered_access_token = request.find('access_token')

                if request == "start":

                    if user_data['user_token']:
                        vk.write_msg(vk_client, event.user_id, help_message)
                    else:
                        show_authorization_message(vk_client, event.user_id, True)
                elif request == 'restart':
                    user_data = vk.get_user_data(vk_client, event.user_id)
                    db_connection.update_user_info(user_data)

                    vk.write_msg(vk_client, event.user_id, f"Информация перезагружена\n{help_message}")
                elif user_data['city'] == 'None' or user_data['gender'] == 'None' or user_data['age'] == 0:
                    vk.write_msg(vk_client, event.user_id, "У тебя профиль не достаточно заполнен.\n"
                                                           "Проверь пожалуйста свои дату рождения, город, пол "
                                                           "и напиши команду 'restart'")
                elif request == "ищи людей" or request[:4] == "след":

                    # если был получен ранее нормальный токен
                    if user_data['user_token']:
                        vk.get_candidate(vk_client, user_data, event.user_id)
                        show_commands(vk_client, event.user_id)
                    else:
                        show_authorization_message(vk_client, event.user_id)
                elif request == "избранное":
                    vk.write_msg(vk_client, event.user_id,
                                 make_msg_favorites(
                                     db_connection.display_favorites(event.user_id))
                                 )
                    show_commands(vk_client, event.user_id)
                elif entered_access_token >= 0:  # -1 если не найден "аксес_токен"
                    # entered_access_token = позиция начала "аксес_токен"
                    start = entered_access_token + len('access_token=')
                    end = request.find('&', entered_access_token)
                    access_token = request[start:(end if end else 0)]
                    if 82 < len(access_token) < 87:
                        # тут было бы хорошо проверить токен на корректность перед записью
                        db_connection.update_user_token(event.user_id, access_token)
                        vk.write_msg(vk_client, event.user_id, f"Токен успешно сохранён!\n{help_message}")

                    # else:
                    #     vk.write_msg(vk_client, event.user_id, help_message)
                elif 82 < len(request) < 87:
                    # вероятнее всего человек написал только токен
                    # у моего токена была длина 85, я хз он меняется там или нет, поэтому взял с зазором
                    access_token = request
                    # тут было бы хорошо проверить токен на корректность перед записью
                    db_connection.update_user_token(event.user_id, access_token)
                    vk.write_msg(vk_client, event.user_id, f"Токен успешно сохранён!\n{help_message}")
                elif request[:5] == 'в изб':
                    current_user = vk.get_current(vk_client, user_data, event.user_id)
                    if current_user:
                        if db_connection.check_if_exist_in_favorite(event.user_id, current_user['id']):
                            vk.write_msg(vk_client, event.user_id, "Пользователь уже существует в бд!")
                        else:
                            db_connection.add_to_favorites(event.user_id, current_user)
                            vk.write_msg(vk_client, event.user_id, "Пользователь успешно сохранён в избранное!")
                    else:
                        vk.write_msg(vk_client, event.user_id, help_message)
                else:
                    vk.write_msg(vk_client, event.user_id, help_message)

        # callback не доходит
        # точка остановки не срабатывает при нажатии на кнопку (вообще)
        #
        # elif vk.is_event_equal_message_event(event.type):
        #     print('hey, I received a callback!')
        #     type_of_event = event.object.payload.get('type')
        #     if type_of_event == 'next':
        #         last_id = vk_api.messages.edit(
        #             peer_id=event.obj.peer_id,
        #             message='test',
        #             conversation_message_id=event.obj.conversation_message_id,
        #             keyboard=kb_candidate_commands)
