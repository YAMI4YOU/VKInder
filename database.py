import sqlite3
from os import path, mkdir


db_path = path.join(f"{path.abspath('db')}", "vkinder.db")

def create_folder() -> None:
    """Создаёт папку для БД"""
    if not path.isdir("db"):
        mkdir("db")

def create_database() -> None:
    create_folder()
    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS couple(
            id INTEGER PRIMARY KEY,
            black_listed INTEGER,
            favorite INTEGET
        );
        """)
        conn.commit()

def check_pair_exist(couple_id: int) -> bool:

    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT id FROM couple WHERE id = ?;
        """, (couple_id,))
        if cur.fetchone() is None:
            return False
        return True

def add_pair(couple_id: int) -> None:

    with sqlite3.connect(f"{db_path}") as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO couple(id)
        VALUES (?);
        """, (couple_id,))
        conn.commit()




