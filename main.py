import os
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from modules.handlers import router
from modules.libraries.database import init_db

from datetime import datetime
if os.name == 'nt':  ## MARK: CHANGE TOKEN 
    TOKEN_FILE_PATH = 'C:/2501/localbankbot/TOKEN'
else:
    TOKEN_FILE_PATH = '/home/syra/2501/tg_bots/localbankbot/TOKEN'

LOGGING_PATH = './logs'

def read_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            token = file.read().strip()
            return token
    except Exception as e:
        raise ValueError(f"Error reading token from file: {e}")

TOKEN = read_token_from_file(TOKEN_FILE_PATH)
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in the token file. Please check your token.")

async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    init_db()
    await dp.start_polling(bot)

if not os.path.exists(LOGGING_PATH):
    os.makedirs(LOGGING_PATH)
log_filename = f'familystom_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.log'

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s]:%(levelname)s:%(funcName)s:%(message)s',
        datefmt='%Y-%m-%d|%H:%M:%S',
        handlers=[
            logging.FileHandler(f"{LOGGING_PATH}/{log_filename}", mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info(f"Using {'WIN' if os.name == 'nt' else 'UNIX'} base kernel")
    asyncio.run(main())
