import sqlite3

def add_column_to_database():
    conn = sqlite3.connect("translations.db")
    cursor = conn.cursor()

    # Add the new column (japanese_grammar)
    cursor.execute("ALTER TABLE translations ADD COLUMN japanese_grammar TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column_to_database()

