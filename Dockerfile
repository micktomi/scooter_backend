FROM python:3.10-slim

WORKDIR /app

# Αντιγραφή των αρχείων requirements
COPY requirements.txt .

# Εγκατάσταση των dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Αντιγραφή του κώδικα του backend
COPY . .

# Έκθεση της θύρας 8000
EXPOSE 8000

# Εκκίνηση της εφαρμογής
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]