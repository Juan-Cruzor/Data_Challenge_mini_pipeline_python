from fastapi import FastAPI, HTTPException, Query
from app.db import get_conn
from app.pipeline import run_pipeline
from app.logger import logger

app = FastAPI(
    title="Events Pipeline API",
    description="Query daily aggregated user metrics.",
    version="1.0.0",
)


@app.get("/daily_stats")
def get_daily_stats(date):
    """
    Return aggregated stats across all users for a given date (YYYY-MM-DD).

    Response format:
    {
        "date": "2025-01-15",
        "total_users": 3,
        "total_searches": 6,
        "total_purchases": 4,
        "total_purchased_amount": 11600.0
    }
    """
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    date::text,
                    COUNT(DISTINCT user_id)                  AS total_users,
                    COALESCE(SUM(searches), 0)               AS total_searches,
                    COALESCE(SUM(purchases), 0)              AS total_purchases,
                    COALESCE(SUM(total_purchased_amount), 0) AS total_purchased_amount
                FROM daily_user_stats
                WHERE date = %s
                GROUP BY date
                """,
                (date,),
            )
            row = cursor.fetchone()
    except Exception as e:

        logger.error(f"DB error on /daily_stats?date={date}: {e}")
        raise HTTPException(status_code=500, detail="Database error.")
    
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"No data found for date: {date}")

    return {
        "date": row[0],
        "total_users": row[1],
        "total_searches": row[2],
        "total_purchases": row[3],
        "total_purchased_amount": float(row[4]),
    }


@app.get("/daily_stats/breakdown")
def get_daily_stats_breakdown(date):
    """
    Return per-user stats for a given date.
    Useful for debugging; not required by the challenge spec.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, searches, purchases, total_purchased_amount
                FROM daily_user_stats
                WHERE date = %s
                ORDER BY user_id
                """,
                (date,),
            )
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"DB error on /daily_stats/breakdown?date={date}: {e}")
        raise HTTPException(status_code=500, detail="Database error.")
    finally:
        conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No data found for date: {date}")

    return {
        "date": date,
        "users": [
            {
                "user_id": user_id,
                "searches": searches,
                "purchases": purchases,
                "total_purchased_amount": float(amount),
            }
            for user_id, searches, purchases, amount in rows
        ],
    }


@app.post("/pipeline/run")
def trigger_pipeline(path):
    """Manually trigger a pipeline run against the given events file."""
    try:
        run_pipeline(path)
        return {"status": "ok", "message": f"Pipeline ran successfully on {path}."}
    except Exception as e:
        logger.error(f"Pipeline failed via API trigger: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}