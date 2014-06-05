#!/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'sdv'

from dasist import db
import config, os

if os.path.exists(config.DB_FILE):
    db.drop_all()
db.create_all()
