import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuración de la app
st.set_page_config(page_title="Finanzas Personales", page_icon="💰", layout="centered")

st.title("💰 App de Finanzas Personales")
st.markdown("Gestión simple y eficiente de tus ingresos y gastos. 📊")

# Conectar con Google Sheets
# Define el alcance
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Carga las credenciales desde variables de entorno en Streamlit Cloud
import json
from google.oauth2.service_account import Credentials

service_account_info = json.loads(st.secrets["gcp_service_account"])
credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)

# Autenticación con gspread
gc = gspread.authorize(credentials)

# ID de tu Google Sheet
SPREADSHEET_ID = "1b6Ci77d0MBua_dS8uGa5cNdj1F_66w4Ju4ONp8GgVD4/edit?gid=0#gid=0"

# Abrir la hoja
sheet = gc.open_by_key(SPREADSHEET_ID)
worksheet = sheet.sheet1

# Leer los datos
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.dataframe(df)
