#CLIENT_ID = '835646137382-fc7lldt05t73gmeh1ejotdudu246ic11.apps.googleusercontent.com'
#CLIENT SECRET = 'LOoW9rdbAbCMNdKyeDWQ616i'

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, User, Task

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "RestaurantMenuApp"

engine = create_engine('sqlite:///todo.db')
Base.metadata.bind = engine

# DBSession = sessionmaker(bind=engine)
# session = DBSession()

session = scoped_session(sessionmaker(bind=engine))

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user=session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user=session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user=session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/')
def showTasks():
    if 'username' not in login_session:
        flash("You are not signed in")
        return redirect('/login')
    
    tasks=session.query(Task).filter_by(user_id=login_session['user_id']).order_by(asc(Task.priority))
    return render_template('task.html', tasks=tasks, name=login_session['username'].partition(' ')[0])

@app.route('/addTask', methods = ['GET', 'POST'])
def addTask():

    if 'username' not in login_session:
        flash("You are not signed in")
        return redirect('/login')
    
    if request.method == 'POST':
        if len(request.form['name']) == 0:
            return redirect(url_for('addTask'))
        
        newTask =  Task(name=request.form['name'], priority = request.form['priority'],
                        user_id=login_session['user_id'])
        session.add(newTask)
        session.commit()
        return redirect(url_for('showTasks'))
    
    else:
        return render_template('addTask.html',user_id=login_session['user_id'])

@app.route('/delTask/<int:task_id>/<int:user_id>/delete', methods=['GET', 'POST'])
def delTask(task_id, user_id):
    taskToDel =  session.query(Task).filter_by(user_id=login_session['user_id']).filter_by(id=task_id).one()
    if request.method=='POST':
        session.delete(taskToDel)
        session.commit()
        return redirect(url_for('showTasks'))

    else:
        return render_template('delTask.html', task=taskToDel)

@app.route('/login')
def login():
    if 'username' in login_session:
        return redirect('/')
    
    state =''.join(random.choice(string.ascii_uppercase+string.digits) for x in range(32))
    login_session['state']=state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    print(code)
    print(request.args)
    print(request.json)
    token = request.form['idtoken']
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        userid = idinfo['sub']
        print(idinfo)
    except ValueError:
        pass

    login_session['username'] = idinfo['name']
    login_session['picture'] = idinfo['picture']
    login_session['email'] = idinfo['email']

    user_id=getUserID(login_session['email'])
    if not user_id:
        user_id=createUser(login_session)
    login_session['user_id']=user_id
    
    print('Going to redirect')
    return redirect(url_for('showTasks'))


@app.route('/logout')
def logout():
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)