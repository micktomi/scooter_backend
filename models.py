from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # Χρησιμοποιώ string αντί για αντικείμενο για το foreign key
    scooters = relationship("Scooter", back_populates="owner", foreign_keys="[Scooter.customer_id]")
    transactions = relationship("Transaction", back_populates="customer")
class Scooter(Base):
    __tablename__ = "scooters"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, index=True, nullable=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    price = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    condition = Column(String, default="Μεταχειρισμένο")

    # Νέα πεδία
    is_sold = Column(Boolean, default=False)
    sold_date = Column(Date, nullable=True)
    sold_to_customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    purchase_price = Column(Float, nullable=True)
    selling_price = Column(Float, nullable=True)

    owner = relationship("Customer", back_populates="scooters", foreign_keys=[customer_id])
    sold_to_customer = relationship("Customer", foreign_keys=[sold_to_customer_id])
    services = relationship("Service", back_populates="scooter")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    scooter_id = Column(Integer, ForeignKey("scooters.id"), nullable=True)

    service_type = Column(String)
    description = Column(String, nullable=True)
    date = Column(Date)
    cost = Column(Float, nullable=True)
    status = Column(String, default="Σε εξέλιξη")
    scooter_info = Column(String, nullable=True)

    scooter = relationship("Scooter", back_populates="services")

class SparePart(Base):
    __tablename__ = "spare_parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, index=True)
    category = Column(String)
    purchase_price = Column(Float, nullable=True)
    selling_price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=5)
    
    transactions = relationship("Transaction", back_populates="spare_part")

# Προσθέστε στο αρχείο models.py

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Float)
    description = Column(String)
    type = Column(String)  # "income" ή "expense"
    category = Column(String)  # "parts_sale", "service", "expense", κτλ.
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    notes = Column(String, nullable=True)

    # Σχέσεις (relationships)
    spare_part = relationship("SparePart", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")