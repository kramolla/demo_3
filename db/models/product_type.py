from sqlalchemy import Column, Integer, Float, String
from db.connection import Base

class ProductTypeModel(Base):
    __tablename__ = "product_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    production_type = Column(String(50), nullable=False)
    coefficient = Column(Float, nullable=False)
