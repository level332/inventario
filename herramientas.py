def mostrar_menu(st, pd, datetime, DB_FILE, USERS_FILE, TIPOS_SPLITTER, df_usuarios, df_inventario, cargar_datos, cargar_usuarios, generar_kml):
    with st.sidebar:
        st.image("https://flaticon.com", width=120)
        st.title("MENÚ DE CONTROL")
        st.markdown(f"👤 *{st.session_state.usuario_actual}* ({st.session_state.rol_actual})")
        opciones = ["➕ Registrar Caja FAT", "📊 Consultar Inventario", "🌍 Google Earth", "⚙️ Técnicos"] if st.session_state.rol_actual == "Máster" else ["➕ Registrar Caja FAT", "📊 Mis Registros"]
        seleccion = st.radio("Herramientas:", opciones)
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    if seleccion == "➕ Registrar Caja FAT":
        st.title("➕ Registro Técnico de Caja FAT")
        with st.form("f_fibra", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                elem = st.selectbox("Elemento", ["Caja FAT / CTO", "Mufa de Empalme", "Poste", "OLT"])
                cod = st.text_input("Código FAT")
                spl = st.selectbox("Splitter", TIPOS_SPLITTER)
                cap = st.number_input("Total Puertos", min_value=1, value=16)
                ocu = st.number_input("Ocupados", min_value=0, value=0)
            with col2:
                lat = st.text_input("Latitud (GPS)")
                lon = st.text_input("Longitud (GPS)")
                est = st.select_slider("Estado", options=["Operativo", "Mantenimiento", "Falla"])
                not_t = st.text_area("Observaciones")
            if st.form_submit_button("💾 Guardar Registro"):
                if not cod or not lat or not lon: st.error("⚠️ Llene Código, Latitud y Longitud.")
                else:
                    n_f = {"Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Registrado Por": st.session_state.usuario_actual, "Rol Usuario": st.session_state.rol_actual, "Elemento/Caja FAT": elem, "Código/Nombre": cod, "Tipo de Splitter": spl, "Capacidad Total": cap, "Puertos Ocupados": ocu, "Latitud": lat, "Longitud": lon, "Estado": est, "Notas": not_t}
                    df = pd.concat([cargar_datos(), pd.DataFrame([n_f])], ignore_index=True)
                    df.to_excel(DB_FILE, index=False)
                    st.success("✅ Guardado con éxito.")

    elif seleccion == "📊 Consultar Inventario":
        st.title("📊 Inventario Global")
        df_act = cargar_datos()
        if df_act.empty: st.info("Sin registros.")
        else:
            st.dataframe(df_act, use_container_width=True)
            with open(DB_FILE, "rb") as f:
                st.download_button("📥 Descargar Excel", f, "Inventario.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    elif seleccion == "🌍 Google Earth":
        st.title("🌍 Exportar a Google Earth")
        df_act = cargar_datos()
        if df_act.empty: st.info("Sin datos GPS.")
        else: st.download_button("🚀 Descargar Archivo KML", generar_kml(df_act), "Red_Fibra.kml", "application/vnd.google-earth.kml+xml", use_container_width=True)

    elif seleccion == "📊 Mis Registros":
        st.title("📊 Mis Actividades")
        df_act = cargar_datos()
        st.dataframe(df_act[df_act["Registrado Por"] == st.session_state.usuario_actual], use_container_width=True)

    elif seleccion == "⚙️ Técnicos":
        st.title("⚙️ Administrar Técnicos")
        u_act = cargar_usuarios()
        st.dataframe(u_act[["Usuario", "Rol"]], use_container_width=True)
        with st.form("a_tec", clear_on_submit=True):
            n_u = st.text_input("Nuevo Usuario").strip()
            n_c = st.text_input("Contraseña", type="password")
            if st.form_submit_button("➕ Crear Cuenta Técnico") and n_u and n_c:
                if n_u in u_act["Usuario"].values: st.error("⚠️ Ya existe.")
                else:
                    pd.concat([u_act, pd.DataFrame([{"Usuario": n_u, "Clave": n_c, "Rol":
