import streamlit as st
import pandas as pd
import os
from datetime import datetime
import xml.etree.ElementTree as ET  # Librería nativa para generar el archivo KML

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

# Función para convertir la base de datos de Excel en un archivo KML de Google Earth
def generar_kml(dataframe):
    # Crear estructura básica del KML
    kml = ET.Element("kml", xmlns="http://opengis.net")
    document = ET.SubElement(kml, "Document")
    
    # Título del mapa en Google Earth
    name_doc = ET.SubElement(document, "name")
    name_doc.text = "Inventario de Fibra Óptica - Red General"
    
    # Recorrer cada caja FAT registrada
    for _, fila in dataframe.iterrows():
        try:
            # Validar que existan las coordenadas
            lat = str(fila["Latitud"]).strip()
            lon = str(fila["Longitud"]).strip()
            
            if lat and lon and lat != "nan" and lon != "nan":
                placemark = ET.SubElement(document, "Placemark")
                
                # Nombre del punto en el mapa (Código de la caja)
                name_p = ET.SubElement(placemark, "name")
                name_p.text = f"{fila['Código/Nombre']} ({fila['Elemento/Caja FAT']})"
                
                # Descripción con la ficha técnica detallada al hacer clic en Google Earth
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
                
                # Asignar coordenadas geográficas
                point = ET.SubElement(placemark, "Point")
                coords = ET.SubElement(point, "coordinates")
                coords.text = f"{lon},{lat},0"  # Formato KML requiere Longitud,Latitud
        except Exception:
            continue
            
    # Retornar el archivo XML listo como texto plano codificado
    return ET.tostring(kml, encoding="utf-8")

# Cargar o inicializar la base de datos de usuarios
def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        return pd.read_excel(USERS_FILE)
    else:
        df_admin = pd.DataFrame([{"Usuario": "admin_master", "Clave": "master2026", "Rol": "Máster"}])
        df_admin.to_excel(USERS_FILE, index=False)
        return df_admin

# Cargar o inicializar la base de datos de inventario
def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    else:
        return pd.DataFrame(columns=[
            "Fecha/Hora", "Registrado Por", "Rol Usuario", "Elemento/Caja FAT", 
            "Código/Nombre", "Tipo de Splitter", "Capacidad Total", "Puertos Ocupados", 
            "Latitud", "Longitud", "Estado", "Notas"
        ])

# Inicializar estados de la sesión web
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""
if "rol_actual" not in st.session_state:
    st.session_state.rol_actual = ""

df_usuarios = cargar_usuarios()
df_inventario = cargar_datos()

st.set_page_config(page_title="Sistema Fibra Óptica Enterprise", layout="wide")

# 1. PANTALLA DE INICIO DE SESIÓN (LOGIN)
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
                st.error("❌ Usuario o contraseña incorrectos")

else:
    with st.sidebar:
        st.image("https://flaticon.com", width=120)
        st.title("MENÚ DE CONTROL")
        st.markdown(f"👤 Usuario: *{st.session_state.usuario_actual}*")
        st.markdown(f"🏷️ Rol: {st.session_state.rol_actual}")
        st.markdown("---")
        
        if st.session_state.rol_actual == "Máster":
            opciones_menu = ["➕ Registrar Caja FAT", "📊 Consultar Inventario Global", "🌍 Enlace Google Earth", "⚙️ Administrar Técnicos"]
        else:
            opciones_menu = ["➕ Registrar Caja FAT", "📊 Mis Registros"]
            
        seleccion_menu = st.radio("Seleccione una herramienta:", opciones_menu)
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario_actual = ""
            st.session_state.rol_actual = ""
            st.rerun()

    if seleccion_menu == "➕ Registrar Caja FAT":
        st.title("➕ Herramienta de Registro Técnico")
        st.write("Complete la ficha técnica para añadir la Caja FAT o elemento a la red.")
        
        with st.form("formulario_fibra", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                elemento = st.selectbox("Tipo de Elemento", ["Caja FAT / CTO", "Mufa de Empalme", "Poste de Paso", "Nodo Central OLT"])
                codigo = st.text_input("Código de la Caja FAT", placeholder="Ej: FAT-B2-P04")
                splitter = st.selectbox("Splitter Asignado a la Caja", TIPOS_SPLITTER)
                capacidad = st.number_input("Puertos/Hilos Totales del Splitter", min_value=1, value=16)
                ocupados = st.number_input("Puertos Ocupados actualmente", min_value=0, value=0)
            with col2:
                latitud = st.text_input("Latitud (GPS)", placeholder="Ej: 10.4806")
                longitud = st.text_input("Longitud (GPS)", placeholder="Ej: -66.9036")
                estado = st.select_slider("Estado Operativo", options=["Operativo / Disponible", "Mantenimiento", "Falla / Dañado"])
                notes = st.text_area("Observaciones del tendido o fusión")
                
            guardar = st.form_submit_button("💾 Guardar Registro en la Red")
            
            if guardar:
                if not codigo:
                    st.error("⚠️ El código identificador de la Caja FAT es obligatorio.")
                elif not latitud or not longitud:
                    st.error("⚠️ Para vincular con Google Earth, la Latitud y Longitud son campos obligatorios.")
                else:
                    nueva_fila = {
                        "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Registrado Por": st.session_state.usuario_actual,
                        "Rol Usuario": st.session_state.rol_actual,
                        "Elemento/Caja FAT": elemento,
                        "Código/Nombre": codigo,
                        "Tipo de Splitter": splitter,
                        "Capacidad Total": capacidad,
                        "Puertos Ocupados"
            
            
                
            
         
