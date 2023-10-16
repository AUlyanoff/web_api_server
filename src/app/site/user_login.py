import logging
from flask_login import UserMixin
import os

logger = logging.getLogger(__name__)


class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else "Без имени"

    def getEmail(self):
        return self.__user['email'] if self.__user else "Без email"

    def getAvatar(self):
        """Чтение аватара из файла"""
        logger.debug(f"Чтение аватара из файла...")
        img = None

        if isinstance(self.__user, bool) or not self.__user['avatar']:
            try:
                with open(os.path.join(os.environ.get('APP_PATH'), 'site', 'static', 'images', 'default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                logger.error(f"Не найден аватар по умолчанию: {str(e)}")
        else:
            img = self.__user['avatar']

        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or ext == "PNG" or ext == "jpg" or ext == "JPG" or ext == "jpeg" or ext == "JPEG":
            return True
        return False