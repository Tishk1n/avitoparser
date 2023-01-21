from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

add_searchb = KeyboardButton('🎆Добавить поисковой запрос')
search_listb = KeyboardButton('📃Список поисковых запросов')
user_menub = KeyboardButton('🤵Меню пользователя')
promo_codes_listb = KeyboardButton('📃Список промокодов')
admin_add_promob = KeyboardButton('✅Добавить промокод')

promo_activateb = KeyboardButton('✅Активировать промокод')
backb = KeyboardButton('Назад')

user_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
user_menu_keyboard.add(promo_activateb).add(backb)

back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
back_keyboard.add(backb)

main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(search_listb).add(add_searchb).add(user_menub)

main_menu_admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_admin_keyboard.add(search_listb).add(add_searchb).add(user_menub).add(promo_codes_listb).add(admin_add_promob)

not_member_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
not_member_keyboard.add(user_menub)

passb = KeyboardButton('Пропустить')
pass_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(passb)

cancelb = KeyboardButton('Отменить')
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cancelb)

day1b = KeyboardButton('1')
day3b = KeyboardButton('3')
day7b = KeyboardButton('7')
day14b = KeyboardButton('14')
day30b = KeyboardButton('30')
day90b = KeyboardButton('90')
day180b = KeyboardButton('180')

promo_code_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(day1b, day3b, day7b, day14b, day30b, day90b, day180b)
