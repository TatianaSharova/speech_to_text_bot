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


#openai.api_key = os.getenv('OPEN_AI_TOKEN')

token = openai.api_key
t = os.getenv('OPEN_AI_TOKEN')

print(token,t)