import psycopg2

conn = psycopg2.connect("postgresql://postgres:mypassword123@financialdb.<your-id>.us-east-1.rds.amazonaws.com:5432/financial_data")
print("Connection successful")
conn.close()
