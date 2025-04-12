# Importar librerías necesarias
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import plotly.express as px

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
# Abrir hoja (reemplaza con tu nombre exacto)
sheet = client.open("finanzas-personales").worksheet("Hoja1")

# Cargar datos existentes
datos = sheet.get_all_records()
# Mostrar datos actuales
st.subheader("📋 Movimientos actuales")
st.dataframe(pd.DataFrame(datos))

# Convertimos datos a DataFrame de Pandas
df = pd.DataFrame(datos)

# Asegurarnos que 'Monto' sea numérico (por seguridad)
df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)

# Agrupamos por Mes y Tipo para sumar los montos
resumen_mensual = df.groupby(['Mes', 'Tipo'])['Monto'].sum().reset_index()

# Gráfico de barras
st.subheader("📊 Ingresos vs Gastos por mes")
fig_bar = px.bar(
    resumen_mensual, 
    x='Mes', 
    y='Monto', 
    color='Tipo', 
    barmode='group', 
    text_auto='.2s',
    labels={'Monto': 'Total', 'Mes': 'Mes'}
)

st.plotly_chart(fig_bar, use_container_width=True)

# Filtramos solo gastos para el gráfico circular
df_gastos = df[df['Tipo'] == 'Gasto']

# Agrupamos gastos por categoría
gastos_categoria = df_gastos.groupby('Categoría')['Monto'].sum().reset_index()

# Gráfico circular (si hay datos)
df_gastos = df[df['Tipo'] == 'Gasto']

if 'categoria' in df_gastos.columns and not df_gastos['Categoría'].isna().all():
    gastos_categoria = df_gastos.groupby('Categoría')['Monto'].sum().reset_index()

    if not gastos_categoria.empty:
        st.subheader("🍕 Distribución de gastos por categoría")
        fig_pie = px.pie(
            gastos_categoria,
            values='Monto',
            names='Categoría',
            title='Distribución porcentual por categoría',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("⚠️ No hay montos válidos para las categorías.")
else:
    st.info("⚠️ No se encontraron categorías válidas para mostrar el gráfico.")


# --- NUEVO FORMULARIO PERSONALIZADO ---
st.subheader("➕ Añadir nuevo movimiento")

# Fecha
fecha = st.date_input("Fecha:", datetime.today())

# Mes (automático según la fecha)
mes = fecha.strftime("%B")  # Ejemplo: "Abril"

# Tipo (Ingreso o Gasto)
tipo = st.selectbox("Tipo:", ["Ingreso", "Gasto"])

# Categoría
categoria = st.text_input("Categoría:")

# Concepto
concepto = st.text_input("Concepto:")

# Monto
monto = st.number_input("Monto:", min_value=0.0, step=1.0)

# Forma de Pago
forma_pago = st.selectbox("Forma de Pago:", ["Efectivo", "Tarjeta", "Transferencia", "Otro"])

# Nota (opcional)
nota = st.text_area("Nota (opcional):")

# Botón para guardar movimiento
if st.button("Guardar movimiento 💾"):
    # Añadir la información en la hoja de Google Sheets
    nueva_fila = [str(fecha), mes, tipo, categoria, concepto, monto, forma_pago, nota]
    sheet.append_row(nueva_fila)
    
    st.success("✅ Movimiento guardado correctamente.")

    # Recargar para ver actualización inmediata
    st.experimental_rerun()
