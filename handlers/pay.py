from aiogram import Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from keyboards.keyboards import menu_kb, access_payment_kb, no_donat_kb
from database.users import game_users
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, callback_query
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.services import is_number


router = Router()


class Donat(StatesGroup):
    total = State()
    access_donat = State()


@router.message(Command('donat'))
async def process_donat(message: Message, state: FSMContext):
    if not game_users[str(message.from_user.id)]['in_play']:
        await message.answer(text='Выберите сумму отправки (руб): ', reply_markup=no_donat_kb)
        await state.set_state(Donat.total)

    else:
        await message.answer(text='Вы в игре!')


@router.message(Donat.total, F.text)
async def process_total(message: Message, state: FSMContext):
    if not game_users[str(message.from_user.id)]['in_play']:
        print(message.text)
        if is_number(message.text):
            if int(message.text) > 500:
                await message.answer(text='Донат не может превышать 500 рублей')
            else:
                await state.update_data(total=int(message.text))
                await message.answer(text='Вы хотите перевести донат?', reply_markup=access_payment_kb)

        else:
            await message.answer(text='Введите число')

    else:
        await message.answer(text='Вы в игре!')


@router.callback_query(F.data == 'access_payment')
async def process_order(call: CallbackQuery, bot: Bot, state: FSMContext):
    total = await state.get_data()
    await bot.send_invoice(chat_id=call.from_user.id,
                           title='Купить билет',
                           description='Покупка билета ',
                           provider_token='381764678:TEST:94256',
                           currency='RUB',
                           prices=[
                               LabeledPrice(
                                   label='Билет',
                                   amount=total['total']*100
                               )
                           ],
                           is_flexible=False,
                           payload='Ticket for quest',
                           photo_url='https://s0.rbk.ru/v6_top_pics/media/img/4/04/346843326750044.jpg',
                           )
    await state.clear()


@router.pre_checkout_query()
async def pre_checkout_q(pre_checkout_qu: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_qu.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    try:
        await message.answer(text='Спасибо за донат)', reply_markup=menu_kb)


    except Exception as es:
        await message.answer(text=f'Ошибка: {es}. Перешлите это сообщение в поддержку')


@router.callback_query(F.data == 'close_donat')
async def close_donat(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(text='Жалко(')




