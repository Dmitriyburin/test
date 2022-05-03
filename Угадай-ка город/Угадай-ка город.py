import random
from flask import Flask, render_template, url_for

from functions.geocoder import get_ll_span
from functions.mapapi_PG import return_all

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
CITIES = ['Москва', 'Токио', 'Нью-Йорк', 'Дубаи', 'Пекин']
L_VALUES = ['map', 'sat']


@app.route("/")
def index():
    random.shuffle(CITIES)
    images = return_all(CITIES)
    url_images = [url_for('static', filename=img) for img in images]
    print(url_images)
    return render_template('index.html', url_images=url_images)


if __name__ == '__main__':
    app.run()