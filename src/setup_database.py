import sqlite3

def create_tables(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

        # Create economic indicators table with consistent date column name
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economic_indicators (
                Date TEXT PRIMARY KEY,
                UNRATE REAL,
                PAYEMS REAL,
                ICSA REAL,
                CIVPART REAL,
                INDPRO REAL
            )
        ''')

        # Create yield_curve_prices table with consistent date column name
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS yield_curve_prices (
                Date TEXT PRIMARY KEY,
                DGS1MO REAL,
                DGS3MO REAL,
                DGS6MO REAL,
                DGS1 REAL,
                DGS2 REAL,
                DGS3 REAL,
                DGS5 REAL,
                DGS7 REAL,
                DGS10 REAL,
                DGS20 REAL,
                DGS30 REAL
            )
        ''')

        # Create production_data table with consistent date column name
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_data (
                Date TEXT PRIMARY KEY,
                SAUNGDPMOMBD REAL,
                ARENGDPMOMBD REAL,
                IRNNGDPMOMBD REAL,
                SAUNXGO REAL,
                QATNGDPMOMBD REAL,
                KAZNGDPMOMBD REAL,
                IRQNXGO REAL,
                IRNNXGO REAL,
                KWTNGDPMOMBD REAL,
                IPN213111S REAL,
                PCU213111213111 REAL,
                DPCCRV1Q225SBEA REAL
            )
        ''')

        # Create business_cycles table with an auto-increment ID as the primary key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Peak_Month TEXT,
                Trough_Month TEXT,
                Start_Date TEXT,
                End_Date TEXT,
                Phase TEXT
            )
        ''')

        # Optionally, add indexes on date columns if they will be used in joins or queries often
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_econ_date ON economic_indicators (Date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_yield_date ON yield_curve_prices (Date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prod_date ON production_data (Date)')

        print("Tables created successfully.")

if __name__ == "__main__":
    create_tables("financial_data.db")