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


def get_all_posts():
    authors = []
    post_details = []
    finaldata = {}
    database = get_db()
    counter = 0

    for author in database.execute('SELECT author_id FROM blog_posts'):
        for val in author:
            finaldata[val] = []

        for row in database.execute('SELECT blog_posts.post_id, blog_posts.title,'
                                    ' blog_posts.post_content, blog_posts.date, '
                                    'authors.firstname, authors.lastname,'
                                    ' authors.author_id FROM '
                                    'blog_posts JOIN authors using (author_id) '
                                    'WHERE author_id=?', author):
            post_details.append(row)

            if post_details[counter][6] in finaldata:
                finaldata[post_details[counter][6]].append(row)

            counter += 1

    return finaldata


def get_user_posts(user_id):
    author = user_id
    post_details = []
    finaldata = {}
    finaldata[author] = []
    database = get_db()
    counter = 0

    for row in database.execute('SELECT blog_posts.post_id, blog_posts.title,'
                                ' blog_posts.post_content, blog_posts.date, '
                                'authors.firstname, authors.lastname,'
                                ' authors.author_id FROM '
                                'blog_posts JOIN authors using (author_id) '
                                'WHERE author_id=?', (author,)):
        post_details.append(row)

        if post_details[counter][6] in finaldata:
            finaldata[post_details[counter][6]].append(row)
        counter += 1
    return finaldata



@app.route('/',  methods=['GET'])
def home_pg():
    if 'logged_in' in session:
        return redirect('/dashboard')
    else:
        data = get_all_posts()
    return render_template('cms/index.html', data=data)


@app.route('/dashboard',  methods=['GET'])
def dashboard():
    if 'logged_in' in session:
        user_id = session['user_id']
        data = get_user_posts(user_id)
        return render_template('/cms/dashboard.html', data=data)
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

@app.route('/edit/<path:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    postid = post_id
    database = get_db()
    title = []
    content = []
    titles = database.execute('SELECT title FROM blog_posts WHERE'
                             ' post_id=?', (postid,)).fetchone()
    contents = database.execute('SELECT post_content FROM blog_posts '
                               'WHERE post_id=?', (postid,)).fetchone()

    title.append(titles)
    content.append(contents)

    if 'logged_in' in session:
        if request.method == 'POST':
            fin_title = request.form['title']
            fin_contents = request.form['content']

            database.execute('UPDATE blog_posts SET title=? , post_content=?'
                             ' WHERE post_id=?', (fin_title, fin_contents, postid))
            database.commit()
            return redirect('/dashboard')
        else:
            return render_template('/cms/edit.html', title=title,
                                   content=content)
    else:
        return redirect('/')


@app.route('/delete', methods=['POST'])
def delete_post():
    database = get_db()
    post_id = request.form['post_to_delete']
    if 'logged_in' in session:
        database.execute('DELETE FROM blog_posts WHERE post_id=?', post_id)
        database.commit()
        return redirect('/dashboard')
    else:
        return redirect('/')


@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            date = request.form['date']
            database = get_db()
            id = session['user_id']

            database.execute('INSERT INTO blog_posts(title, post_content, date,'
                             ' author_id) VALUES(?, ?, ?, ?)', (title, content,
                                                                date, id))
            database.commit()

            return redirect('/dashboard')

        elif request.method == 'GET':
            return render_template('/cms/create.html')
    else:
        return redirect('/login')


if __name__ == '__main__':
    app.run()
