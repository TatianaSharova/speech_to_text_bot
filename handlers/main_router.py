import json
import os

from aiogram import Bot, F, Router
from aiogram.types import Message
from openai.error import APIError, OpenAIError, PermissionError

from config import logging
from exceptions import FileNotFoundInSavedFilesDir, TooBigFile

from .audio_file import save_audio_file
from .transcribation import audio_to_text, process_audio_for_transcription
from .utils import send_text
from .video_note import get_audio_from_video_note
from .voice import save_voice_as_mp3

router: Router = Router()


@router.message(F.text)
async def say_hello(message: Message, bot: Bot) -> Message:
    '''При получении текстового сообщения описывает свои возможности.'''
    await message.answer(
        'Я бот, пришли мне голосовое, видеосообщение или аудиофайл, '
        'и я его транскрибирую.'
    )


@router.message(F.content_type.in_({'voice', 'video_note', 'audio'}))
async def speech_to_text(message: Message, bot: Bot) -> Message:
    '''
    Принимает голосовое, видео сообщение или аудиофайл,
    транскрибирует его в текст,
    затем удаляет скачанный аудио файл.
    '''
    try:
        if message.voice:
            path = await save_voice_as_mp3(bot, message.voice)
        if message.video_note:
            path = await get_audio_from_video_note(bot, message.video_note)
        if message.audio:
            path = await save_audio_file(bot, message.audio)
    except TooBigFile as error:
        await message.reply(
            text=f'Расшифровать аудио не удалось.\n'
            f'Ошибка: {error}'
        )
        return

    result = await process_audio_for_transcription(path)
    await send_text(result, message, bot)

    # try:
    #     transcripted_voice_text = await audio_to_text(path)
    # except (PermissionError, json.decoder.JSONDecodeError,
    #         APIError, OpenAIError, Exception) as error:
    #     logging.error(error)
    #     await message.reply(
    #         text=f'Расшифровать аудио не удалось.\n'
    #         f'Ошибка: {error}'
    #     )
    #     return

    # await send_text(transcripted_voice_text, message, bot)

    try:
        os.remove(f'{path}')
        logging.info('Аудиофайл удалён локально.')
    except FileNotFoundError as error:
        raise FileNotFoundInSavedFilesDir(f'{error}')
