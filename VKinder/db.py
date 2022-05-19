import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from settings import db_settings


def connect_to_db():
    return psycopg2.connect(host=db_settings['hostname'],
                            dbname=db_settings['database'],
                            user=db_settings['username'],
                            password=db_settings['pwd'],
                            port=db_settings['port_id'])


def execute_sql(sql_script: str, returnResults: bool = False):
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
    # поменял user_id на id
    # в сити помещается идентификатор города, а не сам город
    insert_script = f'''INSERT INTO users VALUES(
    '{user_info["id"]}',
    '{user_info["user_token"]}',
    {user_info["age"]},
    '{user_info["gender"]}',
    '{user_info["city"]}'
    )'''
    execute_sql(insert_script, False)


def get_user_data_from_db(user_id: str):
    select_script = f"SELECT * FROM users WHERE user_id = '{user_id}'"
    total_res = execute_sql(select_script, True)
    # total_res = None in some cases
    if total_res:
        res = total_res[0]
        return {'id': res[0], 'user_token': res[1], 'age': res[2], 'gender': res[3], 'city': res[4]}
    else:
        return None


def add_to_favorites(user_id: str, partner_data: dict):
    # внес правки под то, что передаю
    insert_script_favorites = f'''INSERT INTO favorites VALUES(
    '{partner_data["id"]}',
    '{user_id}'
    )'''
    execute_sql(insert_script_favorites, False)
    p_age = partner_data.get("age")
    p_city = partner_data.get("city")
    if p_city:
        p_city = p_city['id']
    else:
        p_city = 'None'

    insert_script_partners = f'''INSERT INTO partners VALUES(
    '{partner_data["id"]}',
    '{partner_data["first_name"]}',
    '{partner_data["last_name"]}',
    {p_age if p_age else 0},
    '{partner_data.get("gender")}',
    '{p_city}',
    '{partner_data.get("photo_ref1")}',
    '{partner_data.get("photo_ref2")}',
    '{partner_data.get("photo_ref3")}'
    )'''
    execute_sql(insert_script_partners, False)


def display_favorites(user_id: str):
    sql_script = f'''SELECT partners.partner_id, first_name, last_name, age, gender, city
    FROM partners
    JOIN favorites ON favorites.partner_id = partners.partner_id
    WHERE favorites.user_id = '{user_id}'
    '''
    return execute_sql(sql_script, True)


def update_user_token(user_id, new_token):
    sql_script = f'''UPDATE users
        SET user_token = '{new_token}'
        WHERE user_id = '{user_id}'
        '''
    execute_sql(sql_script)


def check_if_exist_in_favorite(user_id, partner_id):
    sql_script = f"""SELECT 'its existed!'
        FROM favorites
        WHERE favorites.user_id = '{user_id}'
        and favorites.partner_id = '{partner_id}'
        """
    res = execute_sql(sql_script, True)
    if not res:
        return False
    return len(res)


def update_user_info(user_info: dict):
    sql_script = f'''UPDATE users
        SET gender = '{user_info['gender']}',
            city = '{user_info['city']}'
        WHERE user_id = '{user_info['id']}'
        '''
    execute_sql(sql_script)
