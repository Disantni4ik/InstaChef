import json
from aiogram.types import CallbackQuery
from keyboards import recipes_switch_keyboard_markup
import logging

def get_recipes(file_path: str = "recipes_list.json", recipe_id: int | None = None) -> list[dict] | dict:
    with open(file_path, "r", encoding="utf-8") as file:
        recipes = json.load(file)
        if recipe_id != None and recipe_id < len(recipes):
            return recipes[recipe_id]
        return recipes

def add_recipe(recipe: dict, file_path: str = "recipes_list.json"):
    recipes = get_recipes(file_path=file_path, recipe_id=None)
    if recipes:
        recipes.append(recipe)
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(recipes, fp, indent=4, ensure_ascii=False)
        logging.info(f"Новий фільм додано в {file_path}\n {recipes}")

def search_ingredients(user_msg: dict, file_path : str = "recipes_list.json"):
    suitable_recipes = list()
    with open(file_path, "r", encoding="utf-8") as fl:
        recipes = json.load(fl)
        for full_recipe in recipes:
            identical_ingredients = 0
            user_msg_list = user_msg["text"].lower().split(", ")
            for x in user_msg_list:
                for ingredient in full_recipe["ingredients"]:
                    ingredient = ingredient.split(" -")[0]
                    if ingredient == x:
                        identical_ingredients += 1

                if identical_ingredients >= 2 and full_recipe not in suitable_recipes:
                    suitable_recipes.append(full_recipe)

        return suitable_recipes


def show_recipe(callback: CallbackQuery, recipe, markup = recipes_switch_keyboard_markup()):
    text = f"🍲 Страва: {recipe.name}\n\n" \
           f"🛒 Ігнредієнти:\n{','.join(recipe.ingredients)}\n" \
           f"👨‍🍳 Інструкція:\n{recipe.instructions}\n"

    if markup is None:
        return callback.message.answer_photo(
            caption=text,
            photo=
            recipe.image,
            filename=f"{recipe.name}_image.{recipe.image.split('.')[-1]}")

    else:
        return callback.message.answer_photo(
            reply_markup=markup,
            caption=text,
            photo=
            recipe.image,
            filename=f"{recipe.name}_image.{recipe.image.split('.')[-1]}"
        )
