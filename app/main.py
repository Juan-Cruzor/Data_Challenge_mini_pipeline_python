from fastapi import FastAPI
from app.db import get_conn
from app.pipeline import run_pipeline

app = FastAPI()

@app.get("/daily_stats")

def get_daily_stats(date):
    """Function that gets the table for a date in the endpoint"""

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id, searches, purchases, total_purchased_amount
    FROM daily_user_stats
    WHERE date=%s
    """,(date,))

    rows = cursor.fetchall()

    result = []

    for user_id, searches, purchases, amount in rows:
        result.append({
            "user_id": user_id,
            "searches": searches,
            "purchases": purchases,
            "total_purchased_amount": float(amount)
        })
    
    return result

if __name__ == "__main__":
    run_pipeline("data/events.json")