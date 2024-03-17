import pandas as pd
import pandas_datareader.data as web
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DataLoader:
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.economic_indicators_tickers = ['UNRATE', 'PAYEMS', 'ICSA', 'CIVPART', 'INDPRO']
        self.yield_curve_tickers = ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', 'DGS30']
        self.production_data_tickers = ['SAUNGDPMOMBD', 'ARENGDPMOMBD', 'IRNNGDPMOMBD', 'SAUNXGO', 'DPCCRV1Q225SBEA',
                                        'QATNGDPMOMBD', 'KAZNGDPMOMBD', 'IRQNXGO', 'IRNNXGO', 'KWTNGDPMOMBD', 'IPN213111S', 'PCU213111213111']

    def fetch_and_insert_data(self, tickers, table_name):
        start_date = '2008-12-31'
        end_date = datetime.now().strftime('%Y-%m-%d')
        try:
            data = web.DataReader(tickers, 'fred', start_date, end_date)
            data = data.interpolate(method='quadratic').bfill().ffill()
            data = data.resample('D').ffill().bfill()

            # Convert the index (which is the date) to the correct format
            data.index = pd.to_datetime(data.index).strftime('%Y-%m-%d')

            engine = create_engine(self.db_uri)
            # Ensure index_label matches the uppercase column name in your schema
            data.to_sql(table_name, engine, if_exists='replace', index_label='Date')
            print(f"Data inserted into {table_name} table successfully.")
        except Exception as e:
            print(f"Failed to fetch and insert the data: {e}")

def main():
    db_uri = os.getenv('DATABASE_URI')
    loader = DataLoader(db_uri)
    loader.fetch_and_insert_data(loader.economic_indicators_tickers, 'economic_indicators')
    loader.fetch_and_insert_data(loader.yield_curve_tickers, 'yield_curve_prices')
    loader.fetch_and_insert_data(loader.production_data_tickers, 'production_data')

if __name__ == "__main__":
    main()
