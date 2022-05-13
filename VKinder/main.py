import time
import vk
from db import add_new_user_to_db, get_user_data_from_db, add_to_favorites, display_favorites
from config import group_token

vk_client = vk.initialize_vk_client(group_token)
longpoll = vk.get_longpoll_from_vk(vk_client)
count = 0  # СЧЕТЧИК КАНДИДАТОВ
userAuthorized = False
firstSearch = True
help_message = 'Доступные команды:\n \
               старт - запустить бот / главное меню\n \
               ищи - найти партнера или показать следующего\n \
               изб - добавить в избранное\n \
               все - показать избранное'

while True:
    time.sleep(5)
    for event in longpoll.listen():

        if vk.is_event_equal_new_message(event.type):
            if event.to_me:

                if not userAuthorized:
                    user_data = get_user_data_from_db(event.user_id)
                    if user_data:  # ПРОВЕРЯЕМ ЕСТЬ ЛИ ПОЛЬЗОВАТЕЛЬ В БД
                        userAuthorized = True

                request = event.text.lower()

                if request == "старт" and not userAuthorized:
                    vk.write_msg(vk_client, event.user_id, "Введите токен")

                elif request == "старт" and userAuthorized:
                    current_user = dict()
                    vk.write_msg(vk_client, event.user_id, help_message)

                elif 82 < len(request) < 87:  # ЕСЛИ ВВЕДЕН ТОКЕН
                    user_data = vk.get_user_data(vk_client, event.user_id) # ЕСЛИ ПОЛЬЗОВАТЕЛЬ НЕ В БД, ПОЛУЧАЕМ ДАННЫЕ ИЗ ВК
                    user_data['user_token'] = request
                    add_new_user_to_db(user_data)
                    userAuthorized = True
                    vk.write_msg(vk_client, event.user_id, 'Пользователь/токен успешно сохранён. Введите команду "старт".')

                elif request == "ищи":  # ПОИСК ПЕРВОГО КАНДИДАТА ИЛИ ПЕРЕЙТИ К СЛЕДУЮЩЕМУ КАНДИДАТУ
                    vk_personal = vk.initialize_vk_client(user_data['user_token']) # ИНИЦИАЛИЗАЦИЯ ПЕРСОНАЛЬНОГО ТОКЕНА
                    if firstSearch:
                        result = vk.search_people(vk_personal, user_data) # users.search работает только с персональным токеном
                        number_of_partners = len(result['items'])
                        firstSearch = False
                    if count < number_of_partners:
                        current_user = result['items'][count]
                        message = vk.display_partner_info(current_user)
                        str_attachments = vk.find_photos(current_user['id'], vk_personal)
                        vk.write_msg(vk_client, event.user_id, message,{'attachment': str_attachments})
                        vk.write_msg(vk_client, event.user_id, 'Введите команду "изб" для добавления кандидата в избранное или "ищи" для продолжения поиска.')
                        count += 1
                    else:
                        count = 0
                        firstSearch = True
                        vk.write_msg(vk_client, event.user_id, 'Все кандидаты перебраны. Введите команду "старт", чтобы начать поиск заново.')

                elif request == "изб" and current_user:  # ДОБАВИТЬ В ИЗБРАННОЕ
                    user_info = vk.get_user_data(vk_client, current_user['id'])
                    user_info.update(current_user)
                    add_to_favorites(event.user_id, user_info, str_attachments)
                    current_user = dict()
                    vk.write_msg(vk_client, event.user_id,'Кандидат добавлен в избранное. Введите команду "старт" для возврата в главное меню.')

                elif request == "все":  # ПОКАЗАТЬ ИЗБРАННОЕ
                    favorites_list = display_favorites(event.user_id)
                    for item in favorites_list:
                        message = 'http://vk.com/id' + str(item[0]) + ' ' + item[1] + ' ' + item[2]
                        vk.write_msg(vk_client, event.user_id, message)
                    vk.write_msg(vk_client, event.user_id,'Введите команду "старт" для возврата в главное меню.')

                else:
                    vk.write_msg(vk_client, event.user_id, help_message)