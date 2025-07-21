from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Category:
    id: Optional[int]
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    level: int
    product_count: int
    
    def __init__(self, name: str, description: Optional[str] = None, 
                 parent_id: Optional[int] = None, id: Optional[int] = None,
                 level: int = 1, product_count: int = 0):
        self.id = id
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.level = level
        self.product_count = product_count
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'level': self.level,
            'product_count': self.product_count
        }

@dataclass
class Product:
    id: Optional[int]
    name: str
    description: Optional[str]
    price: float
    category_id: int
    
    def __init__(self, name: str, price: float, category_id: int,
                 description: Optional[str] = None, id: Optional[int] = None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category_id = category_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_id': self.category_id
        }