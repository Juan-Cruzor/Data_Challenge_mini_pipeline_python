from psycopg2.extras import execute_values


def insert_metrics(cursor,rows):
    """Function that writes the computed metrics into the daily_user_stats table.
        It uses the execute_values method for efficient batch insertion and handles
        conflicts by updating existing records with the new metrics.

        date and user_id are the unique key (so one row per user per day).
        If a row already exists with the same date and user_id, instead of failing:
        It updates searches, purchases, and total_purchased_amount with the new values.
            
            Args:
                cursor: The database cursor to execute the query.
                rows[tuple]: A list of tuples containing the metrics to be inserted.
                    
                    returns: None if there're not rows to insert."""

    if not rows:
        return

    execute_values(
        cursor,
        """
        INSERT INTO daily_user_stats
        (date,user_id,searches,purchases,total_purchased_amount)
        VALUES %s
        ON CONFLICT (date,user_id)
        DO UPDATE SET
            searches = EXCLUDED.searches,
            purchases = EXCLUDED.purchases,
            total_purchased_amount = EXCLUDED.total_purchased_amount
        """,
        rows
    )