from app.core.database import db

# استيراد الموديلات حتى تكون متاحة عند استيراد app.models
from .user import User
from .employee import Employee
from .product import Product
from .warehouse import Warehouse
from .inbound import Inbound
from .data_entry import DataEntry
from .archive import Archive

__all__ = [
    "db",
    "User",
    "Employee",
    "Product",
    "Warehouse",
    "Inbound",
    "Outbound",
    "DataEntry",
    "Archive",
]
