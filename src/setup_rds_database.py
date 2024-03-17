import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    db_uri = os.getenv('DATABASE_URI')

    try:
        conn = psycopg2.connect(db_uri)
        cursor = conn.cursor()

        # Drop existing tables first if necessary
        cursor.execute('DROP TABLE IF EXISTS economic_indicators, yield_curve_prices, production_data, business_cycles;')

        # Create economic indicators table with uppercase column names
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economic_indicators (
                "Date" DATE PRIMARY KEY,
                "UNRATE" REAL,
                "PAYEMS" REAL,
                "ICSA" REAL,
                "CIVPART" REAL,
                "INDPRO" REAL
            )
        ''')

        # Create yield_curve_prices table with uppercase column names
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS yield_curve_prices (
                "Date" DATE PRIMARY KEY,
                "DGS1MO" REAL,
                "DGS3MO" REAL,
                "DGS6MO" REAL,
                "DGS1" REAL,
                "DGS2" REAL,
                "DGS3" REAL,
                "DGS5" REAL,
                "DGS7" REAL,
                "DGS10" REAL,
                "DGS20" REAL,
                "DGS30" REAL
            )
        ''')

        # Create production_data table with uppercase column names
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_data (
                "Date" DATE PRIMARY KEY,
                "SAUNGDPMOMBD" REAL,
                "ARENGDPMOMBD" REAL,
                "IRNNGDPMOMBD" REAL,
                "SAUNXGO" REAL,
                "QATNGDPMOMBD" REAL,
                "KAZNGDPMOMBD" REAL,
                "IRQNXGO" REAL,
                "IRNNXGO" REAL,
                "KWTNGDPMOMBD" REAL,
                "IPN213111S" REAL,
                "PCU213111213111" REAL,
                "DPCCRV1Q225SBEA" REAL
            )
        ''')

        # Create business_cycles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_cycles (
                "id" SERIAL PRIMARY KEY,
                "Peak_Month" TEXT,
                "Trough_Month" TEXT,
                "Start_Date" DATE,
                "End_Date" DATE,
                "Phase" TEXT
            )
        ''')

        # Add indexes on date columns
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_econ_date ON economic_indicators ("Date")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_yield_date ON yield_curve_prices ("Date")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prod_date ON production_data ("Date")')

        cursor.close()
        conn.commit()
        conn.close()
        print("Tables and indexes created successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_tables()
