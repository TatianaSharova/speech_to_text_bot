# **Speech to text telegram bot**

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
![OpenAI](https://a11ybadges.com/badge?logo=openai)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

Телеграм бот, который может транскрибировать голосовое или видеосообщение c помощью системы по распознаванию речи Whisper от OpenAI.

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
**_Запустить бот:_**
```
python bot.py
```

### Автор
Татьяна Шарова