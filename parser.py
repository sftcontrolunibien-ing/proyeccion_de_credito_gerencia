import pandas as pd
from typing import List, Dict


class DynamicExcelParser:
    """Clase encargada de parsear e identificar tablas dinámicamente en el libro de Excel."""

    def __init__(self, file_path_or_buffer):
        self.file = file_path_or_buffer

    def parse_workbook(self) -> List[Dict]:
        all_records = []
        xl = pd.ExcelFile(self.file)

        # 1. Parsear Hoja "BASE DE DATOS"
        sheet1_name = [s for s in xl.sheet_names if "BASE DE DATOS" in s.upper()]
        if sheet1_name:
            df_bd = pd.read_excel(self.file, sheet_name=sheet1_name[0], header=None)
            all_records.extend(self._extract_tables_from_sheet_1(df_bd))

        # 2. Parsear Hoja "DECLINADOS - NO APROBADOS"
        sheet2_name = [s for s in xl.sheet_names if "DECLINADO" in s.upper()]
        if sheet2_name:
            df_dec = pd.read_excel(self.file, sheet_name=sheet2_name[0], header=None)
            all_records.extend(self._extract_table_from_sheet_2(df_dec))

        return all_records

    def _extract_tables_from_sheet_1(self, df: pd.DataFrame) -> List[Dict]:
        records = []
        header_indices = []

        # Buscar filas que parecen encabezados ("ID CLIENTE" o "CLIENTE")
        for idx, row in df.iterrows():
            row_vals = [str(val).strip().upper() for val in row.values if pd.notna(val)]
            if "ID CLIENTE" in row_vals or "CLIENTE" in row_vals:
                header_indices.append(idx)

        # Procesar bloques según los índices de encabezados detectados
        for i, header_idx in enumerate(header_indices):
            if i == 0:
                tabla_nombre = "BASE DE DATOS PRINCIPAL"
            elif i == 1:
                tabla_nombre = "LIQUIDADOS / INACTIVOS"
            else:
                tabla_nombre = "LEGAL"

            start_row = header_idx + 1
            end_row = header_indices[i + 1] if i + 1 < len(header_indices) else len(df)

            sub_df = df.iloc[start_row:end_row].copy()
            headers = self._resolve_duplicate_headers(df.iloc[header_idx].values)
            sub_df.columns = headers

            sub_df = sub_df.dropna(how='all')

            for row_num, row_data in sub_df.iterrows():
                if pd.isna(row_data.get("CLIENTE")) and pd.isna(row_data.get("ID CLIENTE")):
                    continue

                record = row_data.to_dict()
                record["_ORIGEN_TABLA"] = tabla_nombre
                record["_EXCEL_ROW"] = row_num + 1
                records.append(record)

        return records

    def _extract_table_from_sheet_2(self, df: pd.DataFrame) -> List[Dict]:
        records = []
        header_idx = None
        for idx, row in df.iterrows():
            row_vals = [str(val).strip().upper() for val in row.values if pd.notna(val)]
            if "ID CLIENTE" in row_vals or "CLIENTE" in row_vals:
                header_idx = idx
                break

        if header_idx is None:
            header_idx = 0

        sub_df = df.iloc[header_idx + 1:].copy()
        headers = self._resolve_duplicate_headers(df.iloc[header_idx].values)
        sub_df.columns = headers
        sub_df = sub_df.dropna(how='all')

        for row_num, row_data in sub_df.iterrows():
            if pd.isna(row_data.get("CLIENTE")) and pd.isna(row_data.get("ID CLIENTE")):
                continue
            record = row_data.to_dict()
            record["_ORIGEN_TABLA"] = "DECLINADOS - NO APROBADOS"
            record["_EXCEL_ROW"] = row_num + 1
            records.append(record)

        return records

    def _resolve_duplicate_headers(self, raw_headers: list) -> list:
        clean_headers = []
        seen = {}
        for idx, h in enumerate(raw_headers):
            name = str(h).strip().upper() if pd.notna(h) else f"COL_{idx}"

            if name == "TELEFONO" and len(clean_headers) > 0:
                prev = clean_headers[-1]
                if "ESPOSO" in prev or "PAREJA" in prev:
                    name = "TELEFONO_PAREJA"
                elif "ARRENDADOR" in prev:
                    name = "TELEFONO_ARRENDADOR"

            if name in seen:
                seen[name] += 1
                clean_headers.append(f"{name}_{seen[name]}")
            else:
                seen[name] = 0
                clean_headers.append(name)
        return clean_headers