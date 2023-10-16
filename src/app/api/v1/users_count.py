import logging
from flask import jsonify, request

from app.api.v1.blueprint import blueprint_v1
from app.app_init import Session
from database.tables import users

logger = logging.getLogger(__name__)


@blueprint_v1.route("/users/count", methods=["GET"])
def users_count():
    """Посчитать количество юзеров в базе"""
    api_path = request.environ['REQUEST_URI'][1:]  # путь вызова API
    logger.debug(f"{api_path} ({users_count.__doc__}) started...")

    with Session() as session:
        # rows = session.query(users).all()
        rows = session.query(users).count()

    response, status = {"data": rows}, 200

    _ll = f"{api_path}, response={response}, HTTP={status} ended"
    logger.info(_ll) if status == 200 else logger.error(_ll)

    return jsonify(response), status
