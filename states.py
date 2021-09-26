from aiogram.dispatcher.filters.state import StatesGroup,State

class AccStates(StatesGroup):
    login = State()
    password = State()
