import sqlite3

def create_tables(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()

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

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_econ_date ON economic_indicators (Date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_yield_date ON yield_curve_prices (Date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prod_date ON production_data (Date)')

        print("Tables created successfully.")

def insert_business_cycle_data(db_name):
    """
    The business cycles below can be defined differently, for example NBER does not show that the economy was in recession in 2022
    Define or adjust this as you see fit. The code below is meant to offer one method of defining marcket cycles.
    """
    business_cycles = [
        {"peak": "1999-03-01", "trough": "2001-03-01", "start": "1999-03-01 00:00:00", "end": "2001-03-01 00:00:00", "phase": "Expansion"},
        {"peak": "2001-03-01", "trough": "2001-11-01", "start": "2001-03-01 00:00:00", "end": "2001-11-01 00:00:00", "phase": "Contraction"},
        {"peak": "2001-11-01", "trough": "2007-12-01", "start": "2001-11-01 00:00:00", "end": "2007-12-01 00:00:00", "phase": "Expansion"},
        {"peak": "2007-12-01", "trough": "2009-06-01", "start": "2007-12-01 00:00:00", "end": "2009-06-01 00:00:00", "phase": "Contraction"},
        {"peak": "2020-02-01", "trough": "2020-04-01", "start": "2009-06-01 00:00:00", "end": "2020-02-01 00:00:00", "phase": "Expansion"},
        {"peak": "2020-02-01", "trough": "2020-04-01", "start": "2020-02-01 00:00:00", "end": "2020-04-01 00:00:00", "phase": "Contraction"},
        {"peak": "2021-12-01", "trough": "2022-03-31", "start": "2020-04-01 00:00:00", "end": "2022-03-11 00:00:00", "phase": "Expansion"}
    ]
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        for cycle in business_cycles:
            cursor.execute('''
                INSERT INTO business_cycles (Peak_Month, Trough_Month, Start_Date, End_Date, Phase)
                VALUES (?, ?, ?, ?, ?)
            ''', (cycle["peak"], cycle["trough"], cycle["start"], cycle["end"], cycle["phase"]))
        print("Business cycle data inserted successfully.")

if __name__ == "__main__":
    db_name = "financial_data.db"
    create_tables(db_name)
    insert_business_cycle_data(db_name)