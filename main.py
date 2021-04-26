from flask import Flask, jsonify, render_template, redirect, request, make_response, session, abort
from flask_admin.contrib.fileadmin import FileAdmin

from data import db_session, news_api, application_api
from data.application import Application
from data.photo import Photo
from data.users import User
from data.news import News
import datetime

from forms.application import ApplicationsForm
from forms.user import RegisterForm
from forms.loginform import LoginForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os.path as op

from mess_to_vk import mess_to_vk

app = Flask(__name__)
api = Api(app)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

db_session.global_init("db/blogs.db")
# администрирование сайтом
admin = Admin(app, name='хроники серых городов', template_mode='bootstrap4')
db_s = db_session.create_session()
admin.add_view(ModelView(User, db_s))
admin.add_view(ModelView(News, db_s))
admin.add_view(ModelView(Application, db_s))
admin.add_view(ModelView(Photo, db_s))
path2 = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdmin(path2, '/static/', name='Load_photo'))


login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    app.register_blueprint(news_api.blueprint)
    app.register_blueprint(application_api.blueprint)

    port = int(os.environ.get("PORT", 5000))
    print(port)
    app.run(host='0.0.0.0', port=port)

@app.route("/")
def index():
    return render_template("start.html")

@app.route("/home")
def home():
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    return render_template("index.html", news=news)

@app.route('/applications')
def applications():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        applic = db_sess.query(Application).filter(
            (Application.user == current_user))
    else:
        applic = False
    return render_template("applic.html", applic=applic)

@app.route("/add_applications", methods=['GET', 'POST'])
@login_required
def add_applications():
    form = ApplicationsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        applic = Application()
        applic.title = form.title.data
        applic.content = form.content.data
        applic.text = form.text.data
        applic.feedback = form.feedback.data
        current_user.applic.append(applic)
        db_sess.merge(current_user)
        db_sess.commit()
        mess_to_vk(form.title.data, form.content.data, form.text.data, form.feedback.data)
        
        return redirect('/applications')
    return render_template('add_applic.html', title='Создание заявки',
                           form=form)

@app.route('/change_applications/<int:id>', methods=['GET', 'POST'])
@login_required
def change_applic(id):
    form = ApplicationsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        applic = db_sess.query(Application).filter(Application.id == id,
                                          Application.user == current_user
                                          ).first()
        if applic:
            form.title.data = applic.title
            form.content.data = applic.content
            form.text.data = applic.text
            form.feedback.data = applic.feedback
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        applic = db_sess.query(Application).filter(Application.id == id,
                                          Application.user == current_user
                                          ).first()
        if applic:
            applic.title = form.title.data
            applic.content = form.content.data
            applic.text = form.text.data
            applic.feedback = form.feedback.data
            db_sess.commit()
            return redirect('/applications')
        else:
            abort(404)
    return render_template('add_applic.html',
                           title='Редактирование заявки',
                           form=form
                           )

@app.route('/delete_applications/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_applications(id):
    db_sess = db_session.create_session()
    applic = db_sess.query(Application).filter(Application.id == id,
                                      Application.user == current_user
                                      ).first()
    if applic:
        db_sess.delete(applic)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/applications')

@app.route("/photo")
def photo():
    db_sess = db_session.create_session()
    ph = db_sess.query(Photo)

    return render_template("photo.html", title="фотографии", photos=ph)

@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        db_sess.add(news)
        db_sess.commit()

        return redirect('/home')
    return render_template('news.html', title='Создание новости',
                           form=form)



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/home")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/home")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 404)


if __name__ == '__main__':
    main()
