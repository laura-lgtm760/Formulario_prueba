import streamlit as st
import pandas as pd
import os

st.title("Formulario de Registro de Parcelas")

# 1. Inicializamos la memoria de la sesión
if "nombre_guardado" not in st.session_state:
    st.session_state.nombre_guardado = ""
if "telefono_guardado" not in st.session_state:
    st.session_state.telefono_guardado = ""
if "mostrar_boton_otra" not in st.session_state:
    st.session_state.mostrar_boton_otra = False
if "finalizado" not in st.session_state:
    st.session_state.finalizado = False
# Un contador para cambiar el nombre del formulario y forzar la limpieza
if "contador_form" not in st.session_state:
    st.session_state.contador_form = 0

# Si el usuario ya ha finalizado, mostramos solo el mensaje final y paramos
if st.session_state.finalizado:
    st.success("Formulario completado. Muchas gracias.")
    st.info(f"Tus datos se han guardado correctamente en el archivo Excel.")
    
    # Por si acaso quieren registrar a otra persona totalmente distinta, les dejamos un botón de reinicio
    if st.button("Registrar un nuevo usuario"):
        st.session_state.clear() # Limpia toda la memoria
        st.rerun()
    st.stop() # Detiene la ejecución aquí para que no vuelva a pintar el formulario

# 2. EL FORMULARIO DE ENTRADA (con key dinámica)
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

# Definimos el nombre del Excel dinámico según el nombre introducido
ARCHIVO_EXCEL = f"{nombre}.xlsx" if nombre else "registro_parcelas.xlsx"

# 3. PROCESAMIENTO AL PULSAR "GUARDAR ESTA PARCELA"
if enviado:
    if not nombre or not municipio:
        st.error("Rellene nombre y municipio")
    else:
        # Guardamos los datos personales en la sesión
        st.session_state.nombre_guardado = nombre
        st.session_state.telefono_guardado = telefono
        
        # Creamos la estructura de datos
        nueva_fila = {
            "Nombre": nombre, "Teléfono": telefono, "Municipio": municipio,
            "Código Municipio": cod_mun, "Polígono": poligono, "Parcela": parcela,
            "Recinto": recinto, "Superficie Ha": super_ha,
            "Cultivo Anterior": cultivo_anterior, "Cultivo Posterior": cultivo_posterior,
            "Observaciones": observaciones
        }
        
        df_nuevo = pd.DataFrame([nueva_fila])
        
        # Guardado/Acumulado en Excel
        if os.path.exists(ARCHIVO_EXCEL):
            df_existente = pd.read_excel(ARCHIVO_EXCEL)  
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final.to_excel(ARCHIVO_EXCEL, index=False)
        
        st.toast(f"¡Parcela de {municipio} guardada correctamente!")
        
        # Activamos el botón secundario
        st.session_state.mostrar_boton_otra = True
        st.rerun()

# 4. BOTONES DE ACCIÓN (FUERA DEL FORMULARIO)
if st.session_state.mostrar_boton_otra:
    st.info("La parcela se ha guardado en el archivo Excel. ¿Qué deseas hacer ahora?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Añadir otra Parcela"):
            st.session_state.contador_form += 1
            st.session_state.mostrar_boton_otra = False
            st.rerun()
            
    with col2:
        # Aquí usamos un st.button NORMAL, ya que estamos fuera del form
        if st.button("Terminar y Enviar"):
            st.session_state.finalizado = True
            st.rerun()