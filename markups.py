from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

cng_acc_btn = KeyboardButton("📝 Изменить аккаунт")
unreads_btn = KeyboardButton("📒 Вывести недочитанные")
bookmarks_btn = KeyboardButton("🔖 Вывести закладки")
#books_showing_btn = KeyboardButton("Отображение манги")
settings_btn = KeyboardButton("⚙️ Настройки")
menu_btn = KeyboardButton("📋 Меню")


main_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1).add(
    unreads_btn, bookmarks_btn, settings_btn)
cng_acc_menu = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True, row_width=1).add(cng_acc_btn, menu_btn)
settings_menu = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True, row_width=1).add(cng_acc_btn, menu_btn)
