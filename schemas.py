from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

# ========== Scooter ==========
class ScooterBase(BaseModel):
    plate: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    condition: Optional[str] = "Μεταχειρισμένο"
    is_sold: Optional[bool] = False
    sold_date: Optional[date] = None
    sold_to_customer_id: Optional[int] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    
class ScooterCreate(ScooterBase):
    customer_id: Optional[int] = None  # Το κάνουμε προαιρετικό

class Scooter(ScooterBase):
    id: int
    customer_id: Optional[int] = None  # Το κάνουμε προαιρετικό
    class Config:
        from_attributes = True

# ========== Customer ==========
class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

class ServiceBase(BaseModel):
    scooter_info: str  # ή scooter_custom: str
    service_type: str
    description: Optional[str] = None
    date: date
    cost: Optional[float] = None
    status: Optional[str] = "Σε εξέλιξη"

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    class Config:
        from_attributes = True

# ========== SparePart ==========
class SparePartBase(BaseModel):
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    stock: int = 0
    min_stock: int = 5

class SparePartCreate(SparePartBase):
    pass

class SparePart(SparePartBase):
    id: int
    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    description: str
    amount: float
    date: date
    category: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int

    class Config:
        from_attributes = True


class SparePartSale(BaseModel):
    spare_part_id: int
    quantity: int = 1
    customer_id: Optional[int] = None
    sale_price: float
    notes: Optional[str] = None

class TransactionBase(BaseModel):
    date: date
    amount: float
    description: str
    type: str
    category: Optional[str] = None
    spare_part_id: Optional[int] = None
    customer_id: Optional[int] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int

    class Config:
        from_attributes = True

    # Στο τέλος του αρχείου schemas.py


class TransactionCategories:
    # Κατηγορίες Εισοδήματος
    SCOOTER_SALE = "Πώληση Σκούτερ"
    SERVICE_INCOME = "Υπηρεσίες Επισκευής"
    SPARE_PARTS_SALE = "Πώληση Ανταλλακτικών"
    OTHER_INCOME = "Λοιπά Έσοδα"

    # Κατηγορίες Εξόδων
    SALARY = "Μισθοδοσία"
    RENT = "Ενοίκιο"
    OPERATIONAL_EXPENSES = "Λειτουργικά Έξοδα"
    SPARE_PARTS_PURCHASE = "Αγορά Ανταλλακτικών"
    EQUIPMENT_MAINTENANCE = "Συντήρηση Εξοπλισμού"
    OTHER_EXPENSES = "Λοιπά Έξοδα"
    
    # Αντιστοίχιση κατηγοριών API με ονόματα για προβολή
    CATEGORY_MAPPING = {
        "scooter_sale": "Πώληση Σκούτερ",
        "service": "Υπηρεσίες Επισκευής",
        "parts_sale": "Πώληση Ανταλλακτικών",
        "other_income": "Λοιπά Έσοδα",
        "salary": "Μισθοδοσία",
        "rent": "Ενοίκιο",
        "operational_expenses": "Λειτουργικά Έξοδα",
        "spare_parts_purchase": "Αγορά Ανταλλακτικών",
        "equipment_maintenance": "Συντήρηση Εξοπλισμού",
        "other_expenses": "Λοιπά Έξοδα"
    }