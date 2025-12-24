import psycopg2
from config import DB_CONFIG

class UserMarkersDB:
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

    def save_marker_state(self, chat_id, marker_name, marker_type, selected):
        """
        Сохраняет состояние маркера БЕЗ серий
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_markers (
                    chat_id, marker_name, marker_type, marker_series, selected
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (chat_id, marker_name, marker_series)
                DO UPDATE SET selected = EXCLUDED.selected
            """, (chat_id, marker_name, marker_type, "", selected))

    def load_marker_state(self, chat_id):
        """
        Загружает состояние маркера {marker_name: bool}
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT marker_name, selected
                FROM user_markers
                WHERE chat_id = %s
                  AND marker_series = %s
            """, (chat_id, ""))
            return {name: sel for name, sel in cur.fetchall()}


    def save_marker_series(self, chat_id, marker_name, marker_type, series, selected):
        """
        Сохраняет состояние конкретной серии Languo
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_markers (
                    chat_id, marker_name, marker_type, marker_series, selected
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (chat_id, marker_name, marker_series)
                DO UPDATE SET selected = EXCLUDED.selected
            """, (chat_id, marker_name, marker_type, series, selected))

    def load_marker_series(self, chat_id, marker_name="Languo Series"):
        """
        Возвращает {series_name: bool}
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT marker_series, selected
                FROM user_markers
                WHERE chat_id = %s
                  AND marker_name = %s
                  AND marker_series IS NOT NULL
            """, (chat_id, marker_name))

            return {series: sel for series, sel in cur.fetchall()}

    def has_selected_series(self, chat_id, marker_name="Languo Series"):
        """
        True, если у маркера выбрана хотя бы одна серия
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 1
                FROM user_markers
                WHERE chat_id = %s
                  AND marker_name = %s
                  AND marker_series != %s
                  AND selected = TRUE
                LIMIT 1
            """, (chat_id, marker_name, ""))

            return cur.fetchone() is not None
