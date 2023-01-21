import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import bot, MANAGER_ID
from database import add_search_db, get_searches_db, delete_search_db, get_user_db, create_user_db, add_promo_code_db, \
    get_promo_code_db, PromoCode, active_promo_code, get_user_searches_db, User, get_user_searches_paginate_db, \
    get_user_search_db, get_promo_codes_db, get_promo_code_scalars_db
from keyboard import add_searchb, search_listb, passb, main_menu_keyboard, pass_keyboard, main_menu_admin_keyboard, \
    admin_add_promob, user_menub, user_menu_keyboard, promo_activateb, backb, not_member_keyboard, promo_codes_listb, \
    cancel_keyboard, cancelb
from states import FSMAddSearchState, FSMAddPromoState, FSMActivatePromoState


async def send_welcome(message: types.Message):
    if not await get_user_db(message.from_user.id):
        await create_user_db(message.from_user.id)
    user: User = await get_user_db(message.from_user.id)
    if user.membership_activate and datetime.date.today() < user.membership_activate or message.from_user.id == MANAGER_ID:
        await bot.send_message(message.from_user.id, 'Сделай выбор',
                               reply_markup=main_menu_admin_keyboard if message.from_user.id == MANAGER_ID else main_menu_keyboard)
    else:
        await bot.send_message(message.from_user.id, 'Ваша подписка не активна', reply_markup=not_member_keyboard)


async def main_menu(message: types.Message):
    user: User = await get_user_db(message.from_user.id)

    if message.text == add_searchb.text:
        if user.membership_activate and datetime.date.today() < user.membership_activate or message.from_user.id == MANAGER_ID:
            await AddSearch.add_search_start(message)
        else:
            await bot.send_message(message.from_user.id, 'Ваша подписка не активна', reply_markup=not_member_keyboard)

    elif message.text == search_listb.text:
        if user.membership_activate and datetime.date.today() < user.membership_activate or message.from_user.id == MANAGER_ID:
            await bot_get_search_list(message)
        else:
            await bot.send_message(message.from_user.id, 'Ваша подписка не активна', reply_markup=not_member_keyboard)

    elif message.text == user_menub.text:
        if message.from_user.id == MANAGER_ID:
            return await bot.send_message(message.from_user.id, f'Привет, 👮{message.from_user.first_name}!\nВы имеете безлимитную подписку',
                                          reply_markup=user_menu_keyboard)

        user: User = await get_user_db(message.from_user.id)
        await bot.send_message(message.from_user.id,
                               f'Привет, 👮{message.from_user.first_name}!\nПодписка истекает {user.membership_activate}' if user.membership_activate and user.membership_activate >= datetime.date.today() else 'Ваша подписка не активна',
                               reply_markup=user_menu_keyboard)

    if message.text == promo_activateb.text:
        await ActivePromoCode.active_promo_start(message)

    elif message.text == backb.text:
        await send_welcome(message)

    elif message.text == admin_add_promob.text and message.from_user.id == MANAGER_ID:
        await AddPromoCode.add_promo_start(message)

    elif message.text == promo_codes_listb.text and message.from_user.id == MANAGER_ID:
        await get_promo_codes_list(message)


async def bot_get_search(callback_data: types.CallbackQuery):
    search_id = callback_data.data.removeprefix('search=')
    search = await get_user_search_db(search_id)
    deleteb = InlineKeyboardButton('Удалить', callback_data=f'delete={search_id}')
    delete_keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(deleteb)
    await bot.send_message(callback_data.from_user.id,
                           f'Название запроса: {search.name}\n\nСсылка на запрос: {search.search}',
                           reply_markup=delete_keyboard, disable_web_page_preview=True)


async def bot_get_search_list_paginate(callback_data: types.CallbackQuery):
    page = int(callback_data.data.removeprefix('page='))
    await bot_get_search_list(callback_data, page)


async def bot_get_search_list(message: types.Message, page: int = 1):
    search_list = await get_user_searches_paginate_db(message.from_user.id, page=page)
    if search_list:
        search_list_kb = InlineKeyboardMarkup(resize_keyboard=True)
        for i in search_list:
            titleb = InlineKeyboardButton(i.name, callback_data=f'search={i.id}')
            search_list_kb.add(titleb)
        if search_list and len(search_list) == 10:
            nextb = InlineKeyboardButton(f'Следующая страница: {page + 1}', callback_data=f'page={page + 1}')
            if page > 1:
                previousb = InlineKeyboardButton(f'Предыдущая страница: {page - 1}', callback_data=f'page={page - 1}')
                search_list_kb.add(previousb).insert(nextb)
            else:
                search_list_kb.add(nextb)
        elif page > 1:
            previousb = InlineKeyboardButton(f'Предыдущая страница: {page - 1}', callback_data=f'page={page - 1}')
            search_list_kb.add(previousb)
        await bot.send_message(message.from_user.id, 'Список поисковых запросов', reply_markup=search_list_kb)
    else:
        await bot.send_message(message.from_user.id, 'Нет ни одного поискового запроса в списке')


async def bot_delete_search(callback_data: types.CallbackQuery):
    search_id = callback_data.data.removeprefix('delete=')
    await delete_search_db(search_id)
    await bot.send_message(callback_data.from_user.id, 'Поисковой запрос удален!')


async def get_promo_codes_list(message: types.Message):
    promo_codes: [PromoCode] = await get_promo_codes_db()
    if promo_codes:
        message_to_send = ''
        for i in promo_codes:
            message_to_send += f'{i.key} - {i.work_days} дней\n'
        await bot.send_message(message.from_user.id, message_to_send)
    else:
        await bot.send_message(message.from_user.id, 'Пока нету доступных промокодов')


class AddSearch:
    @staticmethod
    async def add_search_start(message: types.Message):
        await FSMAddSearchState.search.set()
        await bot.send_message(message.from_user.id, 'Отправь ссылку на поисковой запрос', reply_markup=cancel_keyboard)

    @staticmethod
    async def add_search_url(message: types.Message, state: FSMContext):

        class NotUrlException(Exception):
            pass

        if message.text == '/start' or message.text == cancelb.text:
            await state.finish()
            return await send_welcome(message)

        try:
            if message.text.startswith('https://www.avito.ru/' or 'https://m.avito.ru/'):
                async with state.proxy() as data:
                    data['url'] = message.text
                await FSMAddSearchState.next()
                await bot.send_message(message.from_user.id, 'Отправьте желаемое название',
                                       reply_markup=pass_keyboard)
            else:
                raise NotUrlException('Сообщение не является адресом')
        except NotUrlException:
            await bot.send_message(message.from_user.id,
                                   'Сообщение не является ссылкой на поисковой запрос, попробуйте еще раз')

    @staticmethod
    async def add_search_name(message: types.Message, state: FSMContext):
        if message.text == '/start' or message.text == cancelb.text:
            await state.finish()
            return await send_welcome(message)

        async with state.proxy() as data:
            url = data['url']
        search_name = message.text
        await add_search_db(url, message.from_user.id, search_name)
        await state.finish()
        await bot.send_message(message.from_user.id, 'Поисковой запрос добавлен в список!',
                               reply_markup=main_menu_admin_keyboard if message.from_user.id == MANAGER_ID else main_menu_keyboard)


class AddPromoCode:
    @staticmethod
    async def add_promo_start(message: types.Message):
        await FSMAddPromoState.promo.set()
        await bot.send_message(message.from_user.id,
                               'Выбери длительность дней для промокода или впиши нужное количество дней', reply_markup=cancel_keyboard)

    @staticmethod
    async def add_promo_finish(message: types.Message, state: FSMContext):
        if message.text == '/start' or message.text == cancelb.text:
            await state.finish()
            return await send_welcome(message)

        if message.text.isdigit():
            promo = await add_promo_code_db(int(message.text))
            await state.finish()
            await bot.send_message(message.from_user.id,
                                   f'Новый промокод добавлен!\n\n{promo.key} - {promo.work_days} дней',
                                   reply_markup=main_menu_admin_keyboard if message.from_user.id == MANAGER_ID else main_menu_keyboard)
        else:
            await bot.send_message(message.from_user.id, 'Текст сообщения должен быть числом, попробуй еще раз')


class ActivePromoCode:
    @staticmethod
    async def active_promo_start(message: types.Message):
        await FSMActivatePromoState.promo.set()
        await bot.send_message(message.from_user.id, 'Введи промокод')

    @staticmethod
    async def active_promo_finish(message: types.Message, state: FSMContext):
        if message.text == '/start' or message.text == backb.text:
            return await send_welcome(message)

        if len(message.text) == 24:
            promo: PromoCode = await get_promo_code_scalars_db(message.text)
            if promo:
                date = await active_promo_code(user_id=message.from_user.id, promo=promo)
                await bot.send_message(message.from_user.id, f'Подписка активирована! Ваша подписка закончиться {date}')
                await state.finish()
            else:
                await bot.send_message(message.from_user.id,
                                       f'Промокод не верный! Проверьте правильность и повторите попытку еще раз')
        else:
            await bot.send_message(message.from_user.id,
                                   'Сообщение не соответствуем формату промокода, попробуйте еще раз')


def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_callback_query_handler(bot_get_search, lambda c: c.data and c.data.startswith('search='))
    dp.register_callback_query_handler(bot_delete_search, lambda c: c.data and c.data.startswith('delete='))
    dp.register_callback_query_handler(bot_get_search_list_paginate, lambda c: c.data and c.data.startswith('page='))
    dp.register_message_handler(main_menu)
    dp.register_message_handler(AddSearch.add_search_url, state=FSMAddSearchState.search)
    dp.register_message_handler(AddSearch.add_search_name, state=FSMAddSearchState.name)
    dp.register_message_handler(AddPromoCode.add_promo_finish, state=FSMAddPromoState.promo)
    dp.register_message_handler(ActivePromoCode.active_promo_finish, state=FSMActivatePromoState.promo)
