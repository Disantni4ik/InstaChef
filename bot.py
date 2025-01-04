import asyncio
import logging
import sys
import json
from operator import index
from turtledemo.sorting_animate import instructions1

from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN as TOKEN
from commands import START_BOT_COMMAND, RECIPES_COMMAND, RECIPES_BOT_COMMAND, SEARCH_COMMAND, SEARCH_BOT_COMMAND, CREATE_RECIPE_BOT_COMMAND, CREATE_RECIPE_COMMAND
from keyboards import recipes_keyboard_markup, RecipeCallback, recipes_switch_keyboard_markup, search_recipes_keyboard_markup, SearchRecipeCallback
from model import Recipe
from main_functions import get_recipes, show_recipe, add_recipe, search_ingredients
from states import RecipeForm, UserInput

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, URLInputFile, ReplyKeyboardRemove
from aiogram.client.session.aiohttp import AiohttpSession

from states import RecipeForm

session = AiohttpSession(proxy='http://proxy.server:3128')
ID = 1037707575
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer_photo(caption=f"🍽️ Привіт {message.from_user.full_name}, ласкаво просимо до "
                                       f"SmartChef!👨‍🍳\nЯ тут, щоб допомогти тобі стати шеф-кухарем на власній "
                                       f"кухні!\n\n🎉Ось, що я можу зробити для тебе:\n\n"
                                       f"🥕 Рецепти за інгредієнтами: розкажи, що в тебе є вдома, і я знайду смачні ідеї.\n\n"
                                       f"🕒 Швидкі рецепти: потрібно щось приготувати за 15-30 хвилин? Легко!\n\n"
                                       f"🎯 Для початку:\n- Натисни кнопку <code>Menu</code>, щоб дізнатися всі команди.\n\n",
                                       photo="https://imgur.com/zXxW2tB")

@dp.message(RECIPES_COMMAND)
async def recipes(message: Message) -> None:
        data = get_recipes()
        markup = recipes_keyboard_markup(recipe_list=data)
        await message.answer(f"{html.bold('беріть рецепт нижче')}", reply_markup=markup)

@dp.message(SEARCH_COMMAND)
async def search(message: Message, state: FSMContext):
    await message.answer("Введіть інгредієнти які у вас є🖊️\n"
                         f"{html.bold('Обовязково через кому!')}")
    await state.set_state(UserInput.text)

@dp.message(UserInput.text)
async def find_recipe(message: Message, state: FSMContext, file_path: str = "recipes_list.json"):
    user_message = await state.update_data(text=message.text)
    await state.clear()
    markup = search_recipes_keyboard_markup(recipe_list=search_ingredients(user_message))
    if search_ingredients(user_message):
        await message.answer(text="Ось які рецепти я тобі знайшов👨‍🍳",reply_markup=markup)
    else:
        await message.answer("Нічого не знайдено🤷‍♂️")


@dp.message(CREATE_RECIPE_COMMAND)
async def create_recipe(message: Message, state: FSMContext):
    if message.from_user.id == ID:
        await state.set_state(RecipeForm.name)
        await message.answer(f"Введіть назву страви", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Недостатньо прав!")

@dp.message(RecipeForm.name)
async def recipe_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(RecipeForm.ingredients)
    await message.answer(f"Введіть інгредієнти\n" + html.bold("Обов'язкова кома та відступ після неї"), reply_markup=ReplyKeyboardRemove())

@dp.message(RecipeForm.ingredients)
async def recipe_ingredients(message: Message, state: FSMContext) -> None:
    await state.update_data(ingredients=[x for x in message.text.split(", ")])
    await state.set_state(RecipeForm.instructions)
    await message.answer(f"Напишіть пошагову інструкцію", reply_markup=ReplyKeyboardRemove())

@dp.message(RecipeForm.instructions)
async def recipe_instruction(message: Message, state: FSMContext) -> None:
    await state.update_data(instructions=message.text)
    await state.set_state(RecipeForm.image)
    await message.answer(f"Введіть посилання на зображення страви", reply_markup=ReplyKeyboardRemove())

@dp.message(RecipeForm.image)
async def recipe_image(message: Message, state: FSMContext) -> None:
    data = await state.update_data(image=message.text)
    recipe = Recipe(**data)
    add_recipe(recipe.model_dump())
    await state.clear()
    await message.answer(f"Рецепт додано успішно!", reply_markup=ReplyKeyboardRemove())

@dp.callback_query(RecipeCallback.filter())
async def callback_recipe(callback: CallbackQuery, callback_data:RecipeCallback) -> None:
    global recipe_index
    recipe_index  = callback_data.id
    recipe_data = get_recipes(recipe_id=recipe_index)
    recipe = Recipe(**recipe_data)
    await show_recipe(callback, recipe)

@dp.callback_query(SearchRecipeCallback.filter())
async def callback_search_recipe(callback: CallbackQuery, callback_data: SearchRecipeCallback) -> None:
    with open("recipes_list.json", "r", encoding="utf-8") as fl:
        recipes = json.load(fl)
        for recipe in recipes:
            if recipe["name"] == callback_data.name:
                recipe_id = recipes.index(recipe)

        recipe_data = get_recipes(recipe_id=recipe_id)
        recipe = Recipe(**recipe_data)
        await show_recipe(callback, recipe, None)

@dp.callback_query(lambda callback: "recipe_" in callback.data)
async def switch_recipe(callback: CallbackQuery, file_path: str="recipes_list.json"):
    global recipe_index
    if callback.data == "recipe_BACK":
        recipe_index -= 1
        if recipe_index >= 0:
            recipe_data = get_recipes(recipe_id=recipe_index)
            recipe = Recipe(**recipe_data)

            await show_recipe(callback, recipe)

        else:
            with open(file_path, "r", encoding="utf-8") as file:
                recipes = json.load(file)
                recipe_index = len(recipes) - 1
                recipe_data = get_recipes(recipe_id=recipe_index)
                recipe = Recipe(**recipe_data)

                await show_recipe(callback, recipe)

    elif callback.data == "recipe_NEXT":
        recipe_index += 1
        with open(file_path, "r", encoding="utf-8") as file:
            recipes = json.load(file)
            if recipe_index <= len(recipes) - 1:
                recipe_data = get_recipes(recipe_id=recipe_index)
                recipe = Recipe(**recipe_data)
                await show_recipe(callback, recipe)

            else:
                with open(file_path, "r", encoding="utf-8") as file:
                    recipes = json.load(file)
                    recipe_index = 0
                    recipe_data = get_recipes(recipe_id=recipe_index)
                    recipe = Recipe(**recipe_data)
                    await show_recipe(callback, recipe)

async def main() -> None:

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) #local
    #bot = Bot(token=TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))  # server develop

    await bot.set_my_commands(
        [
            START_BOT_COMMAND,
            RECIPES_BOT_COMMAND,
            SEARCH_BOT_COMMAND,
            CREATE_RECIPE_BOT_COMMAND
        ]
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())