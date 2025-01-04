from aiogram.fsm.state import State, StatesGroup

class RecipeForm(StatesGroup):
    name = State()
    ingredients = State()
    instructions = State()
    image = State()

class UserInput(StatesGroup):
    text = State()