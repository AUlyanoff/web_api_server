import logging
from flask import render_template, g, request, flash, abort, redirect, url_for, make_response

from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.site.blueprint import blueprint_pages
from app.site.forms import LoginForm, RegisterForm
from app.site.user_login import UserLogin

logger = logging.getLogger(__name__)


@blueprint_pages.route('/')
def index():
    """Роут Главной страницы"""
    logger.debug(f'{index.__doc__} started...')
    return render_template('index.html', menu=g.dbase.getMenu(), posts=g.dbase.getPostsAnonce())


@blueprint_pages.route("/add_post", methods=["POST", "GET"])
@login_required
def addPost():
    """Добавление статьи"""
    logger.debug(f'{addPost.__doc__} started...')
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = g.dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=g.dbase.getMenu(), title="Добавление статьи")


@blueprint_pages.route('/post/<alias>')
@login_required
def showPost(alias):
    """Показать статью"""
    logger.debug(f'{showPost.__doc__} started...')
    title, post = g.dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=g.dbase.getMenu(), title=title, post=post)


@blueprint_pages.route("/login", methods=["POST", "GET"])
def login():
    """Авторизация"""
    logger.debug(f'{login.__doc__} started...')
    if current_user.is_authenticated:
        return redirect(url_for('pages.profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = g.dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("pages.profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=g.dbase.getMenu(), title="Авторизация", form=form)


@blueprint_pages.route('/logout')
@login_required
def logout():
    """Выход из профиля"""
    logger.debug(f'{logout.__doc__} started...')
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('pages.login'))


@blueprint_pages.route("/register", methods=["POST", "GET"])
def register():
    """Страница регистрации"""
    logger.debug(f'{register.__doc__} started...')
    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(request.form['psw'])
            res = g.dbase.addUser(form.name.data, form.email.data, hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('pages.login'))
            else:
                flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", menu=g.dbase.getMenu(), title="Регистрация", form=form)


@blueprint_pages.route('/profile')
@login_required
def profile():
    """Страница профиля"""
    logger.debug(f'{profile.__doc__} started...')
    return render_template("profile.html", menu=g.dbase.getMenu(), title="Профиль")


@blueprint_pages.route('/userava')
@login_required
def userava():
    """Загрузка аватара"""
    logger.debug(f'{userava.__doc__} started...')
    img = current_user.getAvatar()
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@blueprint_pages.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    """Обновление аватара"""
    logger.debug(f'{upload.__doc__} started...')
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = g.dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('pages.profile'))

@blueprint_pages.route('/donate')
def donate():
    """Собрать денюжку"""
    logger.debug(f'{donate.__doc__} started...')
    return render_template("donate.html", menu=g.dbase.getMenu(), title="Пода-а-айте бедномуслепомукотуБазилио.")
