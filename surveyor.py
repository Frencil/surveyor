# -*- coding: utf-8 -*-

# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/surveyor.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# initialize the application
app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    
        
# Routes

@app.route('/')
def list_surveys():
    cur = g.db.execute('select title, text from surveys order by id desc')
    surveys = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('list_surveys.html', surveys=surveys)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash(u'You were logged in', 'success')
            return redirect(url_for('show_surveys'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'You were logged out', 'success')
    return redirect(url_for('show_surveys'))

@app.route('/survey/<int:id>')
def view_survey(id):
    query = g.db.execute('select * from surveys where id = ?', [id])
    row = query.fetchone()
    if (row == None):
        abort(404)
    else:
        survey = dict(id=row[0], title=row[1], text=row[2])
        print(survey)
        return render_template('view_survey.html', survey=survey)
        
@app.route('/survey/add', methods=['POST'])
def add_survey():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into surveys (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash(u'New survey was successfully posted', 'success')
    return redirect(url_for('show_surveys'))

if __name__ == '__main__':
    app.run()
