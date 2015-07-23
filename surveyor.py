# -*- coding: utf-8 -*-

# Imports
import sqlite3
from functools import wraps
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuration
DATABASE = '/tmp/surveyor.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/surveyor.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# Initialize the application
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

# Models
class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    is_open = db.Column(db.Integer)
    date_created = db.Column(db.DateTime)
    date_opened = db.Column(db.DateTime)
    date_closed = db.Column(db.DateTime)

    def __init__(self, title, text, is_open=None):
        self.title = title
        self.text = text
        self.date_created = datetime.utcnow()
        if is_open is True:
            self.is_open = 1
            self.date_opened = datetime.utcnow()
        else:
            self.is_open = 0

    def __repr__(self):
        return '<Survey %r>' % self.id


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    surveys_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))
    survey = db.relationship('Survey', backref=db.backref('surveys', lazy='dynamic'))

    def __init__(self, text, survey):
        self.text = text
        self.survey = survey

    def __repr__(self):
        return '<Question %r>' % self.id


# DB Functions

def init_db():
    db.create_all()
    '''
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    '''

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
def index():
    return render_template('index.html')

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
            return redirect(url_for('list_surveys'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'You were logged out', 'success')
    return redirect(url_for('list_surveys'))

@app.route('/surveys')
def list_surveys():
    cur = g.db.execute('select title, text from surveys order by id desc')
    surveys = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('list_surveys.html', surveys=surveys)

@app.route('/surveys/<int:id>')
def view_survey(id):
    query = g.db.execute('select * from surveys where id = ?', [id])
    row = query.fetchone()
    if (row == None):
        abort(404)
    else:
        survey = dict(id=row[0], title=row[1], text=row[2], is_open=row[3],
                      date_created=row[4], date_opened=row[5], date_closed= row[6])
        return render_template('view_survey.html', survey=survey)

@app.route('/surveys/edit/<int:id>')
def edit_survey(id):
    query = g.db.execute('select * from surveys where id = ?', [id])
    row = query.fetchone()
    if (row == None):
        abort(404)
    else:
        survey = dict(id=row[0], title=row[1], text=row[2], is_open=row[3],
                      date_created=row[4], date_opened=row[5], date_closed= row[6])
        return render_template('edit_survey.html', survey=survey)

        
@app.route('/surveys/add', methods=['POST'])
def add_survey():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into surveys (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash(u'New survey was successfully posted', 'success')
    return redirect(url_for('show_surveys'))

# Run

if __name__ == '__main__':
    app.run()
