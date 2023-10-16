import os
import yaml
import logging
from pydantic import ValidationError
from app.config.check_config import DatabaseConfig, AppConfig


logger = logging.getLogger(__name__)


class Config:
    """ Прочитать конфиги в словари, а потом выдавать параметры из словарей
        db.yml      - параметры соединения с базой
        smapi.yml   - параметры приложения
        Если существуют конфиги разработчика smapi_dev.yml, db_dev.yml,
        то используются они, а продуктовые конфиги app.yml и db.yml игнорируются.
    """
    def __init__(self):
        """Перекладываем настройки в словари"""
        self.db = self.fs_load_db()             # это настройки базы данных из файловой системы db[_dev].yml
        self.app = self.fs_load_app()           # это настройки приложения из файловой системы app[_dev].yml
        self.app.update(self.db_load_app())     # доливаем настройки из базы (или откуда угодно)
        self.check_settings()                   # проверяем всё Пидантиком

    # ----------------------------------- функции выдачи параметров приложения ----------------------------------------
    def get_loglevel(self):
        """Получение уровня логирования"""
        return self.app.get('loglevel', 'DEBUG')

    def get_flask_debug(self):
        """В каком режиме запустить flask-приложение"""
        return self.app.get('flask_debug', False)

    def get_threads(self):
        """Получение количества разрешённых потоков"""
        return self.app.get('server', {}).get('threads', 8)

    def get_app_host(self):
        """Получение адреса хоста приложения"""
        return self.app.get('server', {}).get('host', '0.0.0.0')

    def get_app_port(self):
        """Получение номера порта, который слушает приложение"""
        return self.app.get('server', {}).get('port', 5050)

    # ----------------------------------- функции выдачи параметров базы ----------------------------------------------
    def get_db_host(self):
        """Получение хоста БД"""
        return self.db.get('host', '127.0.0.1')

    def get_db_port(self):
        """Получение порта БД"""
        return self.db.get('port', 5432)

    def get_db_name(self):
        """Получение имени БД"""
        return self.db.get('name', 'demo')

    def get_db_schema(self):
        """Получение схемы БД"""
        return self.db.get('db_schema', 'public')

    def get_db_user(self):
        """Получение имени пользователя БД"""
        return self.db.get('user', 'AUlyanoff')

    def get_db_pass(self):
        """Получение пароля БД"""
        return self.db.get('password', 'qRjCuQhx87Nb')

    # ----------------------------------- внутренние сервисные функции класса -----------------------------------------
    def fs_load_db(self):
        """ Читаем из файла настройки базы
            Если есть конфиг разработчика, продуктовый конфиг игнорируется
        """
        db_yaml_path = os.path.join(os.environ.get('SRC_PATH'), 'config', 'db_dev.yml')
        if not os.path.isfile(db_yaml_path):
            db_yaml_path = os.path.join(os.environ.get('SRC_PATH'), 'config', 'db.yml')
            if not os.path.isfile(db_yaml_path):
                raise FileNotFoundError(f'DB config not found: {db_yaml_path}')
        logger.fatal(db_yaml_path.split("\\")[-1] + ' found and will be used for database connect')

        with open(db_yaml_path) as f:  # создаём конфиг-словарь базы
            db_dict = yaml.safe_load(f).get('db')
            if db_dict is None: raise ValueError(f'DB dictionary not found: {db_yaml_path}')

        return db_dict

    def fs_load_app(self):
        """ Читаем из файла настройки приложения
            Если есть конфиг разработчика, продуктовый конфиг игнорируется
        """
        app_yaml_path = os.path.join(os.environ.get('SRC_PATH'), 'config', 'app_dev.yml')
        if not os.path.isfile(app_yaml_path):
            app_yaml_path = os.path.join(os.environ.get('SRC_PATH'), 'config', 'app.yml')
            if not os.path.isfile(app_yaml_path):
                raise FileNotFoundError(f'APP config not found: {app_yaml_path}')
        logger.fatal(app_yaml_path.split("\\")[-1] + ' found and will be used for web-application')

        with open(app_yaml_path) as f:  # создаём конфиг-словарь приложения
            app_dict = yaml.safe_load(f).get('app')
            if app_dict is None: raise ValueError(f'APP dictionary not found: {app_yaml_path}')

        return app_dict

    def db_load_app(self):
        """ Чтение из базы или откуда угодно дополнительных настроек базы и приложения (заглушка) """
        settings = dict()
        # settings.update({'foo': 'foo', 'boo': 'boo'})
        return settings

    def check_settings(self):
        """Проверка конфигов Пидантиком-бантиком"""
        try:
            _db_cfg = DatabaseConfig(**self.db)
        except ValidationError as e:
            logger.fatal(f'DB config checked... failed\n{e}')
            exit(-2)
        else:
            logger.fatal(f'DB config checked... ok')

        try:
            _app_cfg = AppConfig(**self.app)
        except ValidationError as e:
            logger.fatal(f'App config checked... failed\n{e}')
            exit(-4)
        else:
            logger.fatal(f'App config checked... ok')
