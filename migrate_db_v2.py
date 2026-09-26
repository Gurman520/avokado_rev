"""Миграция: добавление total_amount в acts."""
import sqlite3

DB_PATH = "contracts.db"


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # acts.total_amount
    cursor.execute("PRAGMA table_info(acts)")
    cols = [c[1] for c in cursor.fetchall()]
    if "total_amount" not in cols:
        cursor.execute("ALTER TABLE acts ADD COLUMN total_amount REAL")
        print("Добавлено: acts.total_amount")

    conn.commit()
    conn.close()
    print("Миграция v2 завершена.")


if __name__ == "__main__":
    migrate()