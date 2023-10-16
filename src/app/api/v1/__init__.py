#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Устаревшее поведение Flask-а
    в Питоне __init__.py уже не нужны, а во Flask-е ещё нужны
"""
from app.api.v1.users_count import users_count
from app.api.v1.users_list import users_list
