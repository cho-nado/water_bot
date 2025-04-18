from aiogram.filters import BaseFilter
from aiogram import types
from aiogram.fsm.context import FSMContext

class NotInState(BaseFilter):
    """
    Пропускает сообщение, если текущее FSM-состояние пользователя НЕ
    входит в список указанных.
    Используется для «ловушки» всех остальных текстов.
    """

    def __init__(self, *states: str):
        # преобразуем все состояния в строки
        self.states = {str(state) for state in states}

    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        current = await state.get_state()
        return current not in self.states
