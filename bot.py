import asyncio
import io
import json
import logging
import os
import sys

import openai
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, Voice
from dotenv import load_dotenv
from openai.error import APIError, OpenAIError, PermissionError
from pydub import AudioSegment

from exceptions import (AiAccessException, CustomPermissionError,
                        FileNotFoundInVoiceFilesDir, HTTPResponseParsingError,
                        OpenAiAccessError)

load_dotenv()


openai.api_key = os.getenv('OPEN_AI_TOKEN')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

router: Router = Router()

logging.basicConfig(level=logging.INFO)


def check_tokens() -> bool:
    '''Проверка доступности необходимых переменных окружения.'''
    logging.info('Проверка доступности переменных окружения.')
    tokens = [openai.api_key, TELEGRAM_BOT_TOKEN]
    if all(tokens):
        logging.info('Проверка успешно пройдена.')
    return all(tokens)


async def audio_to_text(file_path: str) -> str:
    '''
    Принимает путь к аудио файлу,

    возвращает текст голосового сообщения.
    '''
    logging.info('Начинаем расшифровку аудио.')
    audio_file = open(file_path, 'rb')
    try:
        transcript = await openai.Audio.atranscribe(
            'whisper-1', audio_file
        )
        logging.info(f'Аудио расшифровано. '
                     f'Ответ OpenAI: {transcript}')
    except PermissionError as error:
        raise CustomPermissionError(f'Доступ сервера к OpenAI запрещён. '
                                    f'Причина: {error}')
    except json.decoder.JSONDecodeError as error:
        raise HTTPResponseParsingError(error)
    except APIError as error:
        raise AiAccessException(error)
    except OpenAIError as error:
        raise OpenAiAccessError(error)
    finally:
        audio_file.close()

    return transcript['text']


async def save_voice_as_mp3(bot: Bot, voice: Voice) -> str:
    '''Локально скачивает голосовое сообщение и сохраняет в формате mp3.'''
    logging.info('Скачиваем аудио.')
    voice_file = await bot.get_file(voice.file_id)
    voice_ogg = io.BytesIO()
    await bot.download_file(voice_file.file_path, voice_ogg)
    logging.info(f'Аудио успешно скачано.'
                 f'file path -{voice_file.file_path}.')

    logging.info('Конвертируем аудио в mp3.')
    voice_mp3_path = f'voice_files/voice-{voice.file_unique_id}.mp3'
    AudioSegment.from_file(
        voice_ogg, format='ogg'
        ).export(voice_mp3_path, format='mp3')
    logging.info('Файл в формате mp3 создан.')
    return voice_mp3_path


@router.message(F.content_type == 'voice')
async def process_voice_message(message: Message, bot: Bot):
    '''
    Принимает голосовое сообщение, транскрибирует его в текст,
    затем удаляет скачанный аудио файл.
    '''
    try:
        voice_path = await save_voice_as_mp3(bot, message.voice)
    except Exception as error:
        logging.error(error)
    try:
        transcripted_voice_text = await audio_to_text(voice_path)
    except (PermissionError, json.decoder.JSONDecodeError,
            APIError, OpenAIError, Exception) as error:
        transcripted_voice_text = None
        message_error = error
        logging.error(error)

    if transcripted_voice_text:
        await message.reply(text=transcripted_voice_text)
    else:
        await message.reply(
            text=f'Расшифровать голосовое сообщение не удалось. '
            f'Ошибка: {message_error}'
        )

    try:
        os.remove(f'{voice_path}')
        logging.info('Файл удалён локально.')
    except FileNotFoundError as error:
        raise FileNotFoundInVoiceFilesDir(f'{error}')


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


if __name__ == "__main__":
    asyncio.run(main())
