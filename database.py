from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# base model class
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

class StarredStock(Base):
    __tablename__ = 'starred_stocks'

    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String)
    user_id = Column(ForeignKey('users.id'))

    def __repr__(self):
        return f"<StarredStock(stock_symbol={self.stock_symbol})>"

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(ForeignKey('users.id'))

    def __repr__(self):
        return f"<Report(title={self.title}, description={self.description})>"
    
class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Contact(name={self.name}, email={self.email})>"
    
# utility functions
def open_db():
    engine = create_engine('sqlite:///project.db', echo=True)
    Base.metadata.create_all(engine)
    session =  sessionmaker(bind=engine)
    return session()

def save(object):
    db = open_db()
    db.add(object)
    db.commit()
    db.close()

def get_all(table):
    db = open_db()
    data = db.query(table).all()
    db.close()
    return data




if __name__ == "__main__":
    # create engine
    
    engine = create_engine('sqlite:///project.db', echo=True)
    Base.metadata.create_all(engine)