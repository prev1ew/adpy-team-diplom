from datetime import date
from random import randrange
import vk_api
from vk_api.bot_longpoll import VkBotEventType
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from operator import itemgetter


def initialize_vk_client(token=''):
    if not token:
        # group_token
        token = '0958750174482253c31483e132a96c88aa890529dfe797f60e04beb97f8522441c78629e31f280bcd644c'
    return vk_api.VkApi(token=token)


def get_longpoll_from_vk(vk):
    return VkLongPoll(vk)


def write_msg(vk, user_id, message, additional_parameters=None):
    main_headers = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    }

    vk.method('messages.send',
              main_headers | additional_parameters if additional_parameters else main_headers)


def calc_user_age(bdate):
    list_date = bdate.split('.')
    today = date.today()
    age = today.year - int(list_date[2]) - 1
    if today.month > int(list_date[1]) and today.day > int(list_date[0]):
        age += 1
    return age


def get_user_data(vk, user_id):
    res = vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate, city, sex'})
    info = dict()
    info['gender'] = 'M' if res[0]['sex'] == 2 else 'W'
    # сити - словарь состоящий из id и title
    info['city'] = res[0]['city']['id']
    info['age'] = calc_user_age(res[0]['bdate'])
    info['id'] = user_id
    info['user_token'] = ''
    # прикрутить статус (в поиске или что там)
    # хотя в задаче нечего не говорится про статус, поэтому оставляю на будущее
    return info


def select_age(age, gender):
    # парням помоложе
    # девушкам постарше
    if gender == 'W':
        age_from = age
        age_to = age + 3
    else:
        age_from = age - 3
        age_to = age
    return [age_from, age_to]


def search_people(vk, info):
    age_from_to = select_age(info['age'], info['gender'])
    res = vk.method('users.search', {
        'city': info['city'],
        # 2 = mens, 1 = women
        'sex': 1 if info['gender'] == 'M' else 2,
        'age_from': age_from_to[0],
        'age_to': age_from_to[1],
        # прикрутить статус (в поиске или что там)
        # хотя в задаче нечего не говорится про статус, поэтому оставляю на будущее
    })
    return res


def is_event_equal_new_message(event_type):
    return event_type == VkEventType.MESSAGE_NEW


def is_event_equal_message_event(event_type):
    return event_type == VkBotEventType.MESSAGE_EVENT


def change_token(vk, new_token):
    vk = vk_api.VkApi(token=new_token)


def make_message_about_another_user(user_to_show):
    return f"{user_to_show['first_name']} {user_to_show['last_name']}\n" \
           f"https://vk.com/id{user_to_show['id']}"


def sort_by_likes(items):
    return sorted(items, key=lambda k: k['likes']['count'], reverse=True)


def find_photos(user_id, vk_client):
    try:
        # TODO: добавить сортировку фоток по лайкам
        photos = vk_client.method('photos.get', {'owner_id': user_id, 'extended': '1', 'album_id': 'profile'})
        max_count = 3
        curr_photo_num = 0
        returning_value = ''
        for photo in sort_by_likes(photos['items']):
            curr_photo_num += 1
            if curr_photo_num > max_count:
                break
            returning_value += f'photo{photo["owner_id"]}_{photo["id"]},'
    except Exception as ex:
        # сюда в основном попадаем когда профиль приватный
        return None

    return returning_value


def create_basic_keyboard():
    settings = dict(one_time=True, inline=False, )
    keyboard = VkKeyboard(**settings)
    keyboard.add_callback_button(label='Следующий',
                                 color=VkKeyboardColor.PRIMARY, payload={"type": "next"})
    keyboard.add_line()
    keyboard.add_callback_button(label='В избранное',
                                 color=VkKeyboardColor.POSITIVE, payload={"type": "add_to_favorite"})
    keyboard.add_callback_button(label='Список избранного',
                                 color=VkKeyboardColor.SECONDARY, payload={"type": "show_favorite"})
    keyboard.add_line()
    keyboard.add_callback_button(label='Выход',
                                 color=VkKeyboardColor.NEGATIVE, payload={"type": "exit"})
    return keyboard


def cache_values(func):
    cached_data = dict()
    # словарь со списками

    def new_func(vk_client, user_data, user_id, pointer=0):

        records = cached_data.get(user_id)
        if records:
            pointer = records[0]
            res = func(vk_client, user_data, user_id, records[1][pointer])

        else:
            pointer = 0
            vk_personal = initialize_vk_client(user_data['user_token'])
            candidate_list = search_people(vk_personal, user_data)['items']

            res = func(vk_client, user_data, user_id, candidate_list[pointer])
            cached_data[user_id] = [0, candidate_list]

        cached_data[user_id][0] = pointer + 1

        return res

    return new_func


@cache_values
def get_candidate(vk_client, user_data, user_id, candidate_info):
    # логика подбора кандидатов находится в декораторе
    vk_personal = initialize_vk_client(user_data['user_token'])

    # current_candidate = get_next_candidates_info(vk_personal, user_data)

    message = make_message_about_another_user(candidate_info)
    str_attachments = find_photos(candidate_info['id'], vk_personal)

    # после получения vk_personal vk_client ломается
    # поэтому я его тут повторно инициализирую
    # TODO: найти альтернативу строчке ниже
    vk_client = initialize_vk_client()

    # TODO: callback не работает, чекнуть что не так и поправить
    write_msg(vk_client, user_id, message + ("\n <private profile, can't get photos>" if not str_attachments else ''),
              {
                  'attachment': str_attachments,
                  # клаву убрал так как нет смысла
                  # 'keyboard': kb_candidate_commands.get_keyboard()
              } if str_attachments else None)
