# user_state.py
import psycopg2
import json
from config import DB_CONFIG
import psycopg2.extras

class UserStateDB:
    def __init__(self):
        cfg = DB_CONFIG
        self.conn = psycopg2.connect(
            dbname=cfg["dbname"],
            user=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"]
        )
        self.conn.autocommit = True

    def save_state(self, chat_id, state, book=None, page=None):
        """Сохраняем или обновляем состояние пользователя"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_state (chat_id, state, book, page)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE
                SET state = EXCLUDED.state,
                    book = EXCLUDED.book,
                    page = EXCLUDED.page
                """,
                (chat_id, state, book, page)
            )

    def load_state(self, chat_id):
        """Загружаем состояние пользователя"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT state, book, page FROM user_state WHERE chat_id = %s", (chat_id,))
            row = cur.fetchone()
            if row:
                return {"state": row[0], "book": row[1], "page": row[2]}
            return None

    def delete_state(self, chat_id):
        """Удаляем состояние пользователя"""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM user_state WHERE chat_id = %s", (chat_id,))

    def get_markers(self, user_id: int):
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT markers FROM user_state WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if not row or row["markers"] is None:
                return []
            return row["markers"]  # это уже list

    def set_markers(self, user_id: int, markers: list):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE user_state SET markers = %s WHERE user_id = %s",
                (json.dumps(markers), user_id),
            )