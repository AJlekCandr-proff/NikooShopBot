from aiogram.fsm.state import StatesGroup, State


class StatesAdmin(StatesGroup):
    """Хранит в себе состояния FSM для действий администратора. """

    choice_game = State()
    choice_action = State()
    select_item = State()
    get_item = State()
    get_message = State()
    get_promo = State()
    choice_promo = State()


class StatesUser(StatesGroup):
    """Хранит в себе состояния FSM для действий обычного пользователя. """
    get_promocode = State()
    get_sum = State()
    check_pay = State()
    choice_game = State()
    choice_product = State()
    buy_product = State()
    get_email = State()
