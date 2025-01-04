from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

RECIPES_COMMAND = Command("recipes")
SEARCH_COMMAND = Command("search")
CREATE_RECIPE_COMMAND = Command("create_recipe")

START_BOT_COMMAND = BotCommand(command="start", description="Почати розмову")
RECIPES_BOT_COMMAND = BotCommand(command="recipes", description="Перегляд списку рецептів")
SEARCH_BOT_COMMAND = BotCommand(command="search", description="Знайти рецепт за інгредієнтами")
CREATE_RECIPE_BOT_COMMAND = BotCommand(command="create_recipe", description="Створити рецепт")

