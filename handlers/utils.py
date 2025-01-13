import os
from typing import Union

from aiogram import Bot
from aiogram.types import Audio, FSInputFile, Message, VideoNote, Voice

from config import logging
from exceptions import TooBigFile


async def send_text(text: str, message: Message, bot: Bot) -> None:
    '''Отправляет ответ пользователю в виде сообщения или файла txt.'''
    if len(text) > 4096:
        logging.info('Ответ слишком большой, создаем текстовый файл.')
        if message.audio:
            text_file_path = await create_text_file(
                message.audio.file_name, text)
        else:
            text_file_path = await create_text_file(
                f'text-{message.message_id}', text)
        await message.answer_document(FSInputFile(text_file_path))
        os.remove(f'{text_file_path}')
        logging.info('Файл успешно отправлен и удален локально.')
    else:
        await message.reply(text=text)
        logging.info('Транскрибированный текст успешно отправлен '
                     'пользователю.')


async def create_text_file(file_name: int, text: str) -> str:
    '''Сохраняет слишком длинный текст в файл txt.'''
    file_path = f'text_files/{file_name}.txt'

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

    return file_path


async def check_file_size(
        file: Union[VideoNote, Voice, Audio]
) -> None:
    '''
    Проверяет размер файла.
    Если размер больше 20 МБ, выбрасывает исключение.
    '''
    if file.file_size > 20 * 1024 * 1024:
        raise TooBigFile('Файл слишком большой. '
                         'Максимальный размер: 20 МБ.')
    logging.info('Скачиваемый файл весит меньше 20 МБ.')
