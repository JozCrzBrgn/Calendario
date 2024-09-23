import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td 

import streamlit as st
import streamlit_authenticator as stauth

from config.configuration import config, read_json_from_supabase

#* USER AUTHENTICATION
credenciales = read_json_from_supabase(config.BUCKET_GENERAL, config.CREDENCIALES_FILE)
authenticator = stauth.Authenticate(
    credenciales,
    st.secrets["COOKIE_NAME"],
    st.secrets["COOKIE_KEY"],
    int(st.secrets["COOKIE_EXPIRY_DAYS"]),
)
name, authentication_status, username = authenticator.login()

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username ands password')
elif authentication_status:
    col1, col2 = st.columns([4,1])
    with col1:
        st.success('Bienvenida {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("Reporte de Ventas")

    sucursal = st.radio("Selecciona un sucursal", ["Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán"])
    fecha = st.date_input("Selecciona una fecha")
    print(sucursal, fecha)
    print(str(fecha)[:10])

    tabla_db = {
        "Agrícola Oriental":"db04_inventario_agri", 
        "Nezahualcóyotl":"db04_inventario_neza", 
        "Zapotitlán":"db04_inventario_zapo", 
        "Oaxtepec":"db04_inventario_oaxt", 
        "Pantitlán":"db04_inventario_panti"
        }
    #? ANALISIS DE DATOS
    # Obtenemos los datos de la DB
    cols = "clave,producto,fecha_estatus,hora_estatus"
    data = config.supabase.table(tabla_db[sucursal]).select(cols).eq("fecha_estatus", fecha).execute().data
    # Creamos el Dataframe
    df = pd.DataFrame(data)
    # Renombrar la columna 'tipo_combo' a 'promocion'
    df.rename(columns={'fecha_estatus': 'fecha_venta', 'hora_estatus': 'hora_venta'}, inplace=True)
    if df.empty!=False:
        st.warning(f"La sucursal de {sucursal} no tiene ventas para la fecha {fecha}.")
    else:
        # Asegurarse de que la columna esté en formato de tiempo
        df['hora_venta'] = pd.to_datetime(df['hora_venta'], format='%H:%M:%S').dt.time
        # Ordenamos por hora de venta
        df_sorted = df.sort_values(by=['hora_venta'])
        st.table(df_sorted)