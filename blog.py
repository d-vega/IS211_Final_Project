#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Flask application using sqlite3 database"""


# export FLASK_ENV=development


import sqlite3 as lite
import re
import os
from flask import (Flask, render_template, request, redirect,
                   url_for, current_app, g, flash, session)
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')


def get_db():
    if 'db' not in g:
        g.db = lite.connect('hw13.db')
        g.db.row_factory = lite.Row

    return g.db


@app.route('/',  methods=['GET'])
def home_pg():
    if 'logged_in' in session:
        return redirect('/dashboard')
    else:
        return render_template('cms/index.html')

if __name__ == '__main__':
    app.run()
