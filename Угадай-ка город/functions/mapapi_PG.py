import pygame
import requests
import sys
import os


def show_map(params=None, text=None):
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(response.url)
        print(f"Http статус: {response.status_code} ({response.reason})")
        sys.exit(1)

    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(map_file), (0, 0))

    if text:
        font = pygame.font.Font(None, 20)
        for i in range(len(text)):
            line = font.render(text[i], True, (0, 0, 0))
            screen.blit(line, (5, 5 + i * 25))

    while pygame.event.wait().type != pygame.QUIT:
        pygame.display.flip()

    pygame.quit()
    os.remove(map_file)
