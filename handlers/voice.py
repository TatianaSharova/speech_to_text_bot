'''Модуль для работы с голосовыми сообщениями.'''

import io

from aiogram import Bot
from aiogram.types import Voice
from pydub import AudioSegment

from config import logging

from .utils import check_file_size


async def save_voice_as_mp3(bot: Bot, voice: Voice) -> str:
    '''Локально скачивает голосовое сообщение и сохраняет в формате mp3.'''
    logging.info('Скачиваем аудио.')
    await check_file_size(voice)
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
