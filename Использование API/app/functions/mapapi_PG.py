import random
import requests
import sys
from functions.geocoder import get_ll_span

L_VALUES = ['map', 'sat']


def return_all(places: list):
    map_files_list = []
    for i, place in enumerate(places):
        map_files_list.append(return_map(place=place, count=i))
    return map_files_list


def return_map(place='Москва', count=1):
    ll, spn = get_ll_span(place)
    params = {
        "ll": ll,
        "spn": spn,
        "l": 'sat',
        "pt": f'{ll},pm2rdm',
        'lang': 'ru_RU'
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=params)
    if not response:
        print("Ошибка выполнения запроса:")
        print(response.url)
        print(f"Http статус: {response.status_code} ({response.reason})")
        sys.exit(1)
    map_file = f"img/map{count}.png"
    try:
        with open('static/' + map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    return map_file


