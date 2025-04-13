# Importar librerías necesarias
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import plotly.express as px
import io
import xlsxwriter

# Título principal
st.title("💰 Finanzas Personales")

# Conexión a Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(credentials)
sheet = client.open("finanzas-personales").worksheet("Hoja1")

datos = sheet.get_all_records()
df = pd.DataFrame(datos)
df.columns = df.columns.str.lower()

# Mostrar datos actuales
st.subheader("📋 Movimientos actuales")
st.dataframe(df)

# =============================
# SECCIÓN: ELIMINAR MOVIMIENTOS
# =============================
st.subheader("🗑 Eliminar movimientos")

# Creamos el estado inicial para los checkboxes si no existe
definir_claves_checkboxes = "checkboxes" not in st.session_state
if definir_claves_checkboxes:
    st.session_state.checkboxes = {}

# Mostramos un resumen por fila con checkbox para marcar
st.caption("Selecciona los movimientos que deseas eliminar:")

# Recorremos cada fila del DataFrame y creamos un checkbox único
for idx, row in df.iterrows():
    checkbox_key = f"del_{idx}"

    # Mostramos cada movimiento como una línea con resumen e ID
    seleccionado = st.checkbox(
        f"{row['Fecha']} - {row['Tipo']} - ${row['Monto']} - {row['Categoría']}",
        key=checkbox_key
    )

    # Guardamos el estado actual del checkbox en session_state
    st.session_state.checkboxes[checkbox_key] = seleccionado

# ==================================
# GRÁFICO DE BARRAS: INGRESOS/GASTOS
# ==================================
df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0)
resumen_mensual = df.groupby(['mes', 'tipo'])['monto'].sum().reset_index()
st.subheader("📊 Ingresos vs Gastos por mes")
fig_bar = px.bar(
    resumen_mensual,
    x='mes',
    y='monto',
    color='tipo',
    barmode='group',
    text_auto='.2s',
    labels={'monto': 'Total', 'mes': 'Mes'}
)
st.plotly_chart(fig_bar, use_container_width=True)

# ===============================
# GRÁFICO CIRCULAR DE CATEGORÍAS
# ===============================
df_gastos = df[df['tipo'] == 'Gasto']
if 'categoria' in df_gastos.columns and not df_gastos['categoria'].isna().all():
    gastos_categoria = df_gastos.groupby('categoria')['monto'].sum().reset_index()
    if not gastos_categoria.empty:
        st.subheader("🍕 Distribución de gastos por categoría")
        fig_pie = px.pie(
            gastos_categoria,
            values='monto',
            names='categoria',
            title='Distribución porcentual por categoría',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("⚠️ No hay montos válidos para las categorías.")
else:
    st.info("⚠️ No se encontraron categorías válidas para mostrar el gráfico.")

# ==============================
# EXPORTAR MOVIMIENTOS A EXCEL
# ==============================
st.subheader("📥 Exportar movimientos a Excel")
if not df.empty:
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Movimientos')
    writer.close()
    output.seek(0)
    st.download_button(
        label="📤 Descargar archivo Excel",
        data=output,
        file_name="finanzas_personales.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("⚠️ No hay datos disponibles para exportar.")

# ============================
# FORMULARIO PARA NUEVO GASTO
# ============================
st.subheader("➕ Añadir nuevo movimiento")
fecha = st.date_input("Fecha:", datetime.today())
mes = fecha.strftime("%B")
tipo = st.selectbox("Tipo:", ["Ingreso", "Gasto"])
categoria = st.text_input("Categoría:")
concepto = st.text_input("Concepto:")
monto = st.number_input("Monto:", min_value=0.0, step=1.0)
forma_pago = st.selectbox("Forma de Pago:", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])
nota = st.text_area("Nota (opcional):")

if st.button("Guardar movimiento 💾"):
    nueva_fila = [str(fecha), mes, tipo, categoria, concepto, monto, forma_pago, nota]
    sheet.append_row(nueva_fila)
    st.success("✅ Movimiento guardado correctamente.")
    st.experimental_rerun()
