import sys
import logging
from datetime import datetime
import os

from flask import Flask, g
from sys import version as python_ver

from flask_login import LoginManager
from sqlalchemy.orm import sessionmaker

from app.config.simpl_config import Config
from database.services import FDataBase
from app.site.user_login import UserLogin
import database.init

# --------------------------------------------- настройка логирования -------------------------------------------------
logger = logging.getLogger(__name__)
logger.fatal(f"EDUCATION-server started at {datetime.now().strftime('%d-%m-%Y %H:%M:%S, %A')}...")
log_format = f"%(levelname).1s:(%(threadName)-10s): %(filename)s: %(funcName)s: %(lineno)s: %(message)s "

config = Config()   # чтение конфигов ---------------------------------------------------------------------------------

log_level_chr = config.get_loglevel()
log_level_int = logging.getLevelName(log_level_chr)
logging.basicConfig(level=log_level_int, format=log_format, handlers=[logging.StreamHandler(sys.stderr)])

# -------------------------------- запуск Flask-а, компоненты web-сайта прячем поглубже -------------------------------
app = Flask(__name__,
            template_folder=os.path.join(os.environ.get('APP_PATH'), 'site', 'templates'),
            static_folder=os.path.join(os.environ.get('APP_PATH'), 'site', 'static'),
            static_url_path='/static',
            )
app.config.from_object(__name__)
app.secret_key = 'super secret key'
app.config['DEBUG'] = config.get_flask_debug()
logger.info('Flask started')


# --------------------------------------------- логирование итогов загрузки -------------------------------------------
summary = dict(
    python=str(python_ver),
    loglevel=f"{log_level_chr} ({log_level_int})",
    base_path=os.path.join(os.environ.get('SRC_PATH')),
    flask_path=app.root_path,
    templates=app.template_folder,
    static=f"{app.static_folder}, url_path={app.static_url_path}",
    registered_routes=len([rout for rout in app.url_map.iter_rules()]),
    flask_debug=app.debug,
)
_ll = 'main parameters:' + ''.join([f'\n\t{k:<25} \t= {v}' for k, v in summary.items()])
logger.fatal(f'{_ll}')

# --------------------------------------------- инициализация базы данных ---------------------------------------------
engine, all_db_tables, db_conf = database.init.db_connection(config)      # связываемся с базой
Session = sessionmaker(bind=engine)  # запоминаем параметры сессии (фабрика сессий session = Session(); session.close())

if len(all_db_tables.metadata.sorted_tables) < 3:       # а не мало ли таблиц, может надо сделать demo-наполнение БД?
    conn = engine.connect()                             # присоединяемся к базе через коннект
    database.init.upload_demo(engine, all_db_tables, conn)
    conn.close()

# --------------------------------------------- регистрация blueprint-ов ----------------------------------------------
from app.site.blueprint import blueprint_pages
from app.api.v1.blueprint import blueprint_v1
app.register_blueprint(blueprint_pages)
app.register_blueprint(blueprint_v1, url_prefix='/api/v1')

# --------------------------------------------- инициализация менеджера регистрации -----------------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'pages.login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


# --------------------------------------------------------------------------------------------------------------
# ОБРАБОТЧИКИ НАЧАЛА И ОКОНЧАНИЯ ЗАПРОСОВ
# --------------------------------------------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    logger.debug(f"Loading user id={user_id}")
    return UserLogin().fromDB(user_id, g.dbase)


def connect_db():
    """Создаем соединение с базой"""
    conn = engine.connect()
    logger.debug(f"DB connection created, valid is {conn.connection.is_valid}")
    return conn


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    db = get_db()
    g.dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


if __name__ == "__main__":
    pass
