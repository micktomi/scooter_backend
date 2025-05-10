from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import models, schemas, crud
import database
from datetime import date  # αν δεν υπάρχει ήδη
from datetime import datetime  # Πρόσθεσε αυτό
from typing import Optional
from datetime import timedelta  # Προσθέστε αυτή τη γραμμή στις εισαγωγές

# Δημιουργία πινάκων (αν δεν υπάρχουν)
Base = database.Base
engine = database.engine
SessionLocal = database.SessionLocal

# Αφαίρεσα αυτή τη γραμμή ώστε να μη χάνονται τα δεδομένα σε κάθε επανεκκίνηση
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scooter Service API")
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h1>Scooter Service API</h1><p>Η εφαρμογή λειτουργεί σωστά.</p>"


# CORS για frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency για DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========= CUSTOMERS ==========

@app.post("/customers", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, customer)


@app.get("/customers/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db, skip, limit)


@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Ο πελάτης δεν βρέθηκε")
    return db_customer


@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: int, customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Ο πελάτης δεν βρέθηκε")

    # Ενημέρωση των πεδίων
    for key, value in customer.model_dump().items():
        if hasattr(db_customer, key):
            setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.delete("/customers/{customer_id}", response_model=schemas.Customer)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Ο πελάτης δεν βρέθηκε")
    return crud.delete_customer(db, customer_id)


# ========= SCOOTERS ==========

@app.post("/scooters/", response_model=schemas.Scooter)
def create_scooter(scooter: schemas.ScooterCreate, db: Session = Depends(get_db)):
    return crud.create_scooter(db, scooter)


@app.get("/scooters/", response_model=List[schemas.Scooter])
def get_scooters(db: Session = Depends(get_db)):
    scooters = crud.get_scooters(db)
    return scooters


@app.get("/scooters/{scooter_id}", response_model=schemas.Scooter)
def get_scooter(scooter_id: int, db: Session = Depends(get_db)):
    db_scooter = crud.get_scooter(db, scooter_id)
    if db_scooter is None:
        raise HTTPException(status_code=404, detail="Το σκούτερ δεν βρέθηκε")
    return db_scooter


@app.put("/scooters/{scooter_id}", response_model=schemas.Scooter)
def update_scooter(scooter_id: int, scooter: schemas.ScooterCreate, db: Session = Depends(get_db)):
    db_scooter = crud.get_scooter(db, scooter_id)
    if db_scooter is None:
        raise HTTPException(status_code=404, detail="Το σκούτερ δεν βρέθηκε")

    # Κρατάμε αντίγραφο του is_sold και selling_price πριν την ενημέρωση
    was_sold_before = db_scooter.is_sold
    old_selling_price = db_scooter.selling_price

    # Ενημέρωση των πεδίων
    for key, value in scooter.model_dump().items():
        if hasattr(db_scooter, key):
            setattr(db_scooter, key, value)

    db.commit()
    db.refresh(db_scooter)
    
    # Έλεγχος αν το σκούτερ μόλις πουλήθηκε και έχει τιμή πώλησης
    newly_sold = db_scooter.is_sold and not was_sold_before and db_scooter.selling_price
    price_changed = db_scooter.is_sold and was_sold_before and db_scooter.selling_price != old_selling_price
    
    if newly_sold or price_changed:
        # Υπολογισμός κέρδους εάν υπάρχει τιμή αγοράς
        profit = None
        profit_text = ""
        if db_scooter.purchase_price and db_scooter.purchase_price > 0:
            profit = db_scooter.selling_price - db_scooter.purchase_price
            profit_text = f" (Κέρδος: {profit}€)"
        
        # Εύρεση πληροφοριών πελάτη αν υπάρχει
        customer_info = ""
        customer_id = None
        if db_scooter.sold_to_customer_id:
            customer = db.query(models.Customer).filter(models.Customer.id == db_scooter.sold_to_customer_id).first()
            if customer:
                customer_info = f" στον/στην {customer.name}"
                customer_id = customer.id
                
        # Δημιουργία ή ενημέρωση συναλλαγής
        # Έλεγχος για υπάρχουσα συναλλαγή
        transaction_description = f"Πώληση Σκούτερ {db_scooter.brand} {db_scooter.model}"
        existing_transaction = db.query(models.Transaction).filter(
            models.Transaction.type == "income",
            models.Transaction.category == "scooter_sale",
            models.Transaction.description.startswith(transaction_description)
        ).first()
        
        if existing_transaction and price_changed:
            # Ενημέρωση υπάρχουσας συναλλαγής
            existing_transaction.amount = db_scooter.selling_price
            existing_transaction.date = db_scooter.sold_date or datetime.now().date()
            existing_transaction.description = f"{transaction_description}{customer_info}{profit_text}"
            existing_transaction.customer_id = customer_id
            db.commit()
        elif newly_sold:
            # Δημιουργία νέας συναλλαγής
            transaction = models.Transaction(
                date=db_scooter.sold_date or datetime.now().date(),
                amount=db_scooter.selling_price,
                description=f"{transaction_description}{customer_info}{profit_text}",
                type="income",
                category="scooter_sale",
                customer_id=customer_id,
                notes=f"Πινακίδα: {db_scooter.plate or 'N/A'}"
            )
            db.add(transaction)
            db.commit()
    
    return db_scooter


@app.delete("/scooters/{scooter_id}", response_model=schemas.Scooter)
def delete_scooter(scooter_id: int, db: Session = Depends(get_db)):
    db_scooter = crud.get_scooter(db, scooter_id)
    if db_scooter is None:
        raise HTTPException(status_code=404, detail="Το σκούτερ δεν βρέθηκε")

    # Διαγραφή σχετικών συναλλαγών εσόδων εάν υπάρχουν (από πώληση)
    if db_scooter.is_sold:
        transaction_desc = f"Πώληση Σκούτερ {db_scooter.brand} {db_scooter.model}"
        scooter_transactions = db.query(models.Transaction).filter(
            models.Transaction.type == "income",
            models.Transaction.category == "scooter_sale",
            models.Transaction.description.startswith(transaction_desc)
        ).all()
        
        for transaction in scooter_transactions:
            db.delete(transaction)
    
    # Διαγραφή σκούτερ
    db.delete(db_scooter)
    db.commit()
    return db_scooter


# ========= SERVICES ==========

@app.post("/services/", response_model=schemas.Service)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    # Δημιουργία της υπηρεσίας
    db_service = crud.create_service(db, service)
    
    # Αν η υπηρεσία έχει κόστος, δημιουργούμε μια εγγραφή εσόδων
    if db_service.cost and db_service.cost > 0:
        # Εύρεση πληροφοριών πελάτη αν υπάρχει scooter_id
        customer_name = ""
        customer_id = None
        
        if db_service.scooter_id:
            scooter = db.query(models.Scooter).filter(models.Scooter.id == db_service.scooter_id).first()
            if scooter and scooter.customer_id:
                customer = db.query(models.Customer).filter(models.Customer.id == scooter.customer_id).first()
                if customer:
                    customer_name = f" για {customer.name}"
                    customer_id = customer.id
        
        # Δημιουργία συναλλαγής εσόδου
        transaction = models.Transaction(
            date=db_service.date,
            amount=db_service.cost,
            description=f"Υπηρεσία: {db_service.service_type}{customer_name}",
            type="income",
            category="service",
            customer_id=customer_id,
            notes=db_service.description
        )
        
        # Αποθήκευση στη βάση
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
    
    return db_service


@app.get("/services/", response_model=List[schemas.Service])
def get_all_services(db: Session = Depends(get_db)):
    return crud.get_all_services(db)


@app.get("/services/by_scooter/{scooter_id}", response_model=list[schemas.Service])
def get_services(scooter_id: int, db: Session = Depends(get_db)):
    return crud.get_services_by_scooter(db, scooter_id)


@app.get("/services/{service_id}", response_model=schemas.Service)
def get_service(service_id: int, db: Session = Depends(get_db)):
    db_service = crud.get_service(db, service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Η υπηρεσία δεν βρέθηκε")
    return db_service


@app.put("/services/{service_id}", response_model=schemas.Service)
def update_service(service_id: int, service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db_service = crud.get_service(db, service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Η υπηρεσία δεν βρέθηκε")

    # Κρατάμε το παλιό κόστος για σύγκριση
    old_cost = db_service.cost or 0
    
    # Ενημέρωση των πεδίων
    for key, value in service.model_dump().items():
        if hasattr(db_service, key):
            setattr(db_service, key, value)

    db.commit()
    db.refresh(db_service)
    
    # Αν το κόστος άλλαξε, ενημερώνουμε την αντίστοιχη συναλλαγή ή δημιουργούμε νέα αν δεν υπάρχει
    new_cost = db_service.cost or 0
    if new_cost != old_cost:
        # Αναζήτηση υπάρχουσας συναλλαγής για αυτή την υπηρεσία
        existing_transaction = db.query(models.Transaction).filter(
            models.Transaction.type == "income",
            models.Transaction.category == "service",
            models.Transaction.description.like(f"Υπηρεσία: {db_service.service_type}%")
        ).order_by(models.Transaction.date.desc()).first()
        
        # Εύρεση πληροφοριών πελάτη αν υπάρχει scooter_id
        customer_name = ""
        customer_id = None
        if db_service.scooter_id:
            scooter = db.query(models.Scooter).filter(models.Scooter.id == db_service.scooter_id).first()
            if scooter and scooter.customer_id:
                customer = db.query(models.Customer).filter(models.Customer.id == scooter.customer_id).first()
                if customer:
                    customer_name = f" για {customer.name}"
                    customer_id = customer.id
        
        if existing_transaction:
            # Ενημέρωση υπάρχουσας συναλλαγής
            existing_transaction.amount = new_cost
            existing_transaction.date = db_service.date
            existing_transaction.description = f"Υπηρεσία: {db_service.service_type}{customer_name}"
            existing_transaction.customer_id = customer_id
            existing_transaction.notes = db_service.description
            db.commit()
        elif new_cost > 0:
            # Δημιουργία νέας συναλλαγής εάν δεν υπάρχει
            transaction = models.Transaction(
                date=db_service.date,
                amount=new_cost,
                description=f"Υπηρεσία: {db_service.service_type}{customer_name}",
                type="income",
                category="service",
                customer_id=customer_id,
                notes=db_service.description
            )
            db.add(transaction)
            db.commit()
    
    return db_service


@app.delete("/services/{service_id}", response_model=schemas.Service)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    db_service = crud.get_service(db, service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Η υπηρεσία δεν βρέθηκε")

    # Αναζήτηση και διαγραφή σχετικών συναλλαγών
    related_transactions = db.query(models.Transaction).filter(
        models.Transaction.type == "income",
        models.Transaction.category == "service",
        models.Transaction.description.like(f"Υπηρεσία: {db_service.service_type}%")
    ).all()
    
    for transaction in related_transactions:
        db.delete(transaction)
    
    # Διαγραφή της υπηρεσίας
    db.delete(db_service)
    db.commit()
    return db_service

# ========= EXPENSES ==========



# ========= SPARE PARTS ==========

@app.post("/spare-parts/", response_model=schemas.SparePart)
def create_spare_part(spare_part: schemas.SparePartCreate, db: Session = Depends(get_db)):
    db_spare_part = models.SparePart(**spare_part.model_dump())
    db.add(db_spare_part)
    db.commit()
    db.refresh(db_spare_part)
    return db_spare_part


@app.get("/spare-parts/", response_model=List[schemas.SparePart])
def read_spare_parts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    spare_parts = db.query(models.SparePart).offset(skip).limit(limit).all()
    return spare_parts


@app.get("/spare-parts/{spare_part_id}", response_model=schemas.SparePart)
def read_spare_part(spare_part_id: int, db: Session = Depends(get_db)):
    db_spare_part = db.query(models.SparePart).filter(models.SparePart.id == spare_part_id).first()
    if db_spare_part is None:
        raise HTTPException(status_code=404, detail="Το ανταλλακτικό δεν βρέθηκε")
    return db_spare_part


@app.put("/spare-parts/{spare_part_id}", response_model=schemas.SparePart)
def update_spare_part(spare_part_id: int, spare_part: schemas.SparePartCreate, db: Session = Depends(get_db)):
    db_spare_part = db.query(models.SparePart).filter(models.SparePart.id == spare_part_id).first()
    if db_spare_part is None:
        raise HTTPException(status_code=404, detail="Το ανταλλακτικό δεν βρέθηκε")

    for key, value in spare_part.model_dump().items():
        setattr(db_spare_part, key, value)

    db.commit()
    db.refresh(db_spare_part)
    return db_spare_part


@app.delete("/spare-parts/{spare_part_id}", response_model=schemas.SparePart)
def delete_spare_part(spare_part_id: int, db: Session = Depends(get_db)):
    db_spare_part = db.query(models.SparePart).filter(models.SparePart.id == spare_part_id).first()
    if db_spare_part is None:
        raise HTTPException(status_code=404, detail="Το ανταλλακτικό δεν βρέθηκε")

    db.delete(db_spare_part)
    db.commit()
    return db_spare_part


@app.post("/spare-parts/sell", response_model=schemas.Transaction)  # Χωρίς κάθετο στο τέλος
def sell_spare_part(
        sale: schemas.SparePartSale,
        db: Session = Depends(get_db)
):
    # ... ο υπόλοιπος κώδικας παραμένει ίδιος ...
    # Έλεγχος ότι το ανταλλακτικό υπάρχει
    spare_part = db.query(models.SparePart).filter(models.SparePart.id == sale.spare_part_id).first()
    if not spare_part:
        raise HTTPException(status_code=404, detail="Το ανταλλακτικό δεν βρέθηκε")

    # Έλεγχος διαθεσιμότητας
    if spare_part.stock < sale.quantity:
        raise HTTPException(status_code=400, detail=f"Μη επαρκές απόθεμα. Διαθέσιμα: {spare_part.stock}")

    # Έλεγχος πελάτη αν έχει οριστεί
    if sale.customer_id:
        customer = db.query(models.Customer).filter(models.Customer.id == sale.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Ο πελάτης δεν βρέθηκε")

    # Μείωση αποθέματος
    spare_part.stock -= sale.quantity
    db.add(spare_part)  # Προσθέστε αυτή τη γραμμή

    # Δημιουργία συναλλαγής
    transaction = models.Transaction(
        date=datetime.now().date(),
        amount=sale.sale_price * sale.quantity,
        description=f"Πώληση {sale.quantity} τεμ. {spare_part.name}",
        type="income",
        category="parts_sale",
        spare_part_id=spare_part.id,
        customer_id=sale.customer_id,
        notes=sale.notes
    )

    # Αποθήκευση στη βάση
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


# ========= TRANSACTIONS AND FINANCIAL SUMMARY ==========

@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, transaction)

@app.get("/transactions/", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    transactions = crud.get_transactions_by_period(
        db, type, category, start_date, end_date, skip, limit
    )
    return transactions

@app.get("/transactions/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Η συναλλαγή δεν βρέθηκε")
    return db_transaction

@app.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(transaction_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Η συναλλαγή δεν βρέθηκε")
    return crud.update_transaction(db, transaction_id, transaction)

@app.delete("/transactions/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Η συναλλαγή δεν βρέθηκε")
    return crud.delete_transaction(db, transaction_id)

@app.post("/expenses/", response_model=schemas.Transaction)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    # Μετατροπή του ExpenseCreate σε TransactionCreate
    transaction_data = {
        "date": expense.date,
        "amount": expense.amount,
        "description": expense.description,
        "type": "expense",
        "category": expense.category or "OTHER_EXPENSES"
    }
    transaction = schemas.TransactionCreate(**transaction_data)
    return crud.create_transaction(db, transaction)

@app.get("/financial/summary/", response_model=dict)
def get_financial_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return crud.get_financial_summary(db, start_date, end_date)

@app.get("/financial/income/", response_model=List[dict])
def get_income_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return crud.get_income_summary(db, start_date, end_date)

@app.get("/financial/expenses/", response_model=List[dict])
def get_expense_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return crud.get_expense_summary(db, start_date, end_date)

@app.get("/financial/monthly/", response_model=List[dict])
def get_monthly_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = datetime.now().date() - timedelta(days=365)
    if not end_date:
        end_date = datetime.now().date()
    
    return crud.get_monthly_summary(db, start_date, end_date)