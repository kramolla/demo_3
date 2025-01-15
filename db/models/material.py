from sqlalchemy import Column, Integer, Float, String
from db.connection import Base

class MaterialModel(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    percentage_of_defective_material = Column(Float, nullable=False)
