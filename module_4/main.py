import math

from db.connection import SessionLocal
from db.models.material import MaterialModel
from db.models.product_type import ProductTypeModel
session = SessionLocal()


def module_4(product_type_id, material_id, quantity):

    if product_type_id <= 0:
        return -1
    if material_id <= 0:
        return -1
    if quantity <= 0:
        return -1

    product_type: ProductTypeModel = session.query(ProductTypeModel).filter(ProductTypeModel.id == product_type_id).first()
    if product_type is None:
        return -1
    material: MaterialModel = session.query(MaterialModel).filter(MaterialModel.id == material_id).first()
    if material is None:
        return -1

    material_per_product = quantity * product_type.coefficient_of_product_type
    total_material = material_per_product * (1 + material.percentage_of_defective_material / 100)

    return math.ceil(total_material)