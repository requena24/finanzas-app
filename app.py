# Importar librerías necesarias
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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
sheet_wallet = client.open("finanzas-personales").worksheet("Wallet")

# Cargar datos
datos = sheet.get_all_records()
df = pd.DataFrame(datos)
df.columns = [str(col).lower() for col in df.columns]

# Tabs para organizar secciones
secciones = st.tabs(["📋 Movimientos", "➕ Agregar movimiento", "📑 Formas de pago", "💳 Wallet", "📊 Gráficos", "🗑 Eliminar"])

# ============================
# TAB 3: FORMAS DE PAGO Y TARJETAS
# ============================
with secciones[2]:
    st.subheader("📑 Análisis por forma de pago y tarjetas")

    st.markdown("### 💳 Gastos por forma de pago")
    if not df.empty and 'monto' in df.columns and 'forma de pago' in df.columns:
        df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0)
        resumen_pago = df[df['tipo'] == 'Gasto'].groupby('forma de pago')['monto'].sum().reset_index()
        resumen_pago.columns = ['Forma de pago', 'Total gastado']
        st.dataframe(resumen_pago, use_container_width=True, hide_index=True)

    st.markdown("### 🧾 Gastos por tarjeta (con rango de fechas)")
    if 'fecha' in df.columns and 'monto' in df.columns and 'forma de pago' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
        tarjetas_unicas = df[df['forma de pago'].isin(sheet_wallet.col_values(1)[1:])]['forma de pago'].unique().tolist()

        fecha_inicio = st.date_input("Fecha de corte desde:", value=datetime.today().replace(day=1))
        fecha_fin = st.date_input("Fecha de pago hasta:", value=datetime.today())

        df_tarjetas = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) &
                         (df['fecha'] <= pd.to_datetime(fecha_fin)) &
                         (df['forma de pago'].isin(tarjetas_unicas)) &
                         (df['tipo'] == 'Gasto')]

        if not df_tarjetas.empty:
            resumen_tarjetas = df_tarjetas.groupby('forma de pago')['monto'].sum().reset_index()
            resumen_tarjetas.columns = ['Tarjeta', 'Total gastado en rango']
            st.dataframe(resumen_tarjetas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay gastos con tarjetas en el rango de fechas seleccionado.")
