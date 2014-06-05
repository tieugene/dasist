#!/bin/env python
# -*- coding: utf-8 -*-
# Description:
__author__ = 'ti.eugene@gmail.com'

import os, sys

#PROJECT_DIR = os.path.dirname(__file__)
#sys.path.append(PROJECT_DIR)

import flask
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from blueprints.contact.views import contact
app.register_blueprint(contact)

@app.errorhandler(404)
def not_found(error):
    return flask.render_template('404.html'), 404


@app.route('/')
def index():
    return flask.render_template('index.html')

# 1. standalone
if __name__ == '__main__':
	app.run()
