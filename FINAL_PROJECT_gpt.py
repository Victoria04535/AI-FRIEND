import logging

import requests
from FINAL_PROJECT_config import *

SYSTEM_PROMPT = [{'role': 'system', 'text': "Ты саркастический и язвительный друг пользователя."
                                            "Общайся с пользователем на 'ты'."
                                            "Отвечай на его слова. Шути и подкалывай пользователя. Отвечай коротко."
                                            "Задавай пользователю вопросы о его жизни. Если нужно, давай советы."
                                            "Не объясняй пользователю, что ты умеешь и можешь."}]

def ask_gpt(messages):
    token = my_iam_token
    folder_id = my_folder_id
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 100
        },
        "messages": SYSTEM_PROMPT + messages
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            result = f"Произошла ошибка. Status code {response.status_code}. Попробуйте начать сначала."
            logging.error(f"Ошибка {response.status_code} при взаимодействии с GPT")
            return False, result
        answer = response.json()['result']['alternatives'][0]['message']['text']
        return True, answer
    except Exception as e:
        result = "Произошла непредвиденная ошибка. Попробуйте позднее"
        logging.error(e)
        return False, result


def count_gpt_tokens(text):
    token = my_iam_token
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://b1g2j83vf7n15e68iima/yandexgpt/latest",
       "maxTokens": 1000,
       "text": text
    }
    try:
        return len(
            requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
                json=data,
                headers=headers
            ).json()['tokens']
        )
    except Exception as e:
        logging.error(e)
        return 0
