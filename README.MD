# **Speech to text telegram bot**

![.github/workflows/main.yaml](https://github.com/TatianaSharova/speech_to_text_bot/actions/workflows/main.yml/badge.svg)

Телеграм бот, который может транскрибировать голосовое или видеосообщение c помощью системы по распознаванию речи Whisper от OpenAI. Бот работает со всеми языками и транскрибирует полученное сообщение на том языке, на котором оно было записано.  

**Stack**: Python, Pytest, Aiogram, Asyncio, pydub, Whisper, Github Actions, Heroku.

Настроен CI проекта в GitHub Actions: код проверяется по стандарту PEP8, и выполняются Pytest тесты на проверку доступа к API OpenAI.
CD бота настроен на Heroku.

**План по доработке:**
1. Обработать ошибку при слишком больших файлах.
2. Для транскрибации интервью добавить подписи к говорящим, например, спикер1\спикер2.

### Локальный запуск бота:
--------------------------

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
**_Для CI проекта, добавьте в GitHub Actions новый secret:_**
```
OPENAI_API_KEY             - ваш токен, полученный от OpenAI
```

### Запуск бота на сервере Heroku и настройка CD:  
-------------------------------------------------

**_Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)_**  

**_После установки войдите в свой аккаунт, для этого введите в терминал:_**  
```
heroku login
```
**_Создайте новое приложение:_**
```
cd your_app/
```
```
heroku create speechbot
```
**_Запушьте ваш код на сервер:_**
```
git init
```
```
git add .
```
```
git commit -m'my first commit'
```
```
git push heroku main
```
**_Задайте переменные окружения:_**
```
heroku config:set TELEGRAM_BOT_TOKEN=токен вашего телеграм бота
heroku config:set OPENAI_API_KEY=ваш токен, полученный от OpenAI
```
**_Устанавливаем ffmpeg на сервер:_**
```
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```
**_Включаем бот:_**
```
heroku ps:scale worker=1
```

### Автор
[Татьяна Шарова](https://github.com/TatianaSharova)
