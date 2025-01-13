import json
import os

import openai
from dotenv import load_dotenv
from openai.error import APIError, OpenAIError, PermissionError

from config import logging
from exceptions import (AiAccessException, CustomPermissionError,
                        HTTPResponseParsingError, OpenAiAccessError)

load_dotenv()


openai.api_key = os.getenv('OPENAI_API_KEY')


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
