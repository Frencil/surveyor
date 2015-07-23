# -*- coding: utf-8 -*-

# Imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators
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

# Login manager stuff

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

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

    questions = db.relationship('Question', backref='surveys')

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
    options = db.relationship('Option', backref='questions')

    def __init__(self, text, survey):
        self.text = text
        self.survey = survey

    def __repr__(self):
        return '<Question %r>' % self.id

    
class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    questions_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    
    question = db.relationship('Question', backref=db.backref('questions', lazy='dynamic'))

    def __init__(self, text, question):
        self.text = text
        self.question = question

    def __repr__(self):
        return '<Question %r>' % self.id

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    is_active = db.Column(db.Integer)
    is_admin = db.Column(db.Integer)
    date_registered = db.Column(db.DateTime)

    def __init__(self, email, password, name=None):
        self.email = email
        self.password = password # needs encryption
        self.name = name
        self.is_active = 1
        self.is_admin = 0
        self.date_registered = datetime.utcnow()

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return bool(self.is_active)
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.id


# DB Functions

def init_db():
    db.drop_all()
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


# Forms

class RegisterForm(Form):
    email = TextField('Email Address', [
        validators.Length(min=6, message=u'That\'s a little short for a valid email address.'),
        validators.Email(message=u'That\'s not a valid email address.')
    ])
    password = PasswordField('Password', [
        validators.Length(min=6, message=u'Good passwords are at least 6 characters. Preferably more.'),
    ])

class LoginForm(Form):
    email = TextField('Email Address')
    password = PasswordField('Password')  

        
# Routes

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register' , methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(request.form['email'], request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    print(form.errors)
    return render_template('register.html', form=form)


@app.route('/login',methods=['GET','POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        
        email = request.form['email']
        password = request.form['password']
        registered_user = User.query.filter_by(email=email,password=password).one()
        if registered_user is None:
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('login'))
        
        login_user(registered_user)
        flash(u'Successfully logged in', 'success')
        return redirect(request.args.get('next') or url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash(u'Successfully logged out', 'success')
    return redirect(url_for('index')) 


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
