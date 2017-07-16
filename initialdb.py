from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Category, Item, User, engine

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

default_user = User(id=1, name="Default User", email="defaultuser@example.com")
session.add(default_user)

category1 = Category(id=1, name='Soccer')
category2 = Category(id=2, name='Basketball')
category3 = Category(id=3, name='Baseball')
category4 = Category(id=4, name='Frisbee')
category5 = Category(id=5, name='Snowboarding')
category6 = Category(id=6, name='Rock Climbing')
category7 = Category(id=7, name='Foosball')
category8 = Category(id=8, name='Skating')
category9 = Category(id=9, name='Hockey')
category10 = Category(id=10, name='ping-pong')

session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.add(category5)
session.add(category6)
session.add(category7)
session.add(category8)
session.add(category9)
session.add(category10)

item1 = Item(id=1, name='gate',
             description='Players are not allowed to touch the ball with their hands in play.',
             category=category1,
             user=default_user)
item2 = Item(id=2, name='ball',
             description='players mainly use their feet to strike or pass the ball.',
             category=category1,
             user=default_user)
item3 = Item(id=3, name='Association',
             description='organises World Cups for both men and women every four years',
             category=category1,
             user=default_user)

item4 = Item(id=4, name='Kansas',
             description='intercollegiate men \'s basketball program of the University of Kansas.',
             category=category2,
             user=default_user)

item5 = Item(id=5, name='NCAA',
             description='National Collegiate Athletic Association',
             category=category2,
             user=default_user)

item6 = Item(id=6, name='Major League Baseball',
             description='''Major League Baseball (MLB) is a professional baseball league,
              the oldest of the four major professional sports leagues 
              in the United States and Canada. ''',
             category=category3,
             user=default_user)

item7 = Item(id=7, name='Abner Doubleday',
             description='''In his final years in New Jersey, 
             he was a prominent member and later president of the Theosophical Society. 
             Doubleday has been historically credited with 
             inventing baseball, although this is untrue.''',
             category=category4,
             user=default_user)
item8 = Item(id=8, name='Walter Frederick Morrison',
             description='an American inventor and entrepreneur, best known as the inventor of the Frisbee.',
             category=category4,
             user=default_user)

item9 = Item(id=9, name='Jake Burton Carpenter',
             description='''Jake Burton Carpenter 
             founder of Burton Snowboards and one of the inventors of 
             the modern day snowboard. He grew up in Cedarhurst, New York.''',
             category=category5,
             user=default_user)
item10 = Item(id=10, name='Yosemite Valley',
              description='''The valley is about 8 miles long 
              and up to a mile deep, surrounded by high granite summits 
              such as Half Dome and El Capitan, and densely forested with pines. ''',
              category=category5,
              user=default_user)

item11 = Item(id=11, name='Clean climbing',
              description='contrasts against those styles which can have environmental effects.',
              category=category6,
              user=default_user)
item12 = Item(id=12, name='free climbing',
              description='Bulls Cross on the northern borders of the London Borough of Enfield',
              category=category6,
              user=default_user)
item13 = Item(id=13, name='ottenham Hotspur F.C',
              description='default description',
              category=category6,
              user=default_user)

item14 = Item(id=14, name='Ki-o-rahi',
              description='a ball sport played in New Zealand with a small round ball.',
              category=category7,
              user=default_user)
item15 = Item(id=15, name='Burton Snowboards',
              description='durton Snowboards is a manufacturer of snowboards.',
              category=category7,
              user=default_user)

item16 = Item(id=16, name='Ice skating',
              description='a ball sport played in New Zealand with a small round ball.',
              category=category8,
              user=default_user)

item17 = Item(id=17, name='Bandy',
              description='a ball on a football pitch-sized ice arena',
              category=category9,
              user=default_user)
item18 = Item(id=18, name='Field hockey',
              description='''on gravel, natural grass, 
              or sand-based or water-based artificial turf''',
              category=category9,
              user=default_user)
item19 = Item(id=19, name='china',
              description='now the champion',
              category=category10,
              user=default_user)
item20 = Item(id=20, name='Japan',
              description='the older champion',
              category=category10,
              user=default_user)

session.add(item1)
session.add(item2)
session.add(item3)
session.add(item4)
session.add(item5)
session.add(item6)
session.add(item7)
session.add(item8)
session.add(item9)
session.add(item10)
session.add(item11)
session.add(item12)
session.add(item13)
session.add(item14)
session.add(item15)
session.add(item16)
session.add(item17)
session.add(item18)
session.add(item19)
session.add(item20)

session.commit()

print('Added categories')
