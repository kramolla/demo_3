from sqlalchemy import Column, Integer, String
from db.connection import Base

class PartnerModel(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    partner_type = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    legal_address = Column(String(100), nullable=False)
    inn = Column(String, nullable=False)
    director = Column(String(50), nullable=False)
    phone = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    rating = Column(Integer, nullable=False)
