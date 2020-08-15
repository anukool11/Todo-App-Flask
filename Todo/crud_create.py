
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

myFirstRestaurant = Restaurant(name = "Maharaja")
session.add(myFirstRestaurant)
session.commit()

session.query(Restaurant).all()

cheesepizza = MenuItem(name = "Spanish white sauce pasta", description = "Spanish pasta with original European flavor", course = "Meal", price = "$15.99",
                       restaurant = myFirstRestaurant)

chocolate = MenuItem(name = "Egg Burger", description = "Half fried egg spread with Italian buns and added veggies", course = "Entree", price = "$5.50",
                       restaurant = myFirstRestaurant)

session.add(cheesepizza)
session.add(chocolate)
session.commit()
session.query(MenuItem).all()

firstResult = session.query(Restaurant).first()
print(firstResult.name) 
