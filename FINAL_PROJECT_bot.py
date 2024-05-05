import telebot
from FINAL_PROJECT_database import *
from FINAL_PROJECT_gpt import *
import math
from FINAL_PROJECT_speechkit import *
from FINAL_PROJECT_config import *
import logging

TOKEN = bot_token
bot = telebot.TeleBot(TOKEN)
create_database()

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logging.txt",
    filemode="w",
)


def is_gpt_token_limit(text, used_tokens):
    system_prompt_text = SYSTEM_PROMPT[0]["text"]
    all_tokens = count_gpt_tokens(text) + count_gpt_tokens(system_prompt_text) + used_tokens
    if all_tokens > MAX_GPT_TOKENS:
        return True

def is_stt_block_limit(our_user_id, duration):
    audio_blocks = math.ceil(duration / 15)
    used_blocks=count_all_limits(our_user_id,"stt_blocks")
    if audio_blocks+used_blocks > MAX_USER_STT_BLOCKS:
        return True, audio_blocks
    else:
        return False, audio_blocks

def is_tts_symbol_limit(our_user_id, text):
    tts_symbols=len(text)
    used_tts_symbols=count_all_limits(our_user_id,"tts_symbols")
    if tts_symbols + used_tts_symbols > MAX_USER_TTS_SYMBOLS:
        return True, tts_symbols
    else:
        return False, tts_symbols

@bot.message_handler(commands=["start"])
def start_dialogue(message):
    bot.send_message(message.chat.id,"Привет. Я твой виртуальный друг. Со мной ты можешь общаться на разные темы."
                                     "Отправь текст или голосовое сообщение.")

@bot.message_handler(commands=["help"])
def help_user(message):
    bot.send_message(message.chat.id, "Доступные команды:\n"
                                      "/start - начать общение с ботом\n"
                                      "/help - список команд\n"
                                      "/stt - проверка распознавания речи\n"
                                      "/tts - проверка синтеза речи\n"
                                      "/debug - отправка файла с логами")

@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("logging.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['tts'])
def tts_handler(message):
    our_user_id = message.from_user.id
    bot.send_message(our_user_id, 'Это команда для проверки синтеза речи.'
                                  'Отправь следующим сообщением текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)

def tts(message):
    our_user_id = message.from_user.id
    if message.content_type != 'text':
        bot.send_message(our_user_id, 'Отправь текстовое сообщение')
        bot.register_next_step_handler(message, tts)
        return

    text = message.text
    limit, tts_symbols = is_tts_symbol_limit(our_user_id, text)
    if limit:
        bot.send_message(message.chat.id, "Превышен лимит символов на озвучку текста. "
                                          "Вы не можете пользоваться этой командой")
        logging.info(f"Пользователь {our_user_id} достиг лимита символов для синтеза речи.")
        return
    if tts_symbols >= 100:
        msg = f"Превышен лимит символов в одном запросе, в сообщении {tts_symbols} символов. Напишите короче."
        bot.send_message(our_user_id, msg)
        bot.register_next_step_handler(message, tts)
        return
    success, response = text_to_speech(text)
    if success:
        bot.send_voice(our_user_id, response)
        add_message(our_user_id, "NULL","user", 0, tts_symbols,0)
    else:
        bot.send_message(our_user_id, response)

@bot.message_handler(commands=['stt'])
def stt_handler(message):
    our_user_id = message.from_user.id
    bot.send_message(our_user_id, 'Это команда для проверки распознавания речи. Отправь следующим сообщением аудиозапись.')
    bot.register_next_step_handler(message, stt)

def stt(message):
    our_user_id = message.from_user.id
    if not message.voice:
        bot.send_message(our_user_id, 'Отправь аудиозапись!')
        bot.register_next_step_handler(message, stt)
        return
    duration = message.voice.duration
    limit, stt_blocks = is_stt_block_limit(our_user_id, duration)
    if limit:
        bot.send_message(message.chat.id, "Превышен лимит блоков на распознавание речи. "
                                          "Вы не можете пользоваться этой командой")
        logging.info(f"Пользователь {our_user_id} достиг лимита аудиблоков.")
        return
    if duration >= 30:
        bot.send_message(our_user_id, "Ваше голосовое сообщение должно быть меньше 30 сек. Попробуйте ещё раз.")
        bot.register_next_step_handler(message, stt)
        return
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    success, response = speech_to_text(file)

    if success:
        bot.send_message(our_user_id, response, reply_to_message_id=message.id)
        add_message(our_user_id, "NULL", "user", 0, 0, stt_blocks)
    else:
        bot.send_message(our_user_id, response)

@bot.message_handler(content_types=["text"])
def text_message(message):
    our_user_id=message.from_user.id
    if count_users(our_user_id) >= MAX_USERS:
        logging.info("Количество пользователей бота максимально.")
        bot.send_message(message.chat.id, "Извините, количество пользователей бота превышено.")
        return
    text = message.text
    add_message(our_user_id, text, "user",0,0,0)
    messages, used_tokens = select_n_last_messages(our_user_id)

    if is_gpt_token_limit(text,used_tokens):
        bot.send_message(message.chat.id,f"Превышен общий лимит GPT-токенов {MAX_GPT_TOKENS}")
        logging.info(f"Пользователь {our_user_id} превысил лимит токенов")
        return

    success, result = ask_gpt(messages)
    if success:
        bot.send_message(message.chat.id, result)
        logging.info(f"Запрос пользователя {our_user_id} к GPT выполнен.")
        tokens = used_tokens+count_gpt_tokens(text)+count_gpt_tokens(result)
        add_message(our_user_id, result, "assistant", tokens, 0,0)
    else:
        bot.send_message(message.chat.id, result)


@bot.message_handler(content_types=["voice"])
def voice_message(message):
    our_user_id = message.from_user.id
    if count_users(our_user_id) >= MAX_USERS:
        logging.info("Количество пользователей бота максимально.")
        bot.send_message(message.chat.id, "Извините, количество пользователей бота превышено.")
        return

    duration = message.voice.duration
    limit_stt_blocks, audio_blocks = is_stt_block_limit(our_user_id, duration)
    if limit_stt_blocks:
        bot.send_message(message.chat.id, "Извините, количество блоков для голосовых сообщений закончилось. "
                                          "Вы можете отправить текстовое сообщение")
        logging.info(f"Пользователь {our_user_id} достиг лимита аудиблоков.")
        return
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    success_stt, text = speech_to_text(file)
    if success_stt:
        add_message(our_user_id, text, "user", 0, 0, audio_blocks)
    else:
        bot.send_message(message.chat.id, "Возникла ошибка при взаимодействии с Speechkit. "
                                          "Попробуйте отправить текстовое сообщение")
        return

    messages, used_tokens = select_n_last_messages(our_user_id)

    if is_gpt_token_limit(text, used_tokens):
        bot.send_message(message.chat.id, f"Превышен общий лимит GPT-токенов {MAX_GPT_TOKENS}")
        logging.info(f"Пользователь {our_user_id} превысил лимит токенов")
        return

    success_ask_gpt, result = ask_gpt(messages)
    if success_ask_gpt:
        logging.info(f"Запрос пользователя {our_user_id} к GPT выполнен.")
        tokens = used_tokens + count_gpt_tokens(text) + count_gpt_tokens(result)
        limit_tts_symbols, tss_symbols = is_tts_symbol_limit(our_user_id, result)
        if limit_tts_symbols:
            bot.send_message(message.chat.id, "Превышен лимит символов на озвучку текста, бот будет отправлять текстовые сообщения.")
            bot.send_message(message.chat.id, result)
            logging.info(f"Пользователь {our_user_id} достиг лимита символов для синтеза речи.")
            add_message(our_user_id, result, "assistant", tokens, 0, 0)
            return
        success_tts, response = text_to_speech(result)
        if success_tts:
            add_message(our_user_id, result, "assistant", tokens, tss_symbols , 0)
            bot.send_voice(our_user_id, response)
        else:
            bot.send_message(message.chat.id, response)
            bot.send_message(message.chat.id, result)
            add_message(our_user_id, result, "assistant", tokens, 0, 0)
    else:
        bot.send_message(message.chat.id, result)



bot.polling()