from config_data.config import Config, load_config
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.users import game_users
from database.conection import connection
import re

config: Config = load_config()


def is_admin(user_id: int) -> bool:
    return user_id in config.tg_bot.admin_ids


def is_senior_moderator(user_id: int) -> bool:
    with connection.cursor() as cursor:
        select_user = f'SELECT role FROM users WHERE id = {user_id}'
        cursor.execute(select_user)
        user = cursor.fetchall()

    return user[0]['role'] == 3


def is_moderator(user_id: int) -> bool:
    with connection.cursor() as cursor:
        select_user = f'SELECT role FROM users WHERE id = {user_id}'
        cursor.execute(select_user)
        user = cursor.fetchall()

    return user[0]['role'] == 2


def make_kbs(list_strs: list[str]) -> ReplyKeyboardMarkup:
    list_buttons = [[]]
    for i in range(len(list_strs)):
        list_buttons.append([])
        list_buttons[i].append(KeyboardButton(text=list_strs[i]))
    kb = ReplyKeyboardMarkup(keyboard=list_buttons, resize_keyboard=True)
    return kb


def is_user_id(s: str):
    try:
        int(s)
    except ValueError:
        return False

    if not (int(s) in game_users):
        return False

    return True


def is_email(s: str):
    pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"
    if re.match(pattern, s) is not None:
        return True
    else:
        return False


def is_number(s: str):
    try:
        int(s)
    except ValueError:
        return False

    return True