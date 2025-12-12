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
        """Сохраняем выбор маркера, если есть — обновляем selected"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_markers (chat_id, marker_name, marker_type, selected)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chat_id, marker_name)
                DO UPDATE SET selected = EXCLUDED.selected
            """, (chat_id, marker_name, marker_type, selected))


    def load_marker_state(self, chat_id):
        """Возвращает словарь {marker_name: True/False}"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT marker_name, selected
                FROM user_markers
                WHERE chat_id = %s
            """, (chat_id,))
            return {name: sel for name, sel in cur.fetchall()}

    def get_user_markers(self, chat_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT marker_name, marker_type, selected FROM user_markers WHERE chat_id=%s", (chat_id,))
            return cur.fetchall()
