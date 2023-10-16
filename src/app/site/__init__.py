#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Устаревшее поведение Flask-а
    в Питоне __init__.py уже не нужны, а во Flask-е ещё нужны
"""
from app.site.routes import index
from app.site.routes import addPost
from app.site.routes import showPost
from app.site.routes import login
from app.site.routes import logout
from app.site.routes import register
from app.site.routes import profile
from app.site.routes import userava
from app.site.routes import upload
