from gc import callbacks

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

class RecipeCallback(CallbackData, prefix="recipe", sep=";"):
    id: int
    name: str

class SearchRecipeCallback(CallbackData, prefix="search", sep=";"):
    id: int
    name: str

def recipes_keyboard_markup(recipe_list:list[dict], offset:int|None=None, skip:int|None=None):
    builder = InlineKeyboardBuilder()

    for index, recipe_data in enumerate(recipe_list):
        callbacks_data = RecipeCallback(id=index, **recipe_data)
        builder.button(
            text=f"{callbacks_data.name}",
            callback_data=callbacks_data.pack()
        )
    builder.adjust(2, repeat=True)
    return builder.as_markup()

def search_recipes_keyboard_markup(recipe_list:list[dict], offset:int|None=None, skip:int|None=None):
    builder = InlineKeyboardBuilder()

    for index, recipe_data in enumerate(recipe_list):
        callbacks_data = SearchRecipeCallback(id=index, **recipe_data)
        builder.button(
            text=f"{callbacks_data.name}",
            callback_data=callbacks_data.pack()
        )
    builder.adjust(2, repeat=True)
    return builder.as_markup()

def recipes_switch_keyboard_markup():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"◀️Минулий рецепт",
        callback_data="recipe_BACK"
    )
    builder.button(
        text=f"Наступний рецепт▶️",
        callback_data="recipe_NEXT"
    )
    builder.adjust(3, repeat=False)
    return builder.as_markup()