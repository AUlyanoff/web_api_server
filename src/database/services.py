import logging
import psycopg2
import psycopg2.extras
import time
import re
import pandas as pd
from sqlalchemy import select
from flask import url_for

from database.tables import main_menu, posts, users


logger = logging.getLogger(__name__)


class FDataBase:
    def __init__(self, db):
        self.__db = db

    def getMenu(self):
        """Получить список словарей с пунктами меню (id, название, url)"""
        _query = select(main_menu)
        try:
            res = self.__db.execute(_query)
            if res:
                return res.all()

        except psycopg2.Error as e:
            logger.error(f"Ошибка чтения из БД: {str(e)}")
        return []

    def addPost(self, title, text, url):
        """Добавляем новую статью, url должен быть уникальным"""
        try:
            _query = select(posts.c.title, posts.c.text).where(posts.c.url == url).limit(1)
            _res = self.__db.execute(_query)
            if _res.rowcount > 0:
                logger.warning(f"Статья '{title}' с таким url={url} уже существует")
                return False

            base = url_for('static', filename='images_html')
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>", text)

            tm = pd.to_datetime(time.time(), unit='s')
            _query = posts.insert().values(title=title, text=text, url=url, time=tm)
            _res = self.__db.execute(_query)
            self.__db.commit()
        except psycopg2.Error as e:
            logger.error(f"Ошибка добавления статьи в БД: {str(e)}")
            return False

        return True

    def getPost(self, alias):
        """ Прочитать статью из БД.
            Возвращает titile Заголовок и text Текст статьи.
        """
        try:
            _query = select(posts.c.title, posts.c.text).where(posts.c.url == alias).limit(1)
            _res = self.__db.execute(_query)
            if _res.rowcount > 0:
                return _res.all()[0]

        except psycopg2.Error as e:
            logger.error(f"Ошибка получения статьи из БД {str(e)}")

        return (False, False)

    def getPostsAnonce(self):
        """Возвращает все статьи с их заголовками"""
        try:
            _query = select(posts)
            res = self.__db.execute(_query)
            if res: return res.all()
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения статьи из БД {str(e)}")

        return []

    def addUser(self, name, email, hpsw):
        """Добавляем пользователя. Электронная почта должна быть уникальной."""
        try:
            _query = select(users).where(users.c.email == email).limit(1)
            _res = self.__db.execute(_query)
            if _res.rowcount > 0:
                logger.info(f"Пользователь с таким email={email} уже существует")
                return False

            tm = pd.to_datetime(time.time(), unit='s')
            _query = users.insert().values(name=name, email=email, psw=hpsw, time=tm)
            _res = self.__db.execute(_query)
            self.__db.commit()
        except psycopg2.Error as e:
            logger.error(f"Ошибка добавления пользователя в БД {str(e)}")
            return False

        return True

    def getUser(self, user_id):
        """Получить юзера по его id, юзер - это словарь."""
        try:
            _query = select(users).where(users.c.id == user_id).limit(1)
            res = self.__db.execute(_query)
            if res.rowcount == 0:
                logger.error(f'Пользователь не найден user_id={user_id}')
                return False
            else:
                res = res.mappings().all()[0]
            return res
        except psycopg2.Error as e:
            logger.error(f'Ошибка получения данных из БД {str(e)}')
        return False

    def getUserByEmail(self, email):
        """Получить юзера по его email"""
        try:
            _query = select(users).where(users.c.email == email).limit(1)
            res = self.__db.execute(_query)
            if res.rowcount == 0:
                logger.error(f'Пользователь не найден email={email}')
                return False
            else:
                res = res.mappings().all()[0]
            return res
        except psycopg2.Error as e:
            logger.error(f'Ошибка получения данных из БД {str(e)}')

        return False

    def updateUserAvatar(self, avatar, user_id):
        """Обновить аватар пользователя"""
        if not avatar:
            return False
        try:
            _query = users.update().where(users.c.id == user_id).values(avatar=avatar)
            _res = self.__db.execute(_query)
            self.__db.commit()
        except psycopg2.Error as e:
            logger.error(f'Ошибка обновления аватара в БД: {str(e)}')
            return False
        return True
