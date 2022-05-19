import psycopg2
import psycopg2.extras


def recreate_db_if_needed(wipe_tables=False):
    hostname = 'localhost'
    database = 'postgres'
    username = 'postgres'
    pwd = '123456'
    port_id = 5432

    with psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id) as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

            if wipe_tables:
                cursor.execute('DROP TABLE IF EXISTS users CASCADE')
                cursor.execute('DROP TABLE IF EXISTS search_results CASCADE')
                cursor.execute('DROP TABLE IF EXISTS favorites CASCADE')

            create_script = ''' CREATE TABLE IF NOT EXISTS users(
                                        user_id     varchar(10) PRIMARY KEY,
                                        user_token  varchar(100) NOT NULL,
                                        age         int NOT NULL,
                                        gender      varchar(10) NOT NULL,
                                        city        varchar(50) NOT NULL
                                        ) '''
            cursor.execute(create_script)

            # AGE, city - то же самое что и с таблицей выше
            create_script = ''' CREATE TABLE IF NOT EXISTS partners(
                                        partner_id  varchar(10) PRIMARY KEY,
                                        first_name  varchar(50) NOT NULL,
                                        last_name   varchar(50) NOT NULL,
                                        age         int NOT NULL,
                                        gender      varchar(10) NOT NULL,
                                        city        varchar(50) NOT NULL,
                                        photo_ref1  varchar(50),
                                        photo_ref2  varchar(50),
                                        photo_ref3  varchar(50)
                                        ) '''
            cursor.execute(create_script)

            create_script = ''' CREATE TABLE IF NOT EXISTS favorites(
                                        partner_id  varchar(10) NOT NULL,
                                        user_id     varchar(10) NOT NULL 
                                        ) '''
            cursor.execute(create_script)
