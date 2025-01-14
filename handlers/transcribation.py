import json
import os
import pydub

import openai
from dotenv import load_dotenv
from openai.error import APIError, OpenAIError, PermissionError

from config import logging
from exceptions import (AiAccessException, CustomPermissionError,
                        HTTPResponseParsingError, OpenAiAccessError)
from diarization.speaker_diarization import pipeline

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


def get_diarization_segments(audio_path: str) -> list[dict]:
    """
    Получает сегменты с временными метками для каждого спикера из аудио файла.
    """
    logging.info('Начинаем диарезацию.')
    diarization = pipeline({'uri': 'audio', 'audio': audio_path})
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({'start': turn.start, 'end': turn.end, 'speaker': speaker})
    logging.info('Диарезация успешно закончена.')
    return segments


def split_audio_by_segments(audio_path: str, segments: list[dict]) -> list:
    '''
    Разбивает аудио по сегментам на основе временных меток.
    '''
    logging.info('Делим аудио на фрагменты по спикерам.')
    audio = pydub.AudioSegment.from_mp3(audio_path)  # Загружаем аудио
    segments_audio_paths = []

    for idx, segment in enumerate(segments):
        start_ms = segment['start'] * 1000  # Переводим в миллисекунды
        end_ms = segment['end'] * 1000
        segment_audio = audio[start_ms:end_ms]
        segment_audio_path = f"segment_{idx}.mp3"
        segment_audio.export(segment_audio_path, format="mp3")
        segments_audio_paths.append({'speaker': segment['speaker'], 'path': segment_audio_path})

    return segments_audio_paths


async def process_audio_for_transcription(audio_path: str) -> str:
    '''
    Запускает процес диарезации аудио и возвращает
    текст, разбитый по спикерам.
    '''
    segments = get_diarization_segments(audio_path)
    segments_audio_paths = split_audio_by_segments(audio_path, segments)

    transcripts = {}
    text = ''

    for segment in segments_audio_paths:
        speaker = segment['speaker']
        transcript_text = await audio_to_text(segment['path'])
        if transcript_text:
            if speaker not in transcripts:
                transcripts[speaker] = []
            transcripts[speaker].append(transcript_text)
            text += speaker +'\n' + transcript_text + '\n\n'
            os.remove(segment['path'])  # Удаляем временный файл

    return text


# Вариант фунции, при которой формируется вывод вида:
# start:...
# stop:...
# Transcript: полный текст


# async def audio_to_text(file_path: str) -> str:
#     '''
#     Принимает путь к аудио файлу, выполняет диаризацию и возвращает текст с указанием спикеров.
#     '''
#     logging.info('Начинаем расшифровку аудио.')

#     # Диаризация аудио
#     diarization = pipeline({'uri': 'audio', 'audio': file_path})

#     speaker_segments = {
#         'SPEAKER_00': [],
#         'SPEAKER_01': []
#     }
    
#     # Группируем текст по спикерам
#     for segment, _, speaker in diarization.itertracks(yield_label=True):
#         start_time = segment.start  # Время начала сегмента
#         end_time = segment.end      # Время конца сегмента
#         speaker_id = f"SPEAKER_{speaker}"  # Метка спикера

#         speaker_text = f"start={start_time}s stop={end_time}s speaker_{speaker_id}"
#         speaker_segments[speaker_id].append(speaker_text)

#     # Транскрибируем аудио с использованием OpenAI Whisper
#     with open(file_path, 'rb') as audio_file:
#         try:
#             transcript = await openai.Audio.atranscribe('whisper-1', audio_file)
#             logging.info(f'Аудио расшифровано. Ответ OpenAI: {transcript}')
#         except Exception as error:
#             logging.error(f'Ошибка при транскрибировании аудио: {error}')
#             raise OpenAiAccessError(f'Ошибка при транскрибировании аудио: {error}')

#     # Создаем строку, где текст каждого спикера идет по очереди
#     result = ""
#     for speaker, texts in speaker_segments.items():
#         result += f"{speaker}:\n" + "\n".join(texts) + "\n\n"
#     result += f"Transcript:\n{transcript['text']}"

#     return result
