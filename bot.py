import config
import logging

from aiogram import Bot, Dispatcher, executor, types

from sqliter import SQLighter

from aiogram.dispatcher.filters import Command

from aiogram.dispatcher import FSMContext

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from importlib import reload

from states import AccStates

import re

#уровень логов
logging.basicConfig(level = logging.INFO)

#init
storage = MemoryStorage()
bot = Bot(token = config.API_TOKEN)
dp = Dispatcher(bot, storage = storage)

#echo
"""
@dp.message_handler()
async def echo(message : types.Message):
    await message.answer(message.text)
"""

#database
db_path = '1.db'
db = SQLighter(db_path)

#subscribe activation
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    user_id = message.from_user.id
    print(db.subscriber_exists(user_id))
    if(not db.subscriber_exists(user_id)):
        db.add_subscriber(user_id)
        await message.answer("Успешно...")
    else:
        await message.answer("Вы уже зарегистрированны")



#unsubscribe

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message : types.Message):
    user_id = message.from_user.id
    if(not db.subscriber_exists(user_id)):
        db.add_subscriber(user_id,False)
        await message.answer('Вы итак не подписаны')
    else:
        db.update_subscription(user_id,False)
        await message.answer('Вы отписались')

    await message.answer("Успешно...")

@dp.message_handler(Command(commands = ["addAccount",'changeAccount']),state=None)
async def unsubscribe(message : types.Message):
    user_id = message.from_user.id
    isExist = db.subscriber_exists(user_id)
    if message.text.replace(" ",'') == '/addAccount':
        if(isExist):
            if(db.account_exists(user_id)):

                await message.answer('У вас уже есть аккаунт')
            else:
                await message.answer('Введите логин и пароль разделённые пробелом или введите /exit для отмены')
                await AccStates.first()
    elif message.text.replace(" ",'') == '/changeAccount':
        await message.answer('Введите логин и пароль разделённые пробелом или введите /exit для отмены')
        await AccStates.first()








@dp.message_handler(state = AccStates.data)
async def add_username(message : types.Message,state:FSMContext):
    if message.text.replace(' ','') == '/exit':
        await state.finish()
        await message.answer('Отменено!')
        return
    else:

        user_id = message.from_user.id
        text = message.text
        data = re.split('\s',text)
        await state.update_data(text = text)

        db.add_account(user_id,data[0],data[1])
        await message.answer('Удачно!')
        await state.finish()





@dp.message_handler(commands = ['checkUnreads'])
async def check_unreads(message : types.Message):
    await message.answer('Пожалуйста подождите...')
    from readManga import Parser
    user_id = message.from_user.id

    isExist = db.subscriber_exists(user_id)
    if(isExist):
        if(db.account_exists(user_id)):

            pass
        else:
            await message.answer('Вы не добавили аккаунт!')
            return
    else:
        await message.answer('Вы не подписались!')
        return


    parser = Parser(user_id,db_path)
    parser.parse_bookmarks()
    parser.check_unreads()
    await message.answer(f'У вас {len(parser.unreads)} непрочитанных:')
    answer = ''
    cnt = 0
    prev = ''
    for unread in parser.unreads:
        if prev != unread:
            answer += unread + '\n'
            cnt += 1
            prev = unread
        if cnt > 20:
            await message.answer(answer,parse_mode ='HTML')
            answer = ''
            cnt = 0

    if len(answer) > 0:
        await message.answer(answer,parse_mode ='HTML')
    parser.unreads.clear()
    parser.books.clear()
    parser.fresh_books.clear()



@dp.message_handler(commands = ['commands'])
async def show_commands(message : types.Message):
    res = """
    /subscribe - Регистрация
/unsubscribe - 0тписаться
/addAccount - Добавить аккаунт readManga
/checkUnreads - Проверить не прочитанные главы
/changeAccount - Изменить аккаунт
/bookmarks - Вывести всю мангу из раздела 'В процессе' с ссылками
    """

    await message.answer(res)


@dp.message_handler(commands = ['support'])
async def show_supports(message : types.Message):
    res = """
    При возникновении проблем
или при наличии предложений пишите сюда:
@R_Swanson
    """

    await message.answer(res)


@dp.message_handler(commands = ['bookmarks'])
async def show_books(message : types.Message):
    await message.answer('Пожалуйста подождите...')
    res = ''

    from readManga import Parser

    user_id = message.from_user.id

    isExist = db.subscriber_exists(user_id)
    if(isExist):
        if(db.account_exists(user_id)):

            pass
        else:
            await message.answer('Вы не добавили аккаунт!')
            return
    else:
        await message.answer('Вы не подписались!')
        return

    parser = Parser(user_id,db_path)

    parser.parse_bookmarks()
    cnt = 0
    for book in parser.books:
        res += '<a href = "%s"> %s </a>'%(book['cLink'],book['title']) + '\n'
        cnt+=1
        if cnt > 30:
            await message.answer(res, parse_mode ='HTML')
            res = ''
            cnt = 0
    if len(res) > 0:
        await message.answer(res, parse_mode ='HTML')
    parser.unreads.clear()
    parser.books.clear()
    parser.fresh_books.clear()

















if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)
