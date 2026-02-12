"""
Nightly aggregation stub for dashboard metrics.

Run from cron or CI to produce daily aggregates used by dashboard endpoints.
This is a minimal, well-documented stub — replace DB connection details with app's DB settings or import the app's DB layer.
"""
from datetime import datetime, timedelta
from decimal import Decimal

def compute_aggregates(db_url: str = None, days: int = 7):
    """Compute simple daily aggregates for the last `days` days.

    This function is a stub. In production it should use the application's DB session
    and write results to a dedicated aggregates table.
    """
    # TODO: implement DB connection using SQLModel/SQLAlchemy and write aggregates
    end = datetime.utcnow().date()
    start = end - timedelta(days=days - 1)
    print(f"Computing aggregates from {start} to {end}")
    # Example aggregate record shape
    for day_offset in range(days):
        day = start + timedelta(days=day_offset)
        # TODO: run SQL queries to calculate tokens, cost, requests
        tokens = 0
        cost = Decimal("0.0")
        requests = 0
        print(f"{day.isoformat()}: tokens={tokens}, cost={cost}, requests={requests}")


if __name__ == "__main__":
    compute_aggregates()
