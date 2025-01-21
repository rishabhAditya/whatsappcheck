from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an engine and a base class
engine = create_engine('sqlite:///example.db')
Base = declarative_base()

# Define the User class
class User(Base):
    __tablename__ = 'users'
    phone_number = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)

# Create the table
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Function to add or update a user
def add_or_update_user(phone_number, name, email):
    user = session.query(User).filter_by(phone_number=phone_number).first()
    if user:
        user.name = name
        user.email = email
    else:
        user = User(phone_number=phone_number, name=name, email=email)
        session.add(user)
    session.commit()

# Example usage
# add_or_update_user('1234567890', 'John Doe', 'john.doe@example.com')
# add_or_update_user('0987654321', 'Jane Smith', 'jane.smith@example.com')
