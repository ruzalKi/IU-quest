from aiogram import F, Router
from aiogram.types import Message
import yaml
from services.services import make_kbs
from database.users import game_users
from aiogram import types
from keyboards.keyboards import help_kb, menu_kb
from database.conection import connection
from lexicon.lexicon import LEXICON


with open('handlers/text/text.yaml', 'r', encoding='utf-8') as file:
    text: str = yaml.safe_load(file)


router = Router()


@router.message(F.text)
async def process_text(message: Message):
    if message.text == '/start':
        try:
            with connection.cursor() as cursor:
                add_player = f"INSERT INTO `users` (id, name, in_play, stage, went, team, help, payed, pre_team, role) VALUES ('{str(message.from_user.id)}', 'Gamer', false, 1, 1, 0, 0, false, 0, 1);"
                cursor.execute(add_player)
                connection.commit()

            game_users[str(message.from_user.id)] = {'name': 'Gamer', 'in_play': False, 'stage': 1, 'went': 1, 'team': 0,
                                                'help': 0, 'payed': False, 'pre_team': 0, 'role': 1}


        except Exception as es:
            pass

        await message.answer(text=(LEXICON['/start'] + ' 📃Заполните анкету перед началом игры'),
                             reply_markup=menu_kb)

    elif game_users[str(message.from_user.id)]['went'] == 3 and message.text.startswith('/start') and message.text[7::] == ('ref_' + str(game_users[str(message.from_user.id)]['stage'])):
        game_users[str(message.from_user.id)]['stage'] += 1
        game_users[str(message.from_user.id)]['went'] = 1
        await message.answer(text=text[game_users[str(message.from_user.id)]['stage']]['text'], reply_markup=make_kbs(text[game_users[str(message.from_user.id)]['stage']]['button']))

    elif game_users[str(message.from_user.id)]['went'] == 3 and message.text.startswith('/start') and message.text[7::] != ('ref_' + str(game_users[str(message.from_user.id)]['stage'])):
        await message.answer(text='Не тот qr-код, поищите еще')
    elif game_users[str(message.from_user.id)]['payed'] and game_users[str(message.from_user.id)]['stage'] == 1 and game_users[str(message.from_user.id)]['went'] == 1 and message.text == '🎮Начать игру':
        await message.answer(text=text[1]['text'], reply_markup=make_kbs(text[1]['button']))
        game_users[str(message.from_user.id)]['in_play'] = True

    elif message.text == 'Дальше' and game_users[str(message.from_user.id)]['went'] == 1:
        await message.answer(text=text[game_users[str(message.from_user.id)]['stage']]['questions'],
                             reply_markup=make_kbs(text[game_users[str(message.from_user.id)]['stage']]['buttons']))
        game_users[str(message.from_user.id)]['went'] = 2

    elif text[game_users[str(message.from_user.id)]['stage']]['answer'] == message.text and game_users[str(message.from_user.id)]['went'] == 2:
        if game_users[str(message.from_user.id)]['stage'] == len(text):
            game_users[str(message.from_user.id)]['in_play'] = False
            await message.answer(text=text[game_users[str(message.from_user.id)]['stage']]['if_right'], reply_markup=menu_kb)
            await message.answer_photo(
                photo=types.FSInputFile(path=text[game_users[str(message.from_user.id)]['stage']]['url_photo']))
            game_users[str(message.from_user.id)]['stage'] = 1
            game_users[str(message.from_user.id)]['went'] = 1

        else:
            await message.answer(text=text[game_users[str(message.from_user.id)]['stage']]['if_right'], reply_markup=help_kb)
            await message.answer_photo(
                photo=types.FSInputFile(path=text[game_users[str(message.from_user.id)]['stage']]['url_photo']))

            game_users[str(message.from_user.id)]['went'] = 3

    elif game_users[str(message.from_user.id)]['went'] == 1 and game_users[str(message.from_user.id)]['in_play']:
        await message.answer(text='Так у вас одна кнопка, нажмите на неё просто')

    elif game_users[str(message.from_user.id)]['went'] == 2:
        await message.answer(text=text[game_users[str(message.from_user.id)]['stage']]['if_wrong'])
        await message.answer_photo(photo=types.FSInputFile(path=text[game_users[str(message.from_user.id)]['stage']]['url_photo']))
        game_users[str(message.from_user.id)]['went'] = 3

    elif game_users[str(message.from_user.id)]['went'] == 3 and message.text == 'Подсказка':
        await message.answer(text='Подсказочка✨')
        await message.answer_photo(photo=types.FSInputFile(path=text[game_users[str(message.from_user.id)]['stage']]['help_photo']))
    elif not game_users[str(message.from_user.id)]['payed'] and message.text and not game_users[str(message.from_user.id)]['in_play']:
        await message.answer(text='Заполните для начала анкету')
    else:
        await message.answer(text='Как это? Ошибочка!')


