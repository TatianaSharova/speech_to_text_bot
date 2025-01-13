'''Модуль для работы с аудиофайлами.'''

from aiogram import Bot
from aiogram.types import Audio

from config import logging

from .utils import check_file_size


async def save_audio_file(bot: Bot, audio: Audio) -> str:
    '''
    Локально сохраняет аудиофайл, отправленный пользователем.
    Возвращает путь к сохранённому файлу.
    '''
    logging.info('Скачиваем аудио.')
    await check_file_size(audio)
    file = await bot.get_file(audio.file_id)

    file_path = file.file_path
    local_path = f'voice_files/audio-{audio.file_unique_id}.mp3'

    await bot.download_file(file_path, destination=local_path)
    logging.info(f'Аудио успешно скачано.'
                 f'file path - {local_path}.')
    return local_path
