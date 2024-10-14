from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, callback_query
from aiogram.types.callback_query import CallbackQuery
from keyboards.keyboards import access_fill_kb, dont_access_fill_kb, access_send, other_commands_kb, back_kb
from lexicon.lexicon import LEXICON
from config_data.config import Config, load_config
from services.services import is_admin, is_number, is_email, is_moderator, is_senior_moderator
from database.users import game_users
from database.conection import connection
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pandas as pd


config: Config = load_config()


router = Router()


class SendReport(StatesGroup):
    report = State()


class PeopleInfo(StatesGroup):
    name = State()
    surname = State()
    father_name = State()
    age = State()
    user_email = State()



# region Commands


@router.message(Command('help'))
async def process_help_message(message: Message):
    if game_users[str(message.from_user.id)]['in_play']:
        await message.answer(LEXICON['in_play'])
    else:
        await message.answer(text=LEXICON['FAQ'], reply_markup=other_commands_kb)


@router.message(Command('report'))
async def process_report(message: Message, state: FSMContext):
    if not game_users[str(message.from_user.id)]['in_play']:
        await message.answer('Напишите ваш репорт: ')
        await state.set_state(SendReport.report)
    else:
        await message.answer(text='Вы в игре!')


# endregion

# region Strings


@router.message(F.text == LEXICON['FAQ_button'])
async def process_faq(message: Message):
    if game_users[str(message.from_user.id)]['in_play']:
        await message.answer(LEXICON['in_play'])
    else:
        await message.answer(text=LEXICON['FAQ'], reply_markup=other_commands_kb)


@router.message(F.text == LEXICON['sale_button'])
async def process_sale_ticket(message: Message):
    if game_users[str(message.from_user.id)]['in_play']:
        await message.answer(LEXICON['in_play'])
    else:
        if game_users[str(message.from_user.id)]['payed']:
            await message.answer(text=LEXICON['payed'])
        else:
            await message.answer(text=f'Заполните анкету, чтобы пройти квест', reply_markup=access_fill_kb)

# endregion

# region Callbacks


@router.callback_query(F.data == 'access_fill')
async def process_start_fill(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text=LEXICON['set_name'], reply_markup=dont_access_fill_kb)
    await state.set_state(PeopleInfo.name)


@router.callback_query(F.data == 'moder_commands')
async def process_moder_commands(call: CallbackQuery):
    if game_users[str(call.from_user.id)]['in_play']:
        await call.message.answer(LEXICON['in_play'])
    else:
        if is_admin(call.from_user.id) or is_senior_moderator(call.from_user.id) or is_moderator(call.from_user.id):
            await call.message.edit_text(text=LEXICON['moder_commands'], reply_markup=back_kb)
        else:
            await call.answer(text='У вас недостаточно прав')


@router.callback_query(F.data == 'admin_commands')
async def process_moder_commands(call: CallbackQuery):
    if game_users[str(call.from_user.id)]['in_play']:
        await call.message.answer(LEXICON['in_play'])
    else:
        if is_admin(call.from_user.id) or is_senior_moderator(call.from_user.id):
            await call.message.edit_text(text=LEXICON['admin_commands'], reply_markup=back_kb)
        else:
            await call.answer(text='У вас недостаточно прав')


@router.callback_query(F.data == 'back')
async def process_back(call: CallbackQuery):
    if game_users[str(call.from_user.id)]['in_play']:
        await call.message.answer(LEXICON['in_play'])
    else:
        await call.message.edit_text(text=LEXICON['FAQ'], reply_markup=other_commands_kb)


@router.callback_query(F.data == 'close_fill')
async def process_close_fill(call: CallbackQuery):
    await call.message.answer(text='🏠Главное меню: ')
    await state.clear()


# endregion

# region FSM


@router.message(F.text, SendReport.report)
async def process_send_report(message: Message, state: FSMContext):
    try:
        if len(message.text) <= 300:
            with connection.cursor() as cursor:
                add_report = f"INSERT INTO reports (user_id, text) VALUES ('{str(message.from_user.id)}', '{message.text}');"
                cursor.execute(add_report)
                connection.commit()

            await message.answer('Ваша жалоба отправлена')
            await state.clear()
        else:
            await message.answer('Текст жалобы до 300 символов')

    except Exception as es:
        await message.answer(text=f'Ошибка: {es}. Пожалуйста перешлите это письмо в тех. поддержку')


@router.message(F.text, PeopleInfo.name)
async def process_set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text=LEXICON['set_surname'], reply_markup=dont_access_fill_kb)
    await state.set_state(PeopleInfo.surname)


@router.message(F.text, PeopleInfo.surname)
async def process_set_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer(text=LEXICON['set_father_name'], reply_markup=dont_access_fill_kb)
    await state.set_state(PeopleInfo.father_name)


@router.message(F.text, PeopleInfo.father_name)
async def process_set_father_name(message: Message, state: FSMContext):
    await state.update_data(father_name=message.text)
    await message.answer(text=LEXICON['set_age'], reply_markup=dont_access_fill_kb)
    await state.set_state(PeopleInfo.age)


@router.message(F.text, PeopleInfo.age)
async def process_set_age(message: Message, state: FSMContext):
    if is_number(message.text):
        await state.update_data(age=message.text)
        await message.answer(text=LEXICON['set_email'], reply_markup=dont_access_fill_kb)
        await state.set_state(PeopleInfo.user_email)
    else:
        await message.answer(text='Пожалуйста, введите возраст (нужно число): ', reply_markup=dont_access_fill_kb)


@router.message(F.text, PeopleInfo.user_email)
async def process_set_user_email(message: Message, state: FSMContext):
    if is_email(message.text):
        await message.answer(text='Вы хотите отправить анкету?', reply_markup=access_send)
        await state.update_data(user_email=message.text)
    else:
        await message.answer(text='Пожалуйста, введите валидный email (пример: inno@mail.ru)', reply_markup=dont_access_fill_kb)


@router.callback_query(F.data == 'access_send')
async def process_send(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    try:
        with connection.cursor() as cursor:
            payed = f"UPDATE users SET payed = true WHERE id = '{str(call.from_user.id)}';"
            cursor.execute(payed)
            connection.commit()

        users_data = pd.read_excel('C:/Users/ruzal/PycharmProjects/IU_quest/handlers/data_users/user_data.xlsx')
        users_data.loc[len(users_data.index)] = {'ФИО': (user_data['name'] + ' ' + user_data['surname'] + ' ' + user_data['father_name']), "Возраст": user_data['age'], 'Email': user_data['user_email']}
        users_data.to_excel('C:/Users/ruzal/PycharmProjects/IU_quest/handlers/data_users/user_data.xlsx')
        await call.message.edit_text(text='Вы заполнили анкету')
        await state.clear()
        game_users[str(call.from_user.id)]['payed'] = True

    except Exception as es:
        await call.message.answer(text=f'Ошибка: {es}. Пожалуйста перешлите это письмо в тех. поддержку')


# endregion
