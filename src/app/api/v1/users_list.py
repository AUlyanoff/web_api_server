import logging
from flask import jsonify, request
from sqlalchemy import select

from app.api.v1.blueprint import blueprint_v1
from app.app_init import Session
from database.tables import users

logger = logging.getLogger(__name__)


@blueprint_v1.route("/users/list", methods=["GET"])
def users_list():
    """Возвращает список зарегистрированных юзеров"""
    api_path = request.environ['REQUEST_URI'][1:]  # путь вызова API
    logger.debug(f"{api_path} ({users_list.__doc__}) started...")

    query = select(users.c.name, users.c.email)
    with Session() as session:
        result = session.execute(query).mappings().all()

    list_dicts = list()
    for item in result:
        list_dicts.append(dict(item))  # преобразование mapping-объектов Алхимии в словари

    response, status = {"data": list_dicts}, 200
    _ll = f"{api_path}, HTTP={status} ended\n\tresponse={response}"
    logger.info(_ll) if status == 200 else logger.error(_ll)

    return jsonify(response), status
