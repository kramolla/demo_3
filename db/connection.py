from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

database_url = "postgresql+psycopg://postgres:123456@localhost:5432/test"
Base = declarative_base()
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)
