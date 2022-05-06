from flask import Flask, render_template, redirect, request, abort, url_for, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
from flask_restful import Api

from forms.user import RegisterForm, LoginForm
from forms.job import JobForm
from data.users import User
from data.jobs import Jobs
from data import db_session, jobs_api, user_api, users_resources, jobs_resources

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/lesson.db")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    api.add_resource(users_resources.UsersListResource, '/api/v2/users')
    api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')
    api.add_resource(jobs_resources.JobsListResource, '/api/v2/jobs')
    api.add_resource(jobs_resources.JobsResource, '/api/v2/jobs/<int:job_id>')

    app.run(debug=True)


@app.route("/")
def index():
    print(current_user.id if current_user.is_authenticated else None)
    url_style = url_for('static', filename='css/style.css')
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template("index.html", jobs=jobs, url_style=url_style)


@app.route("/job/<job_id>", methods=['GET', 'POST'])
def job(job_id):
    url_style = url_for('static', filename='css/style.css')
    form = JobForm()

    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == job_id, Jobs.team_leader.in_([current_user.id, 1])).first()
        if jobs:
            form.job.data = jobs.job
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == job_id, Jobs.team_leader.in_([current_user.id, 1])).first()
        if jobs:
            jobs.job = form.job.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
        else:
            abort(404)
        db_sess.commit()
        return redirect('/')

    return render_template("job.html", url_style=url_style, form=form)


@app.route("/delete_job/<int:job_id>", methods=['GET', 'POST'])
def delete_job(job_id):
    db_sess = db_session.create_session()
    if not isinstance(current_user, AnonymousUserMixin):
        job = db_sess.query(Jobs).filter(Jobs.id == job_id, Jobs.team_leader == current_user.id).first()
        if job:
            db_sess.delete(job)
            db_sess.commit()
        else:
            abort(404)

    return redirect('/')


@app.route("/add_job", methods=['GET', 'POST'])
def add_job():
    url_style = url_for('static', filename='css/style.css')
    form = JobForm()
    print(form.validate_on_submit())

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs(
            team_leader=current_user.id,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data
        )

        db_sess.add(job)
        db_sess.commit()

        return redirect('/')

    return render_template("job.html", url_style=url_style, form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    url_style = url_for('static', filename='css/style.css')

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            hashed_password=form.password.data,
            surname=form.surname.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,

        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('login.html', title='Регистрация', form=form, url_style=url_style)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    url_style = url_for('static', filename='css/style.css')

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form, url_style=url_style)


if __name__ == '__main__':
    main()
