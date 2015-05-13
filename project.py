
from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from database_setup import Base, Item, Category, ItemCategory

engine = create_engine('sqlite:///strange_emporium.db')
Base.metadata.bind = engine 

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/categories')
def ShowCategories():
    categories = session.query(Category).all()
    output = ''
    for category in categories:
        output += "<a href='#'>" + category.name + "</a><br>"
    return output    


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)



