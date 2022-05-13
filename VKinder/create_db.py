import psycopg2
import psycopg2.extras
from config import hostname, database, username, pwd, port_id

with psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id) as connection:
    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS partners')
        cursor.execute('DROP TABLE IF EXISTS favorites')

        create_script = ''' CREATE TABLE IF NOT EXISTS users(
                                    user_id     int PRIMARY KEY,
                                    user_token  varchar(100),
                                    birthdate   date,
                                    age         int,
                                    gender      varchar(2),
                                    city_id     int,
                                    city        varchar(20)
                                    ) '''
        cursor.execute(create_script)

        create_script = ''' CREATE TABLE IF NOT EXISTS partners(
                                    partner_id  int PRIMARY KEY,
                                    first_name  varchar(50) NOT NULL,
                                    last_name   varchar(50) NOT NULL,
                                    birthdate   date,
                                    age         int,
                                    gender      varchar(2),
                                    city_id     int,
                                    city        varchar(20),
                                    photo_ref1  varchar(50),
                                    photo_ref2  varchar(50),
                                    photo_ref3  varchar(50)
                                    ) '''
        cursor.execute(create_script)

        create_script = ''' CREATE TABLE IF NOT EXISTS favorites(
                                    partner_id  int references partners(partner_id),
                                    user_id     int references users(user_id),
                                    constraint pk1 PRIMARY KEY (partner_id, user_id)
                                    ) '''
        cursor.execute(create_script)