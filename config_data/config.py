from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    yookassa_secret_key: str


@dataclass
class SqlServer:
    host: str
    port: int
    user: str
    password: str


@dataclass
class Config:
    tg_bot: TgBot
    sql_server: SqlServer


def load_config(path: str or None=None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS'))),
            yookassa_secret_key=env('YOOKASSA_SECRET_KEY')

        ),
        sql_server=SqlServer(
            host=env('HOST'),
            port=env('PORT'),
            user=env('USER'),
            password=env('PASSWORD')
        )
    )
