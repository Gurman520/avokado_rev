"""
Скрипт миграции базы данных на новую версию.
Запускать из корня проекта: python migrate_db.py
"""
import sqlite3

DB_PATH = "contracts.db"  # путь к вашей базе

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица customers
    cursor.execute("PRAGMA table_info(customers)")
    cols = [col[1] for col in cursor.fetchall()]
    if "postal_address" not in cols:
        cursor.execute("ALTER TABLE customers ADD COLUMN postal_address TEXT")
    if "corr_account" not in cols:
        cursor.execute("ALTER TABLE customers ADD COLUMN corr_account TEXT")
    if "email" not in cols:
        cursor.execute("ALTER TABLE customers ADD COLUMN email TEXT")
    if "type" not in cols:
        cursor.execute("ALTER TABLE customers ADD COLUMN type TEXT DEFAULT 'legal'")
        cursor.execute("UPDATE customers SET type = 'legal'")

    # Таблица users (профиль)
    cursor.execute("PRAGMA table_info(users)")
    cols = [col[1] for col in cursor.fetchall()]
    if "corr_account" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN corr_account TEXT")
    if "snils" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN snils TEXT")
    if "email" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "passport" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN passport TEXT")

    # Таблица contracts
    cursor.execute("PRAGMA table_info(contracts)")
    cols = [col[1] for col in cursor.fetchall()]
    if "file_path" not in cols:
        cursor.execute("ALTER TABLE contracts ADD COLUMN file_path TEXT")

    # Таблица cheques
    cursor.execute("PRAGMA table_info(cheques)")
    cols = [col[1] for col in cursor.fetchall()]
    if "act_id" not in cols:
        cursor.execute("ALTER TABLE cheques ADD COLUMN act_id INTEGER REFERENCES acts(id)")

    # Таблица acts
    cursor.execute("PRAGMA table_info(acts)")
    cols = [col[1] for col in cursor.fetchall()]
    if "customer_id" not in cols:
        cursor.execute("ALTER TABLE acts ADD COLUMN customer_id INTEGER REFERENCES customers(id)")

    conn.commit()
    conn.close()
    print("Миграция успешно завершена.")

if __name__ == "__main__":
    migrate()