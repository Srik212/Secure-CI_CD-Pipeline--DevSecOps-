import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    retries = 5
    while retries > 0:
        try:
            return psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                port=os.getenv("DB_PORT", "5432"),
                dbname=os.getenv("DB_NAME", "inventory_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "admin123")
            )
        except psycopg2.OperationalError:
            retries -= 1
            print(f"DB not ready, retrying... ({retries} left)")
            time.sleep(3)
    raise Exception("Could not connect to the database after multiple retries.")
