# Importar librerías necesarias
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

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
