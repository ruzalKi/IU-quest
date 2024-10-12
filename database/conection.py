import pymysql.cursors
from config_data.config import Config, load_config

config: Config = load_config()

try:
    connection = pymysql.connect(
        host=config.sql_server.host,
        port=3306,
        user=config.sql_server.user,
        password=config.sql_server.password,
        database='innoquest',
        cursorclass=pymysql.cursors.DictCursor
    )

except Exception:
    pass
