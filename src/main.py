"""
    Файл запуска приложения.
"""
import os
os.environ.setdefault('SRC_PATH', os.path.join(os.getcwd()))            # путь к корню - в переменные окружения
os.environ.setdefault('APP_PATH', os.path.join(os.getcwd(), 'app'))     # путь к приложению

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher       # это продуктовый сервер WSGI
from app.app_init import app as flask_app, config                       # это приложение Flask и объект с конфигами


dispatcher = PathInfoDispatcher({'/': flask_app})       #
host = config.get_app_host()                            # сервер WSGI запустит Flask
port = config.get_app_port()                            # в продуктовом многопоточном режиме
num_threads = config.get_threads()                      #


def main():
    """Создание продуктового сервера - обёртки вокруг flask-приложения"""
    wsgis_server = WSGIServer((host, port), dispatcher, numthreads=num_threads, max=-1,
                        request_queue_size=1024, timeout=4, shutdown_timeout=4,
                        accepted_queue_size=-1, accepted_queue_timeout=4,
                        peercreds_enabled=False, peercreds_resolve_enabled=False)
    return wsgis_server


if __name__ == "__main__":
    site_server = main()        # создание экземпляра сервера
    site_server.safe_start()    # запуск экземпляра
