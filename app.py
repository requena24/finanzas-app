# Importar librerías
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Título para la app
st.title("📊 Validación Google Sheets ↔️ Streamlit")

# Configuración del acceso a Google Sheets usando Secrets en formato TOML
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Aquí obtenemos las credenciales desde los secrets guardados en Streamlit Cloud
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

# Creamos cliente autorizado para Google Sheets
client = gspread.authorize(credentials)

# Abrir la hoja específica (REEMPLAZA con el nombre de tu Google Sheet)
sheet = client.open("finanzas-personales").worksheet("Hoja1")

# Leer todos los datos y guardarlos en una variable
datos = sheet.get_all_records()

# Mostrar los datos en la app
st.write("✅ ¡Datos cargados correctamente desde Google Sheets!")
st.dataframe(pd.DataFrame(datos))
