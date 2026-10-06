import streamlit as st
import pandas as pd
import os
from datetime import datetime
import xml.etree.ElementTree as ET

# CONFIGURACIÓN DE ARCHIVOS
DB_FILE = "inventario_fibra_empresarial.xlsx"
USERS_FILE = "usuarios_sistema.xlsx"

# LISTA COMPLETA DE SPLITTERS DEL MERCADO
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
    name_doc.text = "Inventario de Fibra Óptica - Red General"
    
    for _, fila in dataframe.iterrows():
        try:
            lat = str(fila["Latitud"]).strip()
            lon = str(fila["Longitud"]).strip()
            if lat and lon and lat != "nan" and lon != "nan":
                placemark = ET.SubElement(document, "Placemark")
                name_p = ET.SubElement(placemark, "name")
                name_p.text = f"{fila['Código/Nombre']} ({fila['Elemento/Caja FAT']})"
                desc = ET.SubElement(placemark, "description")
                desc.text = f"""
                <b>Detalles Técnicos:</b><br>
                • Splitter: {fila['Tipo de Splitter']}<br>
                • Capacidad: {fila['Puertos Ocupados']}/{fila['Capacidad Total']} Hilos<br>
                • Estado: {fila['Estado']}<br>
                • Técnico: {fila['Registrado Por']}<br>
                • Fecha de Inst.: {fila['Fecha/Hora']}<br>
                • Notas: {fila['Notas']}
                """
                point = ET.SubElement(placemark, "Point")
                coords = ET.SubElement(point, "coordinates")
                coords.text = f"{lon},{lat},0"
        except Exception:
            continue
    return ET.tostring(kml, encoding="utf-8")

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        return pd.read_excel(USERS_FILE)
    else:
        df_admin = pd.DataFrame([{"Usuario": "admin_master", "Clave": "master2026", "Rol": "Máster"}])
        df_admin.to_excel(USERS_FILE, index=False)
        return df_admin

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    else:
        return pd.DataFrame(columns=[
            "Fecha/Hora", "Registrado Por", "Rol Usuario", "Elemento/Caja FAT", 
            "Código/Nombre", "Tipo de Splitter", "Capacidad Total", "Puertos Ocupados", 
            "Latitud", "Longitud", "Estado", "Notas"
        ])

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""
if "rol_actual" not in st.session_state:
    st.session_state.rol_actual = ""

df_usuarios = cargar_usuarios()
df_inventario = cargar_datos()

st.set_page_config(page_title="Sistema Fibra Óptica Enterprise", layout="wide")

if not st.session_state.autenticado:
    st.title("🔒 Sistema de Inventario de Fibra Óptica")
    st.subheader("Por favor, inicie sesión para acceder a la barra de herramientas")
    
    with st.form("login_form"):
        usuario_input = st.text_input("Usuario / Técnico")
        contrasena_input = st.text_input("Contraseña", type="password")
        boton_login = st.form_submit_button("Ingresar")
        
        if boton_login:
            user_row = df_usuarios[df_usuarios["Usuario"] == usuario_input]
            if not user_row.empty and str(user_row.iloc[0]["Clave"]) == str(contrasena_input):
                st.session_state.autenticado = True
                st.session_state.usuario_actual = usuario_input
                st.session_state.rol_actual = user_row.iloc[0]["Rol"]
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorre
            
            
                
            
         
