import asyncio
import io
import json
import logging
import os
import sys

import openai
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, VideoNote, Voice, Audio
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
from openai.error import APIError, OpenAIError, PermissionError
from pydub import AudioSegment

from exceptions import (AiAccessException, CustomPermissionError,
                        CustomValueError, FileNotFoundInSavedFilesDir,
                        HTTPResponseParsingError, OpenAiAccessError)

load_dotenv()


openai.api_key = os.getenv('OPENAI_API_KEY')
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
        

        # Сохранение текста в файл
        output_path = os.path.splitext(file_path)[0] + '.txt'
        with open(output_path, 'w', encoding='utf-8') as text_file:
            text_file.write(transcript['text'])
        logging.info(f'Текст сохранён в файл: {output_path}')



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


async def save_audio_file(bot: Bot, audio: Audio) -> str:
    '''
    Сохраняет аудиофайл, отправленный пользователем, локально.
    Возвращает путь к сохранённому файлу.
    '''
    file = await bot.get_file(audio.file_id)
    file_path = file.file_path
    local_path = f'voice_files/audio-{audio.file_unique_id}.mp3'

    await bot.download_file(file_path, destination=local_path)
    logging.info(f'Аудио успешно скачано.'
                 f'file path - {local_path}.')
    return local_path



@router.message(F.text)
async def say_hello(message: Message, bot: Bot) -> Message:
    '''При получении текстового сообщения описывает свои возможности.'''
    await message.answer(
        'Я бот, пришли мне голосовое или видеосообщение, '
        'и я его транскрибирую.'
    )


@router.message(F.content_type.in_({'voice', 'video_note', 'audio'}))
async def speech_to_text(message: Message, bot: Bot) -> Message:
    '''
    Принимает голосовое, видео сообщение или аудиофайл, транскрибирует его в текст,
    затем удаляет скачанный аудио файл.
    '''
    if message.voice:
        path = await save_voice_as_mp3(bot, message.voice)
    if message.video_note:
        path = await get_audio_from_video_note(bot, message.video_note)
    if message.audio:
        path = await save_audio_file(bot, message.audio)

    try:
        transcripted_voice_text = await audio_to_text(path)
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
        os.remove(f'{path}')
        logging.info('Аудиофайл удалён локально.')
    except FileNotFoundError as error:
        raise FileNotFoundInSavedFilesDir(f'{error}')


async def get_audio_from_video_note(bot: Bot, video: VideoNote) -> str:
    '''
    Локально скачивает видеосообщение и сохраняет в формате mp4,
    извлекает аудио из скачанного видео, удаляет скачанное видео и
    возвращает путь к извлеченному аудиофайлу.
    '''
    logging.info('Скачиваем видеосообщение.')
    video_file = await bot.get_file(video.file_id)
    video_path = f'video/{video.file_unique_id}.mp4'
    await bot.download_file(video_file.file_path, video_path)
    logging.info('Видеосообщение успешно скачано. '
                 'Начинаем извлекать аудио из видео.')
    try:
        clip = VideoFileClip(video_path)
    except ValueError as error:
        raise CustomValueError(error)
    audio_path = f'voice_files/voice-{video.file_unique_id}.mp3'
    try:
        clip.audio.write_audiofile(audio_path)
        logging.info('Аудио успешно извлечено.')
    except ValueError as error:
        raise CustomValueError(error)
    finally:
        clip.close()
    try:
        logging.info('Начинаем удаление видеофайла.')
        os.remove(video_path)
        logging.info('Видеофайл удалён локально.')
    except PermissionError as error:
        raise CustomPermissionError(
            f'Видеофайл не удалён: {error}.'
        )
    except FileNotFoundError as error:
        raise FileNotFoundInSavedFilesDir(error)
    return audio_path


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
