import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_uri = os.getenv('DATABASE_URI')

try:
    # Connect to the database
    with psycopg2.connect(db_uri) as conn:
        with conn.cursor() as cursor:
            # Query for a date range
            query = '''SELECT * FROM yield_curve_prices Limit 50;'''
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No data found for the specified date range.")
except Exception as e:
    print(f"Error: {e}")
