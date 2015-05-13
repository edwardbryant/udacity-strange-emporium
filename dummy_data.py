from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Base, Item, Category, ItemCategory
 
engine = create_engine('sqlite:///strange_emporium.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Clear databases
categories = session.query(Category).all()
for category in categories:
    session.delete(category)
    session.commit()

items = session.query(Item).all()
for item in items:
    session.delete(item)
    session.commit()

items_categories = session.query(ItemCategory).all()
for item_category in items_categories:
    session.delete(item_category)
    session.commit()


# Add Catergories
category1 = Category(name = "medical")
session.add(category1)
session.commit()

category2 = Category(name = "scientific")
session.add(category2)
session.commit()

category3 = Category(name = "nautical")
session.add(category3)
session.commit()

category4 = Category(name = "astronomical")
session.add(category4)
session.commit()

category5 = Category(name = "uncategorized")
session.add(category5)
session.commit()


# Add items and item-category assignments
item1 = Item(name = "Thing 1",
             img = "thing1.png",
             featured = 0,
             price = "$99.99",
             description = "The first thing is thing 1, it's scientific and much better than thing 2 or thing 3.")
session.add(item1)
session.commit()
item_category1 = ItemCategory(item = item1, category = category2)
session.add(item_category1)
session.commit()
item_category2 = ItemCategory(item = item1, category = category4)
session.add(item_category2)
session.commit()

item2 = Item(name = "Nach Collin Drill",
             img = "image.png",
             featured = 0,
             price = "$199.88",
             description = "A Nach Collin drill instrument with multiplying action (c. 1900). This instrument can make more turnings by the cogs than the earlier archimedes drill. 18 cm long and in good condition.")
session.add(item2)
session.commit()
item_category3 = ItemCategory(item = item2, category = category1)
session.add(item_category3)
session.commit()

item3 = Item(name = "Victorian Apothecary Cabinet",
             img = "image.png",
             featured = 0,
             price = "$1299.00",
             description = "A Victorian-era (c. 1860) apothecary/chemist chest of drawers. The cabinet is made of mahogany and, as you can see, the drawers have wonderful color and patina. The drawers retain there original wooden handles, dovetail joints, and gilded name plates.")
session.add(item3)
session.commit()
item_category4 = ItemCategory(item = item3, category = category1)
session.add(item_category4)
session.commit()

item4 = Item(name = "Walking Stick with Telescope",
             img = "image.png",
             featured = 0,
             price = "$299.99",
             description = "A walkingstick with a built in telescope (c 1890's). The telescope is integrated into the ivory handle. The walking stick is made from ivory, mahogany, and brass with a length of 89 cm.")
session.add(item4)
session.commit()
item_category5 = ItemCategory(item = item4, category = category2)
session.add(item_category5)
session.commit()

item5 = Item(name = "Celestial Sphere",
             img = "image.png",
             featured = 1,
             price = "$459.99",
             description = "An Abel-Klinger celestial sphere (c. 1855-1895). The globe at the center of the sphere is 4-inch (10.2 cm). Good condition.")
session.add(item5)
session.commit()
item_category6 = ItemCategory(item = item5, category = category2)
session.add(item_category6)
session.commit()
item_category7 = ItemCategory(item = item5, category = category4)
session.add(item_category7)
session.commit()

item6 = Item(name = "Brass Ship Propeller",
             img = "image.png",
             featured = 0,
             price = "$929.99",
             description = "A three-blade solid brass ship propeller. It is inscribed: 'J. Stone & Co., Deptford 1942' Dimension 43 x 10 cm.")
session.add(item6)
session.commit()
item_category8 = ItemCategory(item = item6, category = category3)
session.add(item_category8)
session.commit()

item7 = Item(name = "Ebony Sailor's Whistle",
             img = "image.png",
             featured = 0,
             price = "$99.99",
             description = "An early hand-made ebony sailor's whistle, approx. 3 inches long. In excellant condition - works perfectly and quite loud. Shows use and age, but no damage or issues.")
session.add(item7)
session.commit()
item_category9 = ItemCategory(item = item7, category = category3)
session.add(item_category9)
session.commit()


print "added dummy data!" 
print "\n"

"""
print "CATEGORIES: "
categories = session.query(Category).all()
for category in categories:
    print ("ID: [" + str(category.id) + "]"), ("NAME: [" + category.name + "]")
print "\n"

print "ITEMS: "
items = session.query(Item).all()
for item in items:
    print ("ID: [" + str(item.id) + "]"), ("NAME: [" + item.name + "]")
print "\n"

print "ITEM-CATEGORY ASSIGNMENTS: "
items_categories = session.query(ItemCategory).all()
for item_category in items_categories:
    print ("ID: [" + str(item_category.id) + "]"), ("ITEM: [" + str(item_category.item_id) + "]"), ("CATEGORY: [" + str(item_category.category_id) + "]")
print "\n"
"""

