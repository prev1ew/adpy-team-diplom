import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import hostname, database, username, pwd, port_id

def connect_to_db():
    connection = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    return connection

def execute_sql(sql_script: str, returnResults: bool):
    connection = connect_to_db()
    try:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_script)
        if returnResults:
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def add_new_user_to_db(user_info: dict):
    insert_script = f'''INSERT INTO users VALUES(
    {user_info["id"]},
    '{user_info["user_token"]}',
    '{user_info["bdate"]}',
    {user_info["age"]},
    '{user_info["gender"]}',
    {user_info["city"]["id"]},
    '{user_info["city"]["title"]}'
    )'''
    execute_sql(insert_script, False)

def get_user_data_from_db(user_id: str):
    select_script = f"SELECT * FROM users WHERE user_id = '{user_id}'"
    total_res = execute_sql(select_script, True)
    if total_res:
        res = total_res[0]
        return {'user_id': res[0], 'user_token': res[1], 'age': res[3], 'gender': res[4], 'city_id': res[5]}
    else:
        return None

def add_to_favorites(user_id: str, partner_data: dict, pict_ref: str):

    photos_ref_1 = ''
    photos_ref_2 = ''
    photos_ref_3 = ''

    if pict_ref != '' and 'error' not in pict_ref:
        pict_ref_stripped = pict_ref[:-1]
        photos = pict_ref_stripped.split(',')

        if len(photos) == 1:
            photos_ref_1 = 'http:/vk.com/' + photos[0]
        elif len(photos) == 2:
            photos_ref_1 = 'http:/vk.com/' + photos[0]
            photos_ref_2 = 'http:/vk.com/' + photos[1]
        else:
            photos_ref_1 = 'http:/vk.com/' + photos[0]
            photos_ref_2 = 'http:/vk.com/' + photos[1]
            photos_ref_3 = 'http:/vk.com/' + photos[2]

    insert_script_partners = f'''INSERT INTO partners VALUES(
    '{partner_data["id"]}',
    '{partner_data["first_name"]}',
    '{partner_data["last_name"]}',
    '{partner_data["bdate"]}',
    {partner_data["age"]},
    '{partner_data["gender"]}',
    '{partner_data["city"]["id"]}',
    '{partner_data["city"]["title"]}',
    '{photos_ref_1}',
    '{photos_ref_2}',
    '{photos_ref_3}'
    )'''
    execute_sql(insert_script_partners, False)

    insert_script_favorites = f'''INSERT INTO favorites VALUES(
       '{partner_data["id"]}',
       '{user_id}'
       )'''
    execute_sql(insert_script_favorites, False)

def display_favorites(user_id: str):
    sql_script = f'''SELECT partners.partner_id, first_name, last_name, age, gender, city
    FROM partners
    JOIN favorites ON favorites.partner_id = partners.partner_id
    WHERE favorites.user_id = '{user_id}'
    '''
    return execute_sql(sql_script, True)