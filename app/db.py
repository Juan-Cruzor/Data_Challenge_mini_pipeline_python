import psycopg2
import os

def get_conn():
    """The function establishes a connection to the PostgreSQL database"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST","db"),
        database=os.getenv("DB_NAME","events"),
        user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD","postgres")
    )