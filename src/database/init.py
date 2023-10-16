import os
import logging
import datetime

from sqlalchemy import create_engine, URL, delete, insert

from database.tables import metadata, main_menu, posts, users, all_db_tables

logger = logging.getLogger(__name__)


def db_connection(config):
    """ Инициализация базы и отзеркаливание (автоматическое построение описаний) уже имеющихся таблиц.
        :return: объект БД, объект всех таблиц, конфиг БД
    """
    logger.info(f'Database initialization started')

    db_conf = URL.create('postgresql',
                         database=config.get_db_name(),
                         username=config.get_db_user(),
                         password=config.get_db_pass(),
                         host=config.get_db_host()
                         )
    engine = create_engine(db_conf)  # объект базы
    all_db_tables.metadata.reflect(engine)  # наполняем его из базы именами всех таблиц и колонок с их свойствами

    # красивое логирование параметров базы
    db_conf_dict = db_conf._asdict()
    db_conf_dict.pop('query')
    db_conf_dict['password'] = len(db_conf_dict['password']) * '*'
    db_conf_dict['driver'] = engine.driver
    db_conf_dict['dialect'] = engine.dialect.name
    db_conf_dict['total tables found'] = len(all_db_tables.metadata.sorted_tables)
    _ll = ''.join([f'\n\t{k:<25} \t= {v}' for k, v in db_conf_dict.items()])
    logger.fatal(f'Database initialized successfully: {_ll}')

    return engine, all_db_tables, db_conf


def upload_demo(engine, all_db_tables, conn, force=False):
    """
    Заполнение таблиц демо-данными
        если force=True, то все таблицы БД предварительно уничтожаются
        если force=False, то минимально необходимые таблицы БД предварительно очищаются от всех записей
        :return: объект БД, объект всех таблиц, конфиг БД
    """
    logger.info(f'Upload demo data started, force={force}')

    if force: all_db_tables.metadata.drop_all(engine)  # удалить все таблицы из БД

    # Заполняем таблицы БД (двумя способами в учебных целях) ----------------------------------------------------------
    # Способ 1 current alchemy release через коннект и выполнение sql-запроса
    metadata.create_all(engine)  # создаём все таблицы в базе (в данном случае - все импортированные)

    query = delete(main_menu)      # формируем sql-запрос на удаление всех строк в таблице
    _cursor = conn.execute(query)  # выполнение запроса

    query = main_menu.insert().values(title='Главная', url='/')  # sql-запрос на добавление одной строки
    _cursor = conn.execute(query)

    _cursor = conn.execute(  # sql-запрос на групповое добавление строк
        insert(main_menu),
        [
            {'title': 'Добавить статью', 'url': '/add_post'},
            {'title': 'Авторизация', 'url': '/login'},
            {'title': 'Донаты', 'url': '/donate'},
        ]
    )
    conn.commit()  # запись в базу

    query = delete(posts)
    _cursor = conn.execute(query)
    _cursor = conn.execute(
        insert(posts),
        [
            {'title': 'Про Flask', 'url': 'framework-flask-intro', 'time': datetime.datetime.now(),
             'text': '<p>Flask — это легковесный веб-фреймворк для языка Python, который предоставляет минимальный '
                     'набор инструментов для создания веб-приложений. <br>На нём можно сделать и лендинг, и '
                     'многостраничный сайт с кучей плагинов и сервисов. <br>Не фреймворк, а мечта!'},
            {'title': 'Про SQLAlchemy', 'url': 'framework-sqlalchemy-intro', 'time': datetime.datetime.now(),
             'text': 'Сила SQLAlchemy — в её ORM. Расшифровывается как object relational mapper, или '
                     '«объектно-реляционное отображение». <br>ORM позволяет управлять базами данных с помощью '
                     'методов объектов в коде и при этом не использовать SQL-запросы. <br>На самом деле это очень удобно, '
                     'так как позволяет писать привычный код, не переключаясь на SQL.'},
            {'title': 'Про Python', 'url': 'python-intro', 'time': datetime.datetime.now(),
             'text': 'Python — это скриптовый язык программирования.     <br>Он универсален, поэтому подходит для '
                     'решения разнообразных задач и для многих платформ: начиная с iOS и Android и заканчивая '
                     'серверными операционными системами. <br>Это интерпретируемый язык, а не компилируемый, '
                     'как C++ или Java. Программа на Python представляет собой обычный текстовый файл.'},
            {'title': 'Про API', 'url': 'about_api', 'time': datetime.datetime.now(),
             'text': 'К этому сайту можно обращаться через api:<br>'
                     '/api/v1/users/count<br>'
                     '/api/v1/users/list<br>'
                     'Это неплохой пример, т.к. любое api в конце концов сводится к вычислениями над базой.'},
        ]
    )
    conn.commit()

    query = delete(users)
    _cursor = conn.execute(query)

    _cursor = conn.execute(
        insert(users),
        [
            {'name': 'Lee Ji-Eun', 'email': 'iu@ya.ru', 'time': datetime.datetime.now(),
             'psw': 'pbkdf2:sha256:600000$E6zeNcWAdMGRxtAs$7dde9af9ea97e3b978e5e40a89d0e40536f7e199079f29b9be85986a1608aaa8'},
            {'name': 'Uam12345', 'email': 'u@ya.ru', 'time': datetime.datetime.now(),
             'psw': 'pbkdf2:sha256:600000$E6zeNcWAdMGRxtAs$7dde9af9ea97e3b978e5e40a89d0e40536f7e199079f29b9be85986a1608aaa8'},
            {'name': 'Sil12345', 'email': 's@ya.ru', 'time': datetime.datetime.now(),
             'psw': 'pbkdf2:sha256:600000$E6zeNcWAdMGRxtAs$7dde9af9ea97e3b978e5e40a89d0e40536f7e199079f29b9be85986a1608aaa8'}
        ]
    )
    # дописываем (UPDATE) аватарку Сила - Знайку
    with open(os.path.join(os.environ.get('APP_PATH'), 'site', 'static', 'images', 'znaika.jpg'), "rb") as f:
        avatar = f.read()
        query = users.update().where(users.c.name == 'Sil12345').values(avatar=avatar)
        conn.execute(query)
    conn.commit()

    # дописываем мою аватарку
    with open(os.path.join(os.environ.get('APP_PATH'), 'site', 'static', 'images', 'admin.jpg'), "rb") as f:
        avatar = f.read()
        query = users.update().where(users.c.name == 'Uam12345').values(avatar=avatar)
        conn.execute(query)
    conn.commit()

    # и аватарку дорогой IU
    with open(os.path.join(os.environ.get('APP_PATH'), 'site', 'static', 'images', 'iu.jpg'), "rb") as f:
        avatar = f.read()
        query = users.update().where(users.c.name == 'Lee Ji-Eun').values(avatar=avatar)
        conn.execute(query)
    conn.commit()

    # Способ 2 через сессию ------------------------------------------------------------------------------------
    # all_db_tables.metadata.create_all(engine)           # по описанию создать пустые таблицы
    #
    # session.query(Users).delete()                       # удаление всех строк в таблице
    # u_1 = Users(name='Алекс', email='a1@m.ru', time=datetime.datetime.now(), psw='pbkdf2:sha256:150000$JwCjtXET$cad8e0fe3499657da18cfe0fcd2174e92ad2ff928165dbd0e7e604e78505b8e4')
    # u_2 = Users(name='Сергей', email='s@m.ru', time=datetime.datetime.now(), psw='pbkdf2:sha256:150000$3MoisAAc$0021ec7144d2099d946bfff75e8e563bb9db0f41f560a8c495d9f244103924ee')
    # u_3 = Users(name='Sil12345', email='s@ya.ru', time=datetime.datetime.now(), psw='pbkdf2:sha256:600000$E6zeNcWAdMGRxtAs$7dde9af9ea97e3b978e5e40a89d0e40536f7e199079f29b9be85986a1608aaa8')
    # session.add_all([u_1, u_2, u_3])                    # добавляем три строки
    # session.commit()                                    # записываем в базу

    all_db_tables.metadata.reflect(engine)      # для логирования - перечитываем, сколько сейчас есть таблиц
    logger.info(f'Upload demo data ended, {len(all_db_tables.metadata.sorted_tables)} tables (re)created')

    return None
