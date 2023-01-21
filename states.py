from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMAddSearchState(StatesGroup):
    search = State()
    name = State()


class FSMAddPromoState(StatesGroup):
    promo = State()


class FSMActivatePromoState(StatesGroup):
    promo = State()
