from datetime import date
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import SEARCH_RESULTS_COUNT

def initialize_vk_client(token):
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
    print(res)
    info = dict()
    info['id'] = user_id
    info['user_token'] = ''
    info['bdate'] = res[0]['bdate']
    info['age'] = calc_user_age(res[0]['bdate'])
    info['gender'] = 'M' if res[0]['sex'] == 2 else 'W'
    # ЭТОТ КУСОК КОДА НАДО ПОТОМ ПОПРАВИТЬ, ПОЧЕМУ-ТО МЕТОД users.get ВЫДАЕТ ПОЛЬЗОВАТЕЛЯ БЕЗ ГОРОДА
    if 'city' in res[0]:
        info['city'] = res[0]['city']  # city - словарь состоящий из id и title
    else:
        info['city'] = {'id': 999, 'title': 'Город не указан'}
    # ----------------------------------------------------------------------------------------------
    return info

def select_age(age, gender):
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
        'city': info['city_id'],
        'sex': 1 if info['gender'] == 'M' else 2,
        'age_from': age_from_to[0],
        'age_to': age_from_to[1],
        'count': SEARCH_RESULTS_COUNT
    })
    return res

def is_event_equal_new_message(event_type):
    return event_type == VkEventType.MESSAGE_NEW

def change_token(vk, new_token):
    vk = vk_api.VkApi(token=new_token)

def display_partner_info(user_to_show):
    return f"{user_to_show['first_name']} {user_to_show['last_name']}\n" \
           f"https://vk.com/id{user_to_show['id']}"

def find_photos(user_id, vk_client):
    try:
        photos = vk_client.method('photos.get', {'owner_id': user_id, 'extended': '1', 'album_id': 'profile'})
        max_count = 3
        curr_photo_num = 0
        returning_value = ''
        for photo in photos['items']:
            curr_photo_num += 1
            if curr_photo_num > max_count:
                break
            returning_value += f'photo{photo["owner_id"]}_{photo["id"]},'
    except Exception as ex:
        return f"<can't get photos, error: {ex}>"
    return returning_value