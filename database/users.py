import mysql.connector
from getpass import getpass

import pymysql.cursors
from mysql.connector import connect, Error
from config_data.config import Config, load_config


config: Config = load_config()


game_users = {}

try:
    connection = pymysql.connect(
        host=config.sql_server.host,
        port=3306,
        user=config.sql_server.user,
        password=config.sql_server.password,
        database='innoquest',
        cursorclass=pymysql.cursors.DictCursor
    )
    print('Successfull')

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM `users`;"
            cursor.execute(select_query)
            rows = cursor.fetchall()
            for i in rows:
                game_users[i['id']] = {'name': i['name'], 'in_play': i['in_play'], 'stage': i['stage'], 'went': i['went'], 'team': i['team'], 'help': i['help'], 'payed': i['payed'], 'pre_team': i['pre_team'], 'role': i['role']}
    finally:
        connection.close()


except Exception as e:
    print(e)