import asyncio
import logging
import io
import os

import openai
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, Voice
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()


openai.api_key = os.getenv('OPEN_AI_TOKEN')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

router: Router = Router()


async def audio_to_text(file_path: str) -> str:
    """Принимает путь к аудио файлу, возвращает текст файла."""
    with open(file_path, "rb") as audio_file:
        transcript = await openai.Audio.atranscribe(
            "whisper-1", audio_file
        )
    return transcript["text"]


async def save_voice_as_mp3(bot: Bot, voice: Voice) -> str:
    """Скачивает голосовое сообщение и сохраняет в формате mp3."""
    voice_file_info = await bot.get_file(voice.file_id)
    voice_ogg = io.BytesIO()
    await bot.download_file(voice_file_info.file_path, voice_ogg)
    
    voice_mp3_path = f"voice_files/voice-{voice.file_unique_id}.mp3"
    AudioSegment.from_file(voice_ogg, format="ogg").export(
	    voice_mp3_path, format="mp3"
	)
    return voice_mp3_path


@router.message(F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot):
    """Принимает голосовое сообщение, транскрибирует его в текст."""
    voice_path = await save_voice_as_mp3(bot, message.voice)
    transcripted_voice_text = await audio_to_text(voice_path)

    if transcripted_voice_text:
        await message.reply(text=transcripted_voice_text)


async def main():
    bot: Bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp: Dispatcher = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())