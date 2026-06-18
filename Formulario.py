import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

st.title("Formulario de Registro de Parcelas")


# CONFIGURACIÓN DEL CORREO

CORREO_EMISOR = "formulario.parcelas@gmail.com"  # El correo que enviará el Excel
CONTRASEÑA_EMISOR = "iaut mnvj qvgi gtzy" # Contraseña de aplicación
CORREO_RECEPTOR = "bec_lmacho@mcp.es" # El correo donde RECIBIR los Excel


# FUNCION PARA ENVIAR EL EMAIL CON EL EXCEL ADJUNTO

def enviar_excel_por_correo(nombre_usuario, ruta_excel):
    try:
        # Creamos el mensaje
        msg = MIMEMultipart()
        msg['From'] = CORREO_EMISOR
        msg['To'] = CORREO_RECEPTOR
        msg['Subject'] = f"Nuevo formulario de parcelas: {nombre_usuario}"
        
        cuerpo = f"Hola,\n\nSe han recibido nuevas parcelas del usuario {nombre_usuario}.\nAdjunto encontrarás su archivo Excel."
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        # Abrimos el archivo Excel y lo adjuntamos
        with open(ruta_excel, "rb") as adjunto:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(adjunto.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(ruta_excel)}")
            msg.attach(part)
        
        # Conexión al servidor de Gmail (si usas otra compañía, cambia el smtp)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(CORREO_EMISOR, CONTRASEÑA_EMISOR)
        server.sendmail(CORREO_EMISOR, CORREO_RECEPTOR, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")
        return False


# MEMORIA DE LA SESIÓN

if "nombre_guardado" not in st.session_state:
    st.session_state.nombre_guardado = ""
if "telefono_guardado" not in st.session_state:
    st.session_state.telefono_guardado = ""
if "mostrar_boton_otra" not in st.session_state:
    st.session_state.mostrar_boton_otra = False
if "finalizado" not in st.session_state:
    st.session_state.finalizado = False
if "contador_form" not in st.session_state:
    st.session_state.contador_form = 0

# Pantalla de finalización
if st.session_state.finalizado:
    st.success("Formulario completado. Muchas gracias.")
    st.info("Los datos han sido procesados y enviados por correo correctamente.")
    if st.button("Registrar un nuevo usuario"):
        st.session_state.clear()
        st.rerun()
    st.stop()


# FORMULARIO DE ENTRADA

with st.form(key=f"formulario_parcela_{st.session_state.contador_form}", enter_to_submit= False):
    st.subheader("Datos Personales")
    nombre = st.text_input("Nombre completo:", value=st.session_state.nombre_guardado)
    telefono = st.text_input("Teléfono:", value=st.session_state.telefono_guardado)
    
    st.subheader("Datos de la Parcela")
    municipio = st.text_input("Municipio:")
    cod_mun = st.number_input("Código municipio:", step=1, value=0)
    poligono = st.number_input("Polígono:", step=1, value=0)
    parcela = st.number_input("Parcela:", step=1, value=0)
    recinto = st.number_input("Recinto:", step=1, value=0)
    super_ha = st.number_input("Superficie (Ha):", min_value=0.0, step=0.01)
    cultivo_anterior = st.text_input("Cultivo anterior:")
    cultivo_posterior = st.text_input("Cultivo posterior:")
    observaciones = st.text_input("Notas / Observaciones:")
    
    enviado = st.form_submit_button("Guardar esta Parcela")

# Definimos el nombre del Excel dinámico
ARCHIVO_EXCEL = f"{nombre}.xlsx" if nombre else "registro_parcelas.xlsx"

if enviado:
    if not nombre or not municipio:
        st.error("Rellene nombre y municipio")
    else:
        st.session_state.nombre_guardado = nombre
        st.session_state.telefono_guardado = telefono
        
        nueva_fila = {
            "Nombre": nombre, "Teléfono": telefono, "Municipio": municipio,
            "Código Municipio": cod_mun, "Polígono": poligono, "Parcela": parcela,
            "Recinto": recinto, "Superficie Ha": super_ha,
            "Cultivo Anterior": cultivo_anterior, "Cultivo Posterior": cultivo_posterior,
            "Observaciones": observaciones
        }
        
        df_nuevo = pd.DataFrame([nueva_fila])
        
        if os.path.exists(ARCHIVO_EXCEL):
            df_existente = pd.read_excel(ARCHIVO_EXCEL)  
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final.to_excel(ARCHIVO_EXCEL, index=False)
        
        st.toast(f"¡Parcela de {municipio} guardada correctamente!")
        st.session_state.mostrar_boton_otra = True
        st.rerun()

# Botones de acción tras guardar
if st.session_state.mostrar_boton_otra:
    st.info("La parcela se ha guardado de forma temporal. ¿Qué deseas hacer?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Añadir otra Parcela"):
            st.session_state.contador_form += 1
            st.session_state.mostrar_boton_otra = False
            st.rerun()
    with col2:
        if st.button("Terminar y Enviar"):
            # Llamamos a la función de enviar correo pasándole el nombre y la ruta del Excel
            with st.spinner("Enviando datos por correo..."):
                exito = enviar_excel_por_correo(st.session_state.nombre_guardado, ARCHIVO_EXCEL)
            if exito:
                st.session_state.finalizado = True
                st.rerun()