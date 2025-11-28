Project Structure

cricbuzz_livestats/
│
├─ app.py                 # Main application file
├─ data_ingestion.py      # Script to insert/update data in the database
│
├─ pages/                 # All web page logic
│   ├─ home.py
│   ├─ live_matches.py
│   ├─ top_stats.py
│   ├─ crud_operations.py
│   └─ sql_queries.py
│
├─ utils/
│   └─ db_connection.py   # Database connection helper
│
└─ notebooks/
    └─ data_fetching.ipynb  # Notebook for fetching data


requirements.txt

If the repository does not include requirements.txt, generate it after installing libs