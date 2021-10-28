import config
import logging
import os
import re

from user_requests import User_SQLighter
from readManga import Parser
from markups import *
from states import AccStates

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage






#уровень логов
logging.basicConfig(level = logging.INFO)

#init
storage = MemoryStorage()
bot = Bot(token = config.API_TOKEN)
dp = Dispatcher(bot, storage = storage)

commands_str ="""
/addAccount - Добавить аккаунт readManga
/checkUnreads - Проверить не прочитанные главы
/changeAccount - Изменить аккаунт
/bookmarks - Вывести всю мангу из раздела 'В процессе' с ссылками
"""




#database
db_link = os.getenv('JAWSDB_URL')
db = User_SQLighter(db_link)


def split_list(l, num):
    x = 0
    n = len(l)
    for i in range(x, n, num):
        yield l[x:x+num]
        x += num


async def add_account(message):
    user_id = message.from_user.id
    await message.answer('Введите ваш логин на readManga или введите /exit для отмены')
    await AccStates.login.set()



@dp.message_handler(state = AccStates.login)
async def add_username(message : types.Message,state:FSMContext):
    if message.text.replace(' ','') == '/exit':
        await state.finish()
        await message.answer('Отменено!')
        return -1
    else:

        user_id = message.from_user.id
        nickname = message.text
        db.add_username(user_id, nickname)
        await bot.send_message(user_id, 'Введите ваш пароль на readManga или введите /exit для отмены')
        await AccStates.password.set()

@dp.message_handler(state = AccStates.password)
async def add_username(message : types.Message,state:FSMContext):
    if message.text.replace(' ','') == '/exit':
        await state.finish()
        await message.answer('Отменено!')
        return -1
    else:
        user_id = message.from_user.id
        password = message.text
        db.add_password(user_id, password)
        db.add_account(user_id)
        db.commit()
        await bot.send_message(user_id, 'Успешно!', reply_markup = main_menu)
        await state.finish()


        


async def check_unreads(message):
    await message.answer('Пожалуйста подождите...')
    user_id = message.from_user.id
    if(not db.account_exists(user_id)):
        await bot.send_message(user_id, 'Вы не добавили аккаунт!', reply_markup = cng_acc_menu)
        return -1

    parser = Parser(user_id, db)
    await parser.check_unreads()
    await message.answer(f'У вас {len(parser.unreads)} непрочитанных:')
    splited_unreads = split_list(parser.unreads, 20)
    for l in splited_unreads:
        answer = ''
        for unread in l:
            answer += unread + '\n'
        await bot.send_message(message.from_user.id, answer, parse_mode = 'HTML')
    del parser



@dp.message_handler(commands = ['start'])
async def start_work(message : types.Message):
    user_id = message.from_user.id
    if(not db.user_exists(user_id)):
        try:
            db.add_user(user_id)
        except:
            await message.answer("Ошибка...")
            return -1
        await bot.send_message(user_id, 'Добро пожаловать!', reply_markup = main_menu)
    else:
        await bot.send_message(user_id, "Вы уже вошли...", reply_markup = main_menu)

@dp.message_handler(commands = ['support'])
async def show_supports(message : types.Message):
    res = """
    При возникновении проблем
или при наличии предложений пишите сюда:
@R_Swanson
    """

    await message.answer(res)


async def show_books(message):
    user_id = message.from_user.id
    if(not db.account_exists(user_id)):
        await bot.send_message(user_id, 'Вы не добавили аккаунт!', reply_markup = cng_acc_menu)
        return -1

    await message.answer('Пожалуйста подождите...')
    parser = Parser(user_id,db)
    bookmarks = parser.get_html_bookmarks()
    splited_bookmarks = split_list(bookmarks, 35)
    for l in splited_bookmarks:
        answer = ''
        for book in l:
            answer += book
        await bot.send_message(message.from_user.id, answer, parse_mode = "HTML")
    del parser

async def show_menu(message):
    await bot.send_message(message.from_user.id, "Меню:", reply_markup =main_menu)

async def show_settings(message):
    await bot.send_message(message.from_user.id, "Настройки:", reply_markup =settings_menu)



command_switch = {
    '/changeAccount' : add_account,
    '📝 Изменить аккаунт': add_account,
    '/checkUnreads': check_unreads,
    '📒 Вывести недочитанные' : check_unreads,
    '🔖 Вывести закладки': show_books,
    '/menu' : show_menu,
    '📋 Меню': show_menu,
    '⚙️ Настройки': show_settings,
    '/settings': show_settings,
}

@dp.message_handler()
async def handle(message : types.Message):
    try:
        await command_switch[message.text](message)
    except KeyError:
        pass












if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)
