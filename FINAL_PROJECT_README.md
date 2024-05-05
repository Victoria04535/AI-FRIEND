# Бот-собеседник

Телеграм бот, который может общаться с пользователем на разные
темы.

## Описание

Пользователь может общаться с ботом с помощью текста или голосовых сообщений.
Ответы бота генерируются нейросетью.
Бот присылает пользователю ответ в том же формате, в котором 
пользователь присылал запрос: текст в ответ на текст, голос в ответ на голос.
В боте ограничено количество пользователей, а также токенов на запросы 
к GPT, блоков для разпознавания речи и символов для синтеза речи.

## Инструкции по использованию
- Начало использования:
  - Найди бота в Telegram: @Practicum_gpt_helper_bot.
  - Запусти бота командой /start.
  
- Отправление сообщений:
  - Отправьте боту голосовое или текстлвое сообщение.
  - После этого бот пришлет вам ответ.
- Проверка синтеза речи:
  - Чтобы проверить синтез речи, используйте команду /tts.
- Проверка разпознования речи:
  - Чтобы проверить распознование речи, используйте команду /stt. 
- Логирование:
  - Чтобы получить файл с логами ошибок, используйте команду /debug.

## Нейросеть 

В боте использована нейросеть YandexGPT Lite, а также Yandex Speechkit. 
