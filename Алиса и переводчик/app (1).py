from flask import Flask, request
import logging
import json
from requests import get

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я умею переводить! Напиши: "Переведи '\
                                  '%слово или фразу, которое надо перевести%"'

        return

    if req['request']['nlu']['tokens'][0].lower() == 'переведи':
        print(translate(
            " ".join(req['request']['original_utterance'].split(' ')[1:])
        ).strip('%'))
        res['response']['text'] = translate(
            " ".join(req['request']['original_utterance'].split(' ')[1:]).strip('%')
        )
    else:
        res['response']['text'] = 'Я тебя не поняла. Напиши: "Переведи '\
                                  '%слово или фразу, которое надо перевести%"'


def translate(text) -> str:
    headers = {
        'X-RapidAPI-Host': 'translated-mymemory---translation-memory.p.rapidapi.com',
        'X-RapidAPI-Key': 'c19aab3253msh3f62a3d03457b98p150e06jsnd6095ccb5862'

    }
    params = {
        'langpair': 'ru|en',
        'q': text,
    }
    translate = get('https://translated-mymemory---translation-memory.p.rapidapi.com/api/get', headers=headers,
                    params=params).json()[
        'responseData']['translatedText']

    return translate.strip('%')


if __name__ == '__main__':
    app.run()
