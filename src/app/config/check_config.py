#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field, PositiveInt, IPvAnyAddress, ConfigDict, FilePath, StrictStr, AnyUrl, SecretStr
from typing import Literal, ClassVar, Any, Union
from typing_extensions import Annotated


class DatabaseConfig(BaseModel):
    """ Дата-класс для проверки значений параметров конфига базы """
    # разрешим приведение типов numbers -> str и запретим неописанные параметры
    model_config = ConfigDict(coerce_numbers_to_str=True, extra='forbid')

    # обязательные параметры
    db_schema: StrictStr                                    # строгая строка - запретим приведение типов numeric -> str
    user: StrictStr
    password: Union[SecretStr, int]
    host: Union[IPvAnyAddress, AnyUrl, StrictStr]           # IP-адрес v4/v6, или любой url, или нецифровая строка
    port: PositiveInt                                       # натуральное число
    name: StrictStr

    # необязательные параметры, могут отсутствовать
    type: Literal['postgresql', 'PostgreSQL', 'Mock', 'mock'] = 'postgresql'  # перечень возможных значений
    minconn: Annotated[int, Field(ge=1, le=1999)] = 5       # натуральное число с ограничением сверху
    maxconn: Annotated[int, Field(ge=2, le=2000)] = 40
    sslmode: Literal['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full'] = 'disable'
    sslrootcert: FilePath = ''                              # путь существует и является файлом
    sslcert: FilePath = ''
    sslkey: FilePath = ''


class Server(BaseModel):
    """ Описание параметра server в smapi[_dev].yml """
    # все параметры необязательные
    host: IPvAnyAddress = None
    port: PositiveInt = None
    numthreads: Annotated[int, Field(ge=1, le=1024)] = 20


class AppConfig(BaseModel):
    """ Для проверки параметров приложения """
    model_config = ConfigDict(extra='forbid')   # неописанные параметры запрещены
    LogTypes: ClassVar = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL']

    # все параметры необязательные
    loglevel: LogTypes = 'DEBUG'
    timing: LogTypes = 'CRITICAL'
    flask_debug: bool = False
    log_format: StrictStr = ''                  # строгое StrictStr вместо str - чтобы избежать приведения типов
    reload_settings_period: Annotated[int, Field(ge=0, le=3600)] = None
    server: Server = None                       # параметр конфига server - это словарь
