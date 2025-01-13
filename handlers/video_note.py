'''Модуль для работы с видеосообщениями.'''

import os

from aiogram import Bot
from aiogram.types import VideoNote
from moviepy.editor import VideoFileClip
from openai.error import PermissionError

from config import logging
from exceptions import (CustomPermissionError, CustomValueError,
                        FileNotFoundInSavedFilesDir)

from .utils import check_file_size


async def get_audio_from_video_note(bot: Bot, video: VideoNote) -> str:
    '''
    Локально скачивает видеосообщение и сохраняет в формате mp4,
    извлекает аудио из скачанного видео, удаляет скачанное видео и
    возвращает путь к извлеченному аудиофайлу.
    '''
    logging.info('Скачиваем видеосообщение.')
    await check_file_size(video)
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
