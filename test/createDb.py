import sqlite3
import random

def populate_locations(db_name, num_locations=10):
    """Populates a locations table with random city, country pairs."""

    cities = ["New York", "London", "Tokyo", "Paris", "Sydney", "Berlin", "Rome", "Madrid", "Toronto", "Mumbai", "Cairo", "Rio de Janeiro", "Beijing", "Amsterdam", "Stockholm"]
    countries = ["USA", "UK", "Japan", "France", "Australia", "Germany", "Italy", "Spain", "Canada", "India", "Egypt", "Brazil", "China", "Netherlands", "Sweden"]

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create the locations table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL
            )
        ''')

        # Generate and insert random locations
        for _ in range(num_locations):
            city = random.choice(cities)
            country = random.choice(countries)
            location = f"{city}, {country}"
            cursor.execute("INSERT INTO locations (location) VALUES (?)", (location,))

        conn.commit()
        print(f"{num_locations} random locations inserted into the 'locations' table.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_name = "../comp-dir.db" # Change this if needed.
    populate_locations(db_name)