FROM python:3.10-slim-buster

WORKDIR /stocknear-backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy .env file first (if it exists)
COPY .env .env

COPY . .

# Create directories for databases
RUN mkdir -p data/sqlite backup_db

# Initialize databases with proper error handling
RUN set -e; \
    if [ -f .env ]; then \
        export $(cat .env | xargs); \
        python create_stock_db.py && \
        python create_crypto_db.py && \
        python create_institute_db.py && \
        python create_index_db.py && \
        python create_etf_db.py && \
        cp backup_db/* data/sqlite/ || exit 1; \
    else \
        echo "Warning: .env file not found. Database initialization skipped."; \
        touch data/sqlite/stocks.db data/sqlite/crypto.db data/sqlite/institute.db data/sqlite/index.db data/sqlite/etf.db; \
    fi

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]