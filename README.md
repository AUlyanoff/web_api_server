### Масштабируемый скелет web-приложения и api-сервера
> Имеет простенький, но полнофункциональный компонент авторизации<br>
> Отвечает на `[GET] /api/v1/users/count, /api/v1/users/list`

Собран на:
- Python 3.10 и Flask (приложение обёрнуто в продуктовый WSGI)
- авторизация flask-login
- доступ к PostgreSQL через SQLAlchemy
- фронтэнд Jinja2
- проверка конфигов pydantic 2
