import streamlit as st
import pandas as pd
import os
from datetime import datetime
import xml.etree.ElementTree as ET

# CONFIGURACIÓN DE ARCHIVOS
DB_FILE = "inventario_fibra_empresarial.xlsx"
USERS_FILE = "usuarios_sistema.xlsx"
LOGO_FILE = "logo.png"  # Archivo del logo de LEVELPLUS

TIPOS_SPLITTER = [
    "Asimétrico 99/1", "Asimétrico 98/2", "Asimétrico 97/3", "Asimétrico 95/5", "Asimétrico 90/10",
    "Asimétrico 85/15", "Asimétrico 80/20", "Asimétrico 75/25", "Asimétrico 70/30", "Asimétrico 65/35",
    "Asimétrico 60/40", "Asimétrico 55/45", "Simétrico 50/50 (1x2)", "Simétrico 1x4", "Simétrico 1x8",
    "Simétrico 1x16", "Simétrico 1x32", "Simétrico 1x64"
]

def generar_kml(dataframe):
    kml = ET.Element("kml", xmlns="http://opengis.net")
    document = ET.SubElement(kml, "Document")
    name_doc = ET.SubElement(document, "name")
    name_doc.text = "Inventario de Fibra Óptica - Red LEVELPLUS"
    for _, fila in dataframe.iterrows():
        try:
            lat, lon = str(fila["Latitud"]).strip(), str(fila["Longitud"]).strip()
            if lat and lon and lat != "nan" and lon != "nan":
                placemark = ET.SubElement(document, "Placemark")
                name_p = ET.SubElement(placemark, "name")
                name_p.text = f"{fila['Código/Nombre']} ({fila['Elemento/Caja FAT']})"
                desc = ET.SubElement(placemark, "description")
                desc.text = f"Splitter: {fila['Tipo de Splitter']}\nCapacidad: {fila['Puertos Ocupados']}/{fila['Capacidad Total']}\nTécnico: {fila['Registrado Por']}"
                point = ET.SubElement(placemark, "Point")
                coords = ET.SubElement(point, "coordinates")
                coords.text = f"{lon},{lat},0"
        except: continue
    return ET.tostring(kml, encoding="utf-8")

def cargar_usuarios():
    if os.path.exists(USERS_FILE): return pd.read_excel(USERS_FILE)
    df = pd.DataFrame([{"Usuario": "admin_master", "Clave": "master2026", "Rol": "Máster"}])
    df.to_excel(USERS_FILE, index=False)
    return df

def cargar_datos():
    if os.path.exists(DB_FILE): return pd.read_excel(DB_FILE)
    return pd.DataFrame(columns=["Fecha/Hora", "Registrado Por", "Rol Usuario", "Elemento/Caja FAT", "Código/Nombre", "Tipo de Splitter", "Capacidad Total", "Puertos Ocupados", "Latitud", "Longitud", "Estado", "Notas"])

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = ""
if "rol_actual" not in st.session_state: st.session_state.rol_actual = ""

df_usuarios = cargar_usuarios()
df_inventario = cargar_datos()
st.set_page_config(page_title="Sistema Fibra LEVELPLUS", layout="wide")

if not st.session_state.autenticado:
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
    with col_titulo:
        st.title("🔒 Sistema de Inventario - LEVELPLUS")
        st.subheader("Módulo de Gestión de Infraestructura y Redes FO")
    
    with st.form("login_form"):
        u_in = st.text_input("Usuario / Técnico")
        c_in = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar al Sistema"):
            user_row = df_usuarios[df_usuarios["Usuario"] == u_in]
            if not user_row.empty and str(user_row.iloc[0]["Clave"]) == str(c_in):
                st.session_state.autenticado = True
                st.session_state.usuario_actual = u_in
                st.session_state.rol_actual = user_row.iloc[0]["Rol"]
                st.rerun()
            else: st.error("❌ Usuario o contraseña incorrectos")
else:
    import herramientas
    herramientas.mostrar_menu(st, pd, datetime, DB_FILE, USERS_FILE, LOGO_FILE, TIPOS_SPLITTER, df_usuarios, df_inventario, cargar_datos, cargar_usuarios, generar_kml)
