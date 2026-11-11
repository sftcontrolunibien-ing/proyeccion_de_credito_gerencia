import streamlit as st
import pandas as pd
from parser import DynamicExcelParser
from database import DatabaseRepository
from validator import ValidationEngine

# Configuración de página
st.set_page_config(
    page_title="Mesa de Control - Validación de Prospectos",
    page_icon="🔍",
    layout="wide"
)

db_repo = DatabaseRepository()
validator = ValidationEngine(db_repo)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Base de Datos Local")
    total_records = db_repo.count_records()
    st.metric(label="Registros cargados", value=f"{total_records:,}")

    st.divider()
    st.subheader("📤 Cargar / Actualizar Excel")
    uploaded_file = st.file_uploader("Selecciona el archivo Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        if st.button("Sincronizar y Reescribir BD", use_container_width=True, type="primary"):
            with st.spinner("Leyendo hojas y tablas..."):
                try:
                    parser = DynamicExcelParser(uploaded_file)
                    records = parser.parse_workbook()
                    db_repo.sync_from_excel(records)
                    st.success(f"✓ Base de datos actualizada ({len(records):,} registros).")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al procesar archivo: {e}")

    st.divider()
    if st.button("🗑️ Vaciar BD Local", use_container_width=True):
        db_repo.clear_database()
        st.warning("Base de datos borrada.")
        st.rerun()

# --- ENCABEZADO ---
st.title("🔍 Sistema de Consulta Automática de Prospectos")
st.caption("Búsqueda dinámica por coincidencia parcial en datos de Clientes, Referencias, Cónyuge y Arrendador.")

if total_records == 0:
    st.info("ℹ️ La base de datos está vacía. Carga un archivo Excel desde la barra lateral para habilitar la consulta.")

# --- FORMULARIO DE CONSULTA ---
st.subheader("📋 Datos a Validar del Nuevo Prospecto")

with st.form("prospect_form"):
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Cliente",
        "👨‍👩‍👧 Referencias Familiares",
        "🤝 Referencias Personales",
        "🏠 Cónyuge y Arrendador"
    ])

    with tab1:
        col1, col2, col3 = st.columns(3)
        cliente_nombre = col1.text_input("Nombre / Apellidos del Cliente", key="c_nom")
        cliente_tel = col2.text_input("Teléfono(s) del Cliente", key="c_tel")
        cliente_dom = col3.text_input("Domicilio (INE / Comprobante)", key="c_dom")

    with tab2:
        st.markdown("**Referencia Familiar 1**")
        c1, c2, c3 = st.columns(3)
        ref_fam1_nom = c1.text_input("Nombre Ref. Fam 1", key="rf1_n")
        ref_fam1_tel = c2.text_input("Teléfono Ref. Fam 1", key="rf1_t")
        ref_fam1_dom = c3.text_input("Domicilio Ref. Fam 1", key="rf1_d")

        st.markdown("**Referencia Familiar 2**")
        c4, c5, c6 = st.columns(3)
        ref_fam2_nom = c4.text_input("Nombre Ref. Fam 2", key="rf2_n")
        ref_fam2_tel = c5.text_input("Teléfono Ref. Fam 2", key="rf2_t")
        ref_fam2_dom = c6.text_input("Domicilio Ref. Fam 2", key="rf2_d")

    with tab3:
        st.markdown("**Referencia Personal 1**")
        c1, c2, c3 = st.columns(3)
        ref_per1_nom = c1.text_input("Nombre Ref. Per 1", key="rp1_n")
        ref_per1_tel = c2.text_input("Teléfono Ref. Per 1", key="rp1_t")
        ref_per1_dom = c3.text_input("Domicilio Ref. Per 1", key="rp1_d")

        st.markdown("**Referencia Personal 2**")
        c4, c5, c6 = st.columns(3)
        ref_per2_nom = c4.text_input("Nombre Ref. Per 2", key="rp2_n")
        ref_per2_tel = c5.text_input("Teléfono Ref. Per 2", key="rp2_t")
        ref_per2_dom = c6.text_input("Domicilio Ref. Per 2", key="rp2_d")

    with tab4:
        col_c, col_a = st.columns(2)
        with col_c:
            st.markdown("**Cónyuge / Pareja**")
            conyuge_nom = st.text_input("Nombre Cónyuge", key="cy_n")
            conyuge_tel = st.text_input("Teléfono Cónyuge", key="cy_t")
        with col_a:
            st.markdown("**Arrendador**")
            arrendador_nom = st.text_input("Nombre Arrendador", key="ar_n")
            arrendador_tel = st.text_input("Teléfono Arrendador", key="ar_t")

    submit_button = st.form_submit_button("🔎 Ejecutar Consulta Automática", type="primary", use_container_width=True)

# --- PROCESAMIENTO Y DICTAMEN ---
if submit_button:
    applicant_payload = {
        "Cliente - Nombre": cliente_nombre,
        "Cliente - Teléfono": cliente_tel,
        "Cliente - Domicilio": cliente_dom,
        "Ref. Fam 1 - Nombre": ref_fam1_nom,
        "Ref. Fam 1 - Teléfono": ref_fam1_tel,
        "Ref. Fam 1 - Domicilio": ref_fam1_dom,
        "Ref. Fam 2 - Nombre": ref_fam2_nom,
        "Ref. Fam 2 - Teléfono": ref_fam2_tel,
        "Ref. Fam 2 - Domicilio": ref_fam2_dom,
        "Ref. Per 1 - Nombre": ref_per1_nom,
        "Ref. Per 1 - Teléfono": ref_per1_tel,
        "Ref. Per 1 - Domicilio": ref_per1_dom,
        "Ref. Per 2 - Nombre": ref_per2_nom,
        "Ref. Per 2 - Teléfono": ref_per2_tel,
        "Ref. Per 2 - Domicilio": ref_per2_dom,
        "Cónyuge - Nombre": conyuge_nom,
        "Cónyuge - Teléfono": conyuge_tel,
        "Arrendador - Nombre": arrendador_nom,
        "Arrendador - Teléfono": arrendador_tel
    }

    with st.spinner("Escaneando registros en base de datos..."):
        coincidencias = validator.validate_prospect(applicant_payload)

    st.divider()
    st.subheader("📊 Dictamen de Validación")

    if not coincidencias:
        st.success(
            "✅ **APROBADO SIN REGISTROS:** El prospecto y sus contactos no registran ninguna coincidencia en las tablas analizadas.")
    else:
        st.error(
            f"⚠️ **ATENCIÓN - COINCIDENCIAS DETECTADAS:** Se identificaron **{len(coincidencias)}** coincidencia(s) en la base de datos.")

        # Tabla resumen interactiva
        df_display = pd.DataFrame(coincidencias)
        cols_summary = [
            "Entidad Consultada", "Valor Ingresado", "Cliente Coincidente",
            "Grupo", "Estatus", "Ubicación de Celda"
        ]

        st.markdown("##### 📌 Tabla Resumen de Hallazgos")
        st.dataframe(df_display[cols_summary], use_container_width=True)

        # Redacción explicativa detallada por coincidencia
        st.markdown("##### 📄 Redacción Explicativa Detallada por Coincidencia")
        for idx, match in enumerate(coincidencias, 1):
            titulo_expander = f"Hallazgo #{idx}: {match['Entidad Consultada']} ('{match['Valor Ingresado']}') ➔ Cliente en BD: {match['Cliente Coincidente']}"
            with st.expander(titulo_expander, expanded=True):
                st.info(f"**Explicación:** {match['Explicación']}")

                c_a, c_b, c_c = st.columns(3)
                c_a.write(f"**Cliente Registrado:** {match['Cliente Coincidente']}")
                c_b.write(f"**Grupo:** {match['Grupo']}")
                c_c.write(f"**Estatus:** `{match['Estatus']}`")

                c_d, c_e = st.columns(2)
                c_d.write(f"**Ubicación Celda:** {match['Ubicación de Celda']}")
                c_e.write(f"**Valor Completo en Celda:** `{match['Contenido Celda BD']}`")

                if match['Comentario']:
                    st.caption(f"💬 **Comentario registrado en BD:** {match['Comentario']}")