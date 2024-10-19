# tests/setup_test_db.py

import psycopg
from psycopg import sql
import os
import dotenv

dotenv.load_dotenv()

# Use environment variables for connection parameters
DB_NAME = os.getenv('TEST_DB_NAME', 'test_db')
DB_USER = os.getenv('TEST_DB_USER', 'test_user')
DB_PASSWORD = os.getenv('TEST_DB_PASSWORD', 'test_password')
DB_HOST = os.getenv('TEST_DB_HOST', 'localhost')

def setup_test_db():
    # Connection parameters
    conn_params = {
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "host": DB_HOST
    }

    # Connect to the database
    with psycopg.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            # Read the SQL file
            with open('tests/setup_test_db.sql', 'r') as file:
                sql_script = file.read()

            # Execute the SQL script
            cur.execute(sql_script)

        # Commit the changes
        conn.commit()

    print("Test database setup completed successfully.")

if __name__ == "__main__":
    setup_test_db()