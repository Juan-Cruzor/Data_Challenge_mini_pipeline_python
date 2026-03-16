from fastapi import FastAPI
from app.db import get_conn

app = FastAPI()

@app.get("/daily_stats")

def get_daily_stats(date:str):
    """Function that gets the table for a date in the endpoint"""

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id, searches, purchases, total_purchased_amount
    FROM daily_user_stats
    WHERE date=%s
    """,(date,))

    rows = cursor.fetchall()

    return [
        {
            "user_id":r[0],
            "searches":r[1],
            "purchases":r[2],
            "total_purchased_amount":float(r[3])
        }
        for r in rows
    ]