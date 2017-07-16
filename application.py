import httplib2
import random
import string
import json
import requests
import os
from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

from db_setup import Base, User, Category, Item, engine

client_secrets = {}

app = Flask(__name__)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#show latest Items
@app.route('/')
@app.route('/index')
@app.route('/index.json', endpoint="index-json")
def home():
    logged_in = is_logged_in()

    items = session.query(Item).order_by(Item.id.desc()).all()

    if request.path.endswith('.json'):
        return jsonify(json_list=[i.serialize for i in items])

    categories = session.query(Category).all()

    return render_template('index.html',
                           categories=categories,
                           items=items,
                           logged_in=logged_in,
                           section_title="Latest Items",
                           )

#show Items
@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>.json',
           endpoint="category-json")
def categoryItems(category_name):
    items = session.query(Item).filter_by(category_name=category_name).all()

    if request.path.endswith('.json'):
        return jsonify(json_list=[i.serialize for i in items])

    categories = session.query(Category).all()

    logged_in = is_logged_in()
    return render_template('index.html',
                           categories=categories,
                           current_category=category_name,
                           items=items,
                           logged_in=logged_in,
                           section_title="%s Items (%d items)" % (
                               category_name, len(items)),
                           )

#  ------------------------------  login and ot ------------------------------
#Poge for Login
@app.route('/login')
def showLogin():
    access_token = login_session.get('access_token')

    if access_token is None:
        state = get_token()
        login_session['state'] = state

        return render_template('login.html', STATE=state,
                               CLIENT_ID=client_secrets['client_id'])
    else:
        return render_template('logged_in.html')

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:

        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/vagrant/catalog/client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID didn't match the given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != client_secrets['client_id']:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = AccessTokenCredentials(
        login_session.get('access_token'), 'user-agent-value')

    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return 'logged in'


#Page for Logout
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        login_session.clear()
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session.clear()
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        login_session.clear()
        return redirect(render_template('index.html'))

    return render_template('logged_out.html')

#  ------------------------------  item ------------------------------
#view of selected Item
@app.route('/catalog/<string:category_name>/<string:item_name>')
@app.route('/catalog/<string:category_name>/<string:item_name>.json',
           endpoint="item-json")
def itemDetails(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).one()

    if request.path.endswith('.json'):
        return jsonify(item.serialize)

    logged_in = is_logged_in()
    user_id = login_session.get('user_id')

    return render_template('item_view.html',
                           item=item,
                           user_id=user_id,
                           logged_in=logged_in,
                           )

#Add New Item (for logged user only)
@app.route('/catalog/new-item', methods=['GET', 'POST'])
def addNewItem():
    logged_in = is_logged_in()

    if request.method == 'POST':
        user_id = login_session.get('user_id')

        if user_id is None:
            # ensure only authenticated users are allowed
            return render_template('error.html',
                                   error='Invalid user',
                                   logged_in=logged_in)

        category = request.form['category_name']
        item_name = request.form['name']
        item_description = request.form['description']

        if category is None or category.strip() == '':
            return render_template('error.html',
                                   error='Invalid category name',
                                   logged_in=logged_in)

        if item_name is None or item_name.strip() == '':
            return render_template('error.html',
                                   error='Invalid item name',
                                   logged_in=logged_in)

        item = Item(name=item_name,
                    description=item_description,
                    user_id=user_id,
                    category_name=category)
        session.add(item)
        session.commit()
        flash('New item added')
        return redirect(url_for('itemDetails',
                                category_name=item.category_name,
                                item_name=item.name))
    else:
        categories = session.query(Category).all()
        return render_template('item_add.html',
                               categories=categories,
                               logged_in=logged_in)

#Edit Item (for logged user only)
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    logged_in = is_logged_in()
    item = session.query(Item).filter_by(name=item_name).one()
    user_id = login_session.get('user_id')

    if request.method == 'POST':

        if user_id is None or user_id != item.user_id:
            # ensure only authorized users are allowed
            return render_template('error.html',
                                   error='Invalid user',
                                   logged_in=logged_in)

        category = request.form['category_name']
        new_name = request.form['name']
        new_description = request.form['description']

        if category is None or category.strip() == '':
            return render_template('error.html',
                                   error='Invalid category name',
                                   logged_in=logged_in)

        if new_name is None or new_name.strip() == '':
            return render_template('error.html',
                                   error='Invalid item name',
                                   logged_in=logged_in)

        item.name = new_name
        item.description = new_description
        item.category_name = category

        session.add(item)
        session.commit()
        flash('Item edited')
        return redirect(url_for('itemDetails',
                                category_name=item.category_name,
                                item_name=item.name))
    else:
        categories = session.query(Category).all()
        return render_template('item_edit.html',
                               categories=categories,
                               item=item,
                               user_id=user_id,
                               logged_in=logged_in)

#Delete Items (for logged user only)
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    logged_in = is_logged_in()
    item = session.query(Item).filter_by(name=item_name).one()
    user_id = login_session.get('user_id')

    if request.method == 'POST':

        if user_id is None or user_id != item.user_id:
            # ensure only authorized users are allowed
            return render_template('error.html',
                                   error='Invalid user',
                                   logged_in=logged_in)

        session.delete(item)
        session.commit()

        flash('Item deleted')
        return redirect(url_for('home'))
    else:
        return render_template('item_delete.html',
                               item=item,
                               user_id=user_id,
                               logged_in=logged_in)
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(32))

def is_logged_in():
	access_token = login_session.get('access_token')
  	return access_token is not None

def load_client_secret():
    global client_secrets
    # with open(CLIENT_SECRETS_FILE) as f:
    client_secrets = json.load(open('/vagrant/catalog/client_secret.json'))['web']

if __name__ == '__main__':
    load_client_secret()
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)    
