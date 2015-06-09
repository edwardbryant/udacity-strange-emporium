
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker 
from database_setup import Base, Item, Category, ItemCategory #, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

engine = create_engine('sqlite:///strange_emporium.db')
Base.metadata.bind = engine 

DBSession = sessionmaker(bind=engine)
session = DBSession()

# routes

@app.route('/')
def ShowHome():
    featured_items = session.query(Item).filter_by(featured = 1)
    return render_template('index.html', featured_items = featured_items)


@app.route('/visit/')
def ShowLocation():
    return render_template('store-location.html')


@app.route('/categories/')
def ShowCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    return render_template('categories-list.html', categories = categories)


@app.route('/categories/<int:c_id>/')
def ShowItemsInCategory(c_id):
    items = session.query(Item).join(ItemCategory, Item.id == ItemCategory.item_id).filter_by(category_id = c_id)
    category = session.query(Category).filter_by(id = c_id).one()
    return render_template('category.html', items = items, category = category)


@app.route('/categories/add/', methods=['GET','POST'])
def NewCategory():
    # if 'username' not in login_session:
        # return redirect('/login')
    if request.method == 'POST':
        new_category = Category(name = request.form['category-name'].lower())
        session.add(new_category)
        session.commit()
        flash('New Category Added!')
        return redirect(url_for('ShowCategories'))
    else:
        return render_template('category-add.html')


@app.route('/categories/<int:c_id>/edit/', methods=['GET','POST'])
def EditCategory(c_id):
    edited_category = session.query(Category).filter_by(id = c_id).one()
    if request.method == 'POST':
        if request.form['category-name']:
           edited_category.name = request.form['category-name']
        session.add(edited_category)
        session.commit()
        flash('Category Edited!')
        return redirect(url_for('ShowCategories'))
    else:
        return render_template('category-edit.html', category = edited_category)


@app.route('/categories/<int:c_id>/delete/', methods=['GET','POST'])
def DeleteCategory(c_id):
    deleted_category = session.query(Category).filter_by(id = c_id).one()
    if request.method == 'POST':
        id = deleted_category.id
        session.delete(deleted_category)
        session.commit()
        deleted_category_assignments = session.query(ItemCategory).filter_by(category_id = id)
        for i in deleted_category_assignments:
            session.delete(i)
            session.commit() 
        flash('Category Deleted!')
        return redirect(url_for('ShowCategories'))
    else:
        return render_template('category-delete.html', category = deleted_category)


@app.route('/items/<int:i_id>/')
def ShowItem(i_id):
    item = session.query(Item).filter_by(id = i_id).one()
    return render_template('item.html', item = item)


@app.route('/items/')
def ShowAllItems():
    items = session.query(Item).all()
    return render_template('items-all.html', items = items)


@app.route('/items/featured/')
def ShowFeaturedItems():
    featured_items = session.query(Item).filter_by(featured = 1)
    return render_template('items-featured.html', featured_items = featured_items)


@app.route('/items/newest/')
def ShowNewestItems():
    items = session.query(Item).order_by(desc(Item.id)).limit(6)
    return render_template('items-newest.html', items = items)














# login system routes

@app.route('/login/')
def ShowLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE = state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['ContentType'] = 'application/json'
        return response
    code = request.data
    try:
        # upgrade auth code into a credentials obj
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = '')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code) 
    except FlowExchangeError:
        response = make_response(json.dumps('failed to upgrade the authorization code'), 401)
        response.headers['ContentType'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # abort for error in access token info
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['ContentType'] = 'application/json'
        return response
    # verify access_token is used for intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user id doesn't match given user id."), 401)
        response.headers['ContentType'] = 'application/json'
        return response
    # verify that access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Client id does not match app's."), 401)
        response.headers['ContentType'] = 'application/json'
        return response
    # check to see if user is already logged in.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Current user is already logged in."), 200)
        response.headers['ContentType'] = 'application/json'
    # store access token for later use
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo" 
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params = params)
    data = json.loads(answer.text)
    print data
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>'
    output += login_session['username']
    output += '</h1>'
    output += '<div><img src="'
    output += login_session['picture']
    output += '" height=100 width=100></div>'
    output += '<div>'
    output += login_session['email']
    output += '</div>'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user is not connected."), 401)
        response.headers['ContentType'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers['ContentType'] = 'application/json'
        return response
    else:
        # whatever the reason, token was invalid
        response = make_response(json.dumps("Failed to revoke token for current user: result was (%s)." % result['status']), 400)
        response.headers['ContentType'] = 'application/json'
        return response








@app.route('/items/new/', methods=['GET','POST'])
def NewItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_name = request.form['item-name']
        new_img = request.form['item-img']
        new_featured = int(request.form['item-featured'])
        new_price = request.form['item-price']
        new_description = request.form['item-description'] 
        new_item = Item(name = new_name, img = new_img, featured = new_featured, price = new_price, description = new_description, user_id = login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('New Item Added!')
        return redirect(url_for('ShowAllItems'))
    else:
        return render_template('new-item.html')


@app.route('/items/<int:i_id>/edit/', methods=['GET','POST'])
def EditItem(i_id):
    edited_item = session.query(Item).filter_by(id = i_id).one()
    if request.method == 'POST':
        edited_item.name = request.form['item-name']
        edited_item.img = request.form['item-img']
        edited_item.featured = int(request.form['item-featured'])
        edited_item.price = request.form['item-price']
        edited_item.description = request.form['item-description']
        session.add(edited_item)
        session.commit()
        flash('Item Edited!')
        return redirect(url_for('ShowAllItems'))
    else:
        return render_template('edit-item.html', item = edited_item)


@app.route('/items/<int:i_id>/delete/', methods=['GET','POST'])
def DeleteItem(i_id):
    deleted_item = session.query(Item).filter_by(id = i_id).one()
    if request.method == 'POST':        
        session.delete(deleted_item)
        session.commit()
        flash('Item Deleted!')
        return redirect(url_for('ShowAllItems'))
    else:
        return render_template('delete-item.html', item = deleted_item)





# API routes

@app.route('/API/JSON/items/<int:i_id>/')
def GetItemJSON(i_id):
    item = session.query(Item).filter_by(id = i_id).one()
    return jsonify(id=item.id, name=item.name, featured=item.featured, price=item.price, description=item.description) 

@app.route('/API/JSON/categories/<int:c_id>/')
def GetCategoryJSON(c_id):
    category = session.query(Category).filter_by(id = c_id).one()
    return jsonify(id=category.id, name=category.name)

# User registration / permissions 

"""
def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], image = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user
"""

if __name__ == '__main__':
    app.secret_key = 'super-duper_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)



