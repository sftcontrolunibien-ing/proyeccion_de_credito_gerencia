import sqlite3
import json
import pandas as pd
from typing import List, Dict


class DatabaseRepository:
    """Capa de persistencia SQLite local."""

    def __init__(self, db_path: str = "local_database.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS clientes_records
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               origen_tabla
                               TEXT,
                               excel_row
                               INTEGER,
                               estatus
                               TEXT,
                               grupo
                               TEXT,
                               comentario
                               TEXT,
                               cliente_nombre
                               TEXT,
                               data_json
                               TEXT
                           )
                           """)
            conn.commit()

    def clear_database(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM clientes_records")
            conn.commit()

    def save_records(self, records: List[Dict]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for r in records:
                origen = r.get("_ORIGEN_TABLA", "DESCONOCIDO")
                row_idx = r.get("_EXCEL_ROW", 0)
                estatus = str(r.get("ESTATUS", "")).strip()
                grupo = str(r.get("GRUPO", "")).strip()
                comentario = str(r.get("COMENTARIO", "")).strip()
                cliente = str(r.get("CLIENTE", "")).strip()

                clean_r = {str(k): str(v) for k, v in r.items() if pd.notna(v)}

                cursor.execute("""
                               INSERT INTO clientes_records (origen_tabla, excel_row, estatus, grupo, comentario,
                                                             cliente_nombre, data_json)
                               VALUES (?, ?, ?, ?, ?, ?, ?)
                               """, (origen, row_idx, estatus, grupo, comentario, cliente,
                                     json.dumps(clean_r, ensure_ascii=False)))
            conn.commit()

    def sync_from_excel(self, records: List[Dict]):
        self.clear_database()
        self.save_records(records)

    def count_records(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clientes_records")
            return cursor.fetchone()[0]

    def fetch_all(self) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, origen_tabla, excel_row, estatus, grupo, comentario, data_json FROM clientes_records")
            rows = cursor.fetchall()
            result = []
            for r in rows:
                item = json.loads(r[6])
                item["_ID_LOCAL"] = r[0]
                item["_ORIGEN_TABLA"] = r[1]
                item["_EXCEL_ROW"] = r[2]
                item["ESTATUS"] = r[3]
                item["GRUPO"] = r[4]
                item["COMENTARIO"] = r[5]
                result.append(item)
            return result