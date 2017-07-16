from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine, event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    picture = Column(String(250))
    email = Column(String(250), nullable=False)
    


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)

    # unique URLs to identify a category  by name 
    # but not by ID. 
    #ForeignKey also required for the situation
    name = Column(String(250), unique=True, nullable=False)

    @property
    def serialize(self):
        """Return object in serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)

    # unique URLs to identify a category  by name 
    #but not by ID. 
    name = Column(String(250), unique=True, nullable=False)
    description = Column(String(250))
    category_name = Column(Integer, ForeignKey('category.name'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category_name,
        }


engine = create_engine('sqlite:///catalogs.db')

# This function configures SQLite to enforce foreign key
# constraints in connections made from this application.
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Base.metadata.create_all(engine)
