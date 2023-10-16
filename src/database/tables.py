from sqlalchemy import MetaData, Table, Column, Integer, String, Text, DateTime     # , LargeBinary
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects import postgresql

# СПОСОБ 1
# служебный объект метаданных для описания таблиц ---------------------------------------------------------------------
metadata = MetaData()

# Описание таблицы для Главного Меню
main_menu = Table('mainmenu', metadata,
                  Column('id', Integer(), primary_key=True),
                  Column('title', String(64), nullable=False),
                  Column('url', String(256), nullable=False)
                  )
# Описание таблицы для Статей
posts = Table('posts', metadata,
              Column('id', Integer(), primary_key=True),
              Column('title', String(256), nullable=False),
              Column('text', Text, nullable=False),
              Column('url', String(256), nullable=False),
              Column('time', DateTime, nullable=False)
              )

# описание таблицы для Пользователей
users = Table('users', metadata,
              Column('id', Integer(), primary_key=True),
              Column('name', String(128), nullable=False),
              Column('email', String(128), nullable=False),
              Column('psw', String(256), nullable=False),
              # Column('avatar', LargeBinary, nullable=True),
              Column('avatar', postgresql.BYTEA, nullable=True),
              Column('time', DateTime, nullable=False)
              )

# # СПОСОБ 2
# # объект для ВСЕХ таблиц базы для наследования классов таблиц -------------------------------------------------------
all_db_tables = declarative_base()
#
#
# # описание таблицы для Пользователей
# class Users(all_db_tables):
#     __tablename__ = 'users'
#     __table_args__ = {'extend_existing': True}  # продолжать, если таблица существует
#     id = Column(Integer(), primary_key=True)
#     name = Column(String(128), nullable=False)
#     email = Column(String(128), nullable=False)
#     psw = Column(String(256), nullable=False)
#     avatar = Column(LargeBinary(), nullable=True)
#     time = Column(DateTime, nullable=False)
#
