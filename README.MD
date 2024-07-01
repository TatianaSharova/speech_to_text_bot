# **Speech to text telegram bot**

[![Build Status](https://github.com/TatianaSharova/speech_to_text_bot/workflows/SpeechBotWorkflow/badge.svg)](https://github.com/TatianaSharova/speech_to_text_bot/actions/workflows/main.yml)


[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![OpenAI](https://a11ybadges.com/badge?logo=openai)](https://openai.com/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/)

Телеграм бот, который может транскрибировать голосовое или видеосообщение c помощью системы по распознаванию речи Whisper от OpenAI. Бот работает со всеми языками и транскрибирует полученное сообщение на том языке, на котором оно было записано.

### Локальный запуск бота:

**_Склонировать репозиторий к себе_**
```
git@github.com:TatianaSharova/speech_to_text_bot.git
```
**_В директории проекта создать файл .env и заполнить своими данными:_**
```
TELEGRAM_BOT_TOKEN         - токен вашего телеграм бота
OPENAI_API_KEY             - ваш токен, полученный от OpenAI
```
**_Создать и активировать виртуальное окружение:_**

Для Linux/macOS:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Для Windows:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
**_Установить зависимости из файла requirements.txt:_**
```
pip install -r requirements.txt
```
**_Ввести команду в терминал (для установки ffmpeg):_**
```
ffdl install
```
**_Запустить бот:_**
```
python bot.py
```
```
Если у вас вылетает ошибка PermissionError, включите VPN.
```

### Автор
Татьяна Шарова