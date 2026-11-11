from typing import Dict, List


class ValidationEngine:
    """Motor de búsqueda cruzada con soporte de coincidencia parcial y generación de dictamen."""

    def __init__(self, db_repository):
        self.db_repo = db_repository

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        return str(text).strip().upper()

    def _generar_redaccion(self, entidad_input: str, valor_ingresado: str, cliente_bd: str,
                           columna: str, celda_valor: str, tabla: str, fila: int,
                           grupo: str, estatus: str) -> str:
        """Genera una explicación en lenguaje natural para la Mesa de Control."""
        return (
            f"El valor '{valor_ingresado}' capturado en el campo [{entidad_input}] "
            f"se encontró contenido dentro de la celda de la columna [{columna}] "
            f"(Valor registrado: '{celda_valor}') en la tabla [{tabla}], Fila Excel #{fila}. "
            f"Corresponde al registro del cliente '{cliente_bd}' (Grupo: {grupo}), "
            f"el cual registra actualmente un ESTATUS de '{estatus}'."
        )

    def validate_prospect(self, applicant_data: Dict[str, str]) -> List[Dict]:
        all_records = self.db_repo.fetch_all()
        coincidencias = []

        # Normalizar datos ingresados en el formulario
        inputs_to_check = {}
        for entity_label, value in applicant_data.items():
            norm_val = self._normalize(value)
            if norm_val and len(norm_val) >= 2:  # Mínimo 2 caracteres para evitar falsos positivos masivos
                inputs_to_check[entity_label] = norm_val

        for rec in all_records:
            tabla = rec.get("_ORIGEN_TABLA", "Desconocida")
            fila_excel = rec.get("_EXCEL_ROW", "N/A")
            estatus = str(rec.get("ESTATUS", "SIN ESTATUS")).strip()
            grupo = str(rec.get("GRUPO", "SIN GRUPO")).strip()
            cliente_nombre_bd = str(rec.get("CLIENTE", rec.get("cliente_nombre", "DESCONOCIDO"))).strip()
            comentario = str(rec.get("COMENTARIO", "Sin comentarios")).strip()
            id_cliente = rec.get("ID CLIENTE", rec.get("_ID_LOCAL", "N/A"))

            # Recorrer todas las columnas de la fila actual
            for col_name, cell_value in rec.items():
                if col_name.startswith("_"):
                    continue

                cell_val_norm = self._normalize(cell_value)
                if not cell_val_norm:
                    continue

                for entity_key, input_val in inputs_to_check.items():
                    # Coincidencia parcial (subcadena): el valor ingresado está contenido en la celda
                    if input_val in cell_val_norm:
                        celda_ubicacion = f"Tabla: '{tabla}' | Columna: '{col_name}' | Fila Excel: #{fila_excel}"

                        explicacion = self._generar_redaccion(
                            entidad_input=entity_key,
                            valor_ingresado=input_val,
                            cliente_bd=cliente_nombre_bd,
                            columna=col_name,
                            celda_valor=cell_val_norm,
                            tabla=tabla,
                            fila=fila_excel,
                            grupo=grupo,
                            estatus=estatus
                        )

                        coincidencias.append({
                            "Entidad Consultada": entity_key,
                            "Valor Ingresado": input_val,
                            "Cliente Coincidente": cliente_nombre_bd,
                            "Grupo": grupo,
                            "Estatus": estatus,
                            "Ubicación de Celda": celda_ubicacion,
                            "Tabla": tabla,
                            "Columna": col_name,
                            "Fila Excel": fila_excel,
                            "Contenido Celda BD": cell_val_norm,
                            "ID Cliente BD": id_cliente,
                            "Comentario": comentario,
                            "Explicación": explicacion
                        })

        return coincidencias