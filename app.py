# Importamos Streamlit y librerías necesarias
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Título de la app
st.title("📊 Finanzas Personales - Validar Conexión Google Sheets")

# Definir permisos para la app (scopes)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Conectar a Google Sheets usando las credenciales guardadas en Streamlit Secrets
credentials = Credentials.from_service_account_info(st.secrets, scopes=scope)

# Crear un cliente para interactuar con Google Sheets
client = gspread.authorize(credentials)

# Abrir la hoja específica (Reemplaza con el nombre exacto de tu hoja de Google Sheets)
sheet = client.open("finanzas-personales").worksheet("Hoja1")

# Obtener todos los datos de la hoja
datos = sheet.get_all_records()

# Mostrar datos en pantalla con Streamlit
st.write("✅ Conexión exitosa. Datos en tu Google Sheet:")
st.dataframe(datos)  # Esto los muestra como una tabla bonita en Streamlit
