from sqlalchemy import Column, Integer, Float, String, ForeignKey
from db.connection import Base

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_number = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    minimum_cost = Column(Float, nullable=False)
    product_type_id = Column(Integer, ForeignKey('product_types.id'), nullable=False)
