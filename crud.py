from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import models, schemas
from datetime import date, timedelta, datetime
from typing import List, Dict, Optional, Tuple


# ========== CUSTOMERS ==========

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def update_customer(db: Session, customer_id: int, customer: schemas.CustomerCreate):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        for key, value in customer.model_dump().items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
    return customer

# ========== SCOOTERS ==========

def create_scooter(db: Session, scooter: schemas.ScooterCreate):
    db_scooter = models.Scooter(**scooter.model_dump())
    db.add(db_scooter)
    db.commit()
    db.refresh(db_scooter)
    return db_scooter

def get_scooter(db: Session, scooter_id: int):
    return db.query(models.Scooter).filter(models.Scooter.id == scooter_id).first()

def get_scooter_by_plate(db: Session, plate: str):
    return db.query(models.Scooter).filter(models.Scooter.plate == plate).first()

def get_scooters(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Scooter).offset(skip).limit(limit).all()

def update_scooter(db: Session, scooter_id: int, scooter: schemas.ScooterCreate):
    db_scooter = get_scooter(db, scooter_id)
    if db_scooter:
        for key, value in scooter.model_dump().items():
            setattr(db_scooter, key, value)
        db.commit()
        db.refresh(db_scooter)
    return db_scooter

def delete_scooter(db: Session, scooter_id: int):
    scooter = get_scooter(db, scooter_id)
    if scooter:
        db.delete(scooter)
        db.commit()
    return scooter

# ========== SERVICES ==========

def create_service(db: Session, service: schemas.ServiceCreate):
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_service(db: Session, service_id: int):
    return db.query(models.Service).filter(models.Service.id == service_id).first()

def get_services_by_scooter(db: Session, scooter_id: int):
    return db.query(models.Service).filter(models.Service.scooter_id == scooter_id).all()

def get_today_services(db: Session):
    
    today = date.today()
    return db.query(models.Service).filter(models.Service.date >= today).all()

def get_all_services(db: Session, skip: int = 0, limit: int = 100):
    from datetime import date, datetime
    services = db.query(models.Service).offset(skip).limit(limit).all()

    # Διόρθωση για τις ημερομηνίες
    for service in services:
        if isinstance(service.date, datetime):
            service.date = service.date.date()

    return services

def update_service(db: Session, service_id: int, service: schemas.ServiceCreate):
    db_service = get_service(db, service_id)
    if db_service:
        for key, value in service.model_dump().items():
            setattr(db_service, key, value)
        db.commit()
        db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int):
    service = get_service(db, service_id)
    if service:
        db.delete(service)
        db.commit()
    return service


# ========== TRANSACTIONS ==========

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionCreate):
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        for key, value in transaction.model_dump().items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    transaction = get_transaction(db, transaction_id)
    if transaction:
        db.delete(transaction)
        db.commit()
    return transaction

# ========== FINANCIAL SUMMARY ==========

def get_income_summary(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict]:
    """Συνοψίζει τα έσοδα ανά κατηγορία για συγκεκριμένο χρονικό διάστημα"""
    query = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label('total')
    ).filter(models.Transaction.type == 'income')

    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)

    query = query.group_by(models.Transaction.category)
    
    result = query.all()
    return [{'category': r.category, 'total': float(r.total)} for r in result]

def get_expense_summary(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict]:
    """Συνοψίζει τα έξοδα ανά κατηγορία για συγκεκριμένο χρονικό διάστημα"""
    query = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label('total')
    ).filter(models.Transaction.type == 'expense')

    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)

    query = query.group_by(models.Transaction.category)
    
    result = query.all()
    return [{'category': r.category, 'total': float(r.total)} for r in result]

def get_financial_summary(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
    """Παρέχει μια συνολική οικονομική σύνοψη"""
    # Υπολογισμός συνολικών εσόδων
    income_query = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.type == 'income')
    if start_date:
        income_query = income_query.filter(models.Transaction.date >= start_date)
    if end_date:
        income_query = income_query.filter(models.Transaction.date <= end_date)
    total_income = income_query.scalar() or 0.0

    # Υπολογισμός συνολικών εξόδων
    expense_query = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.type == 'expense')
    if start_date:
        expense_query = expense_query.filter(models.Transaction.date >= start_date)
    if end_date:
        expense_query = expense_query.filter(models.Transaction.date <= end_date)
    total_expenses = expense_query.scalar() or 0.0

    # Λεπτομερής ανάλυση εσόδων ανά κατηγορία
    income_by_category = get_income_summary(db, start_date, end_date)
    
    # Λεπτομερής ανάλυση εξόδων ανά κατηγορία
    expenses_by_category = get_expense_summary(db, start_date, end_date)

    # Μηνιαία σύνοψη (τελευταίοι 12 μήνες αν δεν έχουν οριστεί ημερομηνίες)
    if not start_date:
        start_date = datetime.now().date() - timedelta(days=365)
    if not end_date:
        end_date = datetime.now().date()
    
    monthly_summary = get_monthly_summary(db, start_date, end_date)

    return {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'profit': float(total_income - total_expenses),
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
        'monthly_summary': monthly_summary
    }

def get_monthly_summary(db: Session, start_date: date, end_date: date) -> List[Dict]:
    """Παρέχει μηνιαία σύνοψη εσόδων και εξόδων"""
    # Θα χρησιμοποιήσουμε SQLAlchemy core για να κάνουμε group by ανά μήνα
    # Αυτό είναι πιο σύνθετο και εξαρτάται από τη βάση δεδομένων (SQLite, PostgreSQL, κλπ.)
    # Για απλότητα, θα χρησιμοποιήσουμε μια απλή προσέγγιση

    monthly_data = []
    current_date = start_date.replace(day=1)  # Ξεκινάμε από την αρχή του μήνα
    
    while current_date <= end_date:
        next_month = current_date.replace(day=28) + timedelta(days=4)  # Πηγαίνουμε στον επόμενο μήνα
        month_end = next_month.replace(day=1) - timedelta(days=1)  # Τελευταία μέρα του τρέχοντος μήνα
        
        # Έσοδα για τον τρέχοντα μήνα
        income = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.type == 'income',
            models.Transaction.date >= current_date,
            models.Transaction.date <= month_end
        ).scalar() or 0.0
        
        # Έξοδα για τον τρέχοντα μήνα
        expenses = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.type == 'expense',
            models.Transaction.date >= current_date,
            models.Transaction.date <= month_end
        ).scalar() or 0.0
        
        # Προσθήκη δεδομένων για τον τρέχοντα μήνα
        monthly_data.append({
            'month': current_date.strftime('%Y-%m'),
            'month_name': current_date.strftime('%B %Y'),
            'income': float(income),
            'expenses': float(expenses),
            'profit': float(income - expenses)
        })
        
        # Μετάβαση στον επόμενο μήνα
        current_date = next_month.replace(day=1)
    
    return monthly_data

def get_transactions_by_period(
    db: Session, 
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[models.Transaction]:
    """Ανακτά συναλλαγές φιλτραρισμένες με βάση τον τύπο, την κατηγορία και το χρονικό διάστημα"""
    query = db.query(models.Transaction)
    
    if transaction_type:
        query = query.filter(models.Transaction.type == transaction_type)
    
    if category:
        query = query.filter(models.Transaction.category == category)
    
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)
    
    # Ταξινόμηση με βάση την ημερομηνία (πιο πρόσφατες πρώτα)
    query = query.order_by(models.Transaction.date.desc(), models.Transaction.id.desc())
    
    # Σελιδοποίηση
    result = query.offset(skip).limit(limit).all()
    
    return result


