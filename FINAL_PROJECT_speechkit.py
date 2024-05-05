import logging
import requests
from FINAL_PROJECT_config import *

def speech_to_text(data):
    iam_token = my_iam_token
    folder_id = my_folder_id

    params = "&".join([
        "topic=general",
        f"folderId={folder_id}",
        "lang=ru-RU"
    ])

    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    response = requests.post(
        f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
        headers=headers,
        data=data
    )

    decoded_data = response.json()

    if decoded_data.get("error_code") is None:
        logging.info("Речь успешно распознана.")
        return True, decoded_data.get("result")
    else:
        logging.error("Ошибка при взаимодействии с SpeechKit")
        return False, "При запросе в SpeechKit возникла ошибка"

def text_to_speech(text: str):
    iam_token = my_iam_token
    folder_id = my_folder_id

    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'ermil',
        'folderId': folder_id,
    }

    response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)

    if response.status_code == 200:
        logging.info("Речь успешно синтезирована.")
        return True, response.content
    else:
        logging.error("Ошибка при взаимодействии с SpeechKit")
        return False, f"{response.status_code}При запросе в SpeechKit возникла ошибка"
