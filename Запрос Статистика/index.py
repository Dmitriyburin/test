from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
from flask_restful import Api

from statistics import statistics

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def main():
    app.run(debug=True)


@app.route("/vk_stat/<int:group_id>")
def index(group_id: int):
    if not statistics(group_id):
        return 'Ошибка: не удалось получить доступ к группе'

    activities, ages, cities = statistics(group_id)
    return render_template("index.html", activities=activities, ages=ages, cities=cities)


if __name__ == '__main__':
    main()
