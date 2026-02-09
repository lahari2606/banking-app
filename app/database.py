from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Create the database file (SQLite stores everything in this one file)
DATABASE_URL = "sqlite:///./banking.db"

# Engine = the connection to the database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session = a conversation with the database
# (like picking up the phone to talk to the bank)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = the parent class for all database tables
Base = declarative_base()


# This function gives us a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
