import asyncio
import os
import sys

import openai
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from config import logging
from handlers.main_router import router

load_dotenv()


openai.api_key = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(level=logging.INFO)


def check_tokens() -> bool:
    '''Проверка доступности необходимых переменных окружения.'''
    logging.info('Проверка доступности переменных окружения.')
    tokens = [openai.api_key, TELEGRAM_BOT_TOKEN]
    if all(tokens):
        logging.info('Проверка успешно пройдена.')
    return all(tokens)


async def main():
    if not check_tokens():
        logging.critical('Отсутствуют необходимые переменные окружения.')
        sys.exit(1)
    bot: Bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp: Dispatcher = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)

    while True:
        await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
