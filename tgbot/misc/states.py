from aiogram.fsm.state import State, StatesGroup


class ExampleState(StatesGroup):
    waiting_send_example_text = State()


class AddPostState(StatesGroup):
    waiting_send_post = State()


class AddPostIntervalState(StatesGroup):
    waiting_send_interval_timedelta = State()


class TechSupporttState(StatesGroup):
    waiting_send_techsup = State()


class AdminState(StatesGroup):
    waiting_set_new_payment_sum = State()
