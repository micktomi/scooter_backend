import os
import sys
from pathlib import Path

# Προσθέτουμε το τρέχοντα φάκελο στο sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Εισαγωγές από την εφαρμογή
from database import Base, engine
from models import Customer, Scooter, Service, SparePart

# Εκτυπώνουμε πληροφορίες για debug
print("Διαδρομή βάσης δεδομένων:", engine.url)
print("Μοντέλα προς δημιουργία:", [t.__tablename__ for t in Base.__subclasses__()])

# Διαγραφή όλων των πινάκων
Base.metadata.drop_all(bind=engine)
print("Διαγράφηκαν οι υπάρχοντες πίνακες")

# Δημιουργία όλων των πινάκων από την αρχή
Base.metadata.create_all(bind=engine)
print("Δημιουργήθηκαν νέοι πίνακες")

# Επιβεβαίωση της δομής του πίνακα scooters
from sqlalchemy import inspect
inspector = inspect(engine)
columns = inspector.get_columns('scooters')
column_names = [c['name'] for c in columns]
print("Στήλες του πίνακα scooters:", column_names)

print("Η βάση δεδομένων επαναδημιουργήθηκε με επιτυχία!")