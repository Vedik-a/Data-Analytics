from sqlalchemy import create_engine
import pandas as pd

# ✅ Create SQLAlchemy engine
engine = create_engine('mysql+pymysql://root:pass%40ved07@localhost/myflights')

# 📂 Path to your CSV
csv_path = r'C:\ProgramData\MySQL\MySQL Server 8.0\Uploads\flights.csv'
chunksize = 100000  # Adjust as needed

# 🚀 Insert CSV data into MySQL table in chunks
for chunk in pd.read_csv(csv_path, chunksize=chunksize):
    chunk.replace("", pd.NA, inplace=True)  # Convert empty strings to NULL
    chunk.to_sql('flights', con=engine, if_exists='append', index=False)
    print(f"✅ Inserted {len(chunk)} rows")

