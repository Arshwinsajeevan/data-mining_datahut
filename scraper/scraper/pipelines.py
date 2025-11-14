"""Pipeline that stores each scraped agent into a SQLite database."""

import os
import json
import sqlite3

class SQLiteStorePipeline:
    """
    Stores each scraped item in a SQLite database.

    Features:
    - Creates output/ folder automatically.
    - Ensures one unique row per profile_url.
    - Saves cleaned JSON into the `data` column.
    """

    def open_spider(self, spider):
        """Initialize the SQLite database when the spider starts."""
        os.makedirs("output", exist_ok=True)

        # Connect to database
        self.conn = sqlite3.connect("output/ewm_agents.db")
        self.cursor = self.conn.cursor()

        # Create table for agents
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT UNIQUE,
                data TEXT
            )
            """
        )
        self.conn.commit()

    def process_item(self, item, spider):
        """Insert or update a scraped item into SQLite."""
        profile_url = item.get("profile_url", "")
        item_json = json.dumps(dict(item), ensure_ascii=False)

        self.cursor.execute(
            """
            INSERT OR REPLACE INTO agents (profile_url, data)
            VALUES (?, ?)
            """,
            (profile_url, item_json),
        )
        self.conn.commit()

        return item

    def close_spider(self, spider):
        """Close the SQLite database connection when finished."""
        self.conn.close()