from sqlalchemy import Column, Integer, ForeignKey, Date
from db.connection import Base

class OrderModel(Base):
    __tablename__ = 'orders'

    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    partner_id = Column(Integer, ForeignKey('partners.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    sale_date = Column(Date, nullable=False)
