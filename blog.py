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
        g.db = lite.connect('flaskpress.db')
        g.db.row_factory = lite.Row
    return g.db


def get_posts():
    authors = []
    post_details = []
    database = get_db()

    for author in database.execute('SELECT author_id FROM blog_posts'):
        if author not in authors:
            authors.append(author)

    for row in database.execute('SELECT post_id, title, post_content, '
                                'date FROM blog_posts'):
        post_details.append(list(row))

    finaldata = dict(zip(authors, post_details))
    return finaldata



@app.route('/',  methods=['GET'])
def home_pg():
    #if 'logged_in' in session:
    #    return redirect('/dashboard')
    #else:
    data = get_posts()
    return render_template('cms/index.html', data=data)


@app.route('/dashboard',  methods=['GET'])
def dashboard():
    if 'logged_in' in session:
        return render_template('/cms/dashboard.html')
    else:
        return render_template('/auth/login.html')


@app.route('/register',  methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect('/dashboard')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        message = None
        database = get_db()

        if not email:
            message = 'Email is required.'
        elif not password:
            message = 'Password is required.'
        elif database.execute('SELECT author_id FROM authors WHERE email = ?',(
                               email,)).fetchone() is not None:
            message = 'User email {} is already registered.'.format(email)

        if message is None:
            message = "Registration successful!"
            database.execute(
                'INSERT INTO authors (firstname, lastname, email, password)'
                ' VALUES (?, ?, ?, ?)',
                (firstname, lastname, email, generate_password_hash(password)))
            database.commit()
            flash(message)
            return redirect('/login')

        flash(message)
        return redirect('/register')

    elif request.method == 'GET':
        return render_template('auth/register.html')


@app.route('/login',  methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect('/dashboard')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        database = get_db()
        user = database.execute(
            'SELECT * FROM authors WHERE email = ?',
            (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect/Invalid email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['logged_in'] = True
            session['user_id'] = user['author_id']
            return redirect('/dashboard')

        flash(error)
        return render_template('/auth/login.html')

    if request.method == 'GET':
        return render_template('/auth/login.html')


if __name__ == '__main__':
    app.run()
