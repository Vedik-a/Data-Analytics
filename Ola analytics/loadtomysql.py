import pandas as pd
from sqlalchemy import create_engine
df = pd.read_excel(r"C:\Users\vedik\Downloads\OLA_DataSet_Cleaned.xlsx", sheet_name="Sheet1")


# MySQL credentials
user = "root"
password = "abc"
host = "localhost"
database = "olaa"

# Create connection (note the %40 for @)
engine = create_engine("mysql+mysqlconnector://root:abc@localhost:3306/olaa")

# Store DataFrame in MySQL
df.to_sql("ola_july_cleaned", con=engine, if_exists="replace", index=False)

print("✅ Data successfully stored in MySQL table: ola_july_cleaned")
