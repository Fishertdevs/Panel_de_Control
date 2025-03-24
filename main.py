"""
Panel de Control Interactivo
Autor: Harry Fishert
GitHub: https://github.com/Fishertdevs
Descripción: Una aplicación interactiva desarrollada con Streamlit y Plotly para analizar archivos subidos por los usuarios.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image
from PyPDF2 import PdfReader
import docx
import nbformat
import zipfile

# Configuración de la página
st.set_page_config(
    page_title="Panel de Control de Archivos",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título del panel
st.title("📂 Panel de Control de Archivos")
st.markdown("Sube un archivo y obtén detalles relevantes sobre su contenido y características.")

# Widget para subir archivos
st.sidebar.header("Subir Archivo")
archivo_subido = st.sidebar.file_uploader("Selecciona un archivo", type=None)

# Mostrar detalles del archivo subido
if archivo_subido is not None:
    # Mostrar detalles básicos del archivo
    st.subheader("Detalles del Archivo")
    st.write(f"**Nombre del archivo:** {archivo_subido.name}")
    st.write(f"**Tamaño del archivo:** {archivo_subido.size / 1024:.2f} KB")
    st.write(f"**Tipo de archivo:** {archivo_subido.type}")

    # Intentar leer el contenido del archivo
    try:
        if archivo_subido.type.startswith("text") or archivo_subido.name.endswith(".csv"):
            # Si es un archivo de texto o CSV, mostrar el contenido
            df = pd.read_csv(archivo_subido)
            st.subheader("Contenido del Archivo (Texto o CSV)")
            st.dataframe(df)
        elif archivo_subido.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            # Si es un archivo Excel, mostrar los datos en una tabla
            df = pd.read_excel(archivo_subido)
            st.subheader("Contenido del Archivo (Excel)")
            st.dataframe(df)

            # Gráficos dinámicos para archivos Excel
            st.subheader("Gráficos Dinámicos")
            columnas_numericas = df.select_dtypes(include=["number"]).columns
            if len(columnas_numericas) >= 2:
                x_col = st.selectbox("Selecciona la columna X", columnas_numericas, key="unique_x_col")
                y_col = st.selectbox("Selecciona la columna Y", columnas_numericas, key="unique_y_col")
                tipo_grafico = st.radio("Selecciona el tipo de gráfico", ["Dispersión", "Línea", "Barras"], key="unique_chart_type")
                if tipo_grafico == "Dispersión":
                    fig = px.scatter(df, x=x_col, y=y_col, title="Gráfico de Dispersión")
                elif tipo_grafico == "Línea":
                    fig = px.line(df, x=x_col, y=y_col, title="Gráfico de Línea")
                elif tipo_grafico == "Barras":
                    fig = px.bar(df, x=x_col, y=y_col, title="Gráfico de Barras")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("El archivo no contiene suficientes columnas numéricas para generar gráficos.")
        elif archivo_subido.type.startswith("image"):
            # Si es una imagen, mostrarla
            st.subheader("Vista Previa de la Imagen")
            image = Image.open(archivo_subido)
            st.image(image, caption=archivo_subido.name, use_container_width=True)
        elif archivo_subido.type in ["application/pdf"]:
            # Si es un archivo PDF, mostrar su contenido
            st.subheader("Contenido del Archivo PDF")
            pdf_reader = PdfReader(archivo_subido)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            st.text_area("Vista previa del contenido del PDF", pdf_text, height=300)
        elif archivo_subido.name.endswith(".docx"):
            # Si es un archivo Word, mostrar su contenido
            st.subheader("Contenido del Archivo Word")
            doc = docx.Document(archivo_subido)
            doc_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            st.text_area("Vista previa del contenido del Word", doc_text, height=300)
        elif archivo_subido.name.endswith(".ipynb"):
            # Si es un archivo Jupyter Notebook, mostrar su contenido
            st.subheader("Contenido del Archivo Jupyter Notebook")
            notebook = nbformat.read(archivo_subido, as_version=4)
            notebook_text = "\n".join([cell.source for cell in notebook.cells if cell.cell_type == "code"])
            st.text_area("Vista previa del contenido del Notebook", notebook_text, height=300)
        elif archivo_subido.name.endswith(".zip"):
            # Si es un archivo ZIP, listar su contenido
            st.subheader("Contenido del Archivo ZIP")
            try:
                with zipfile.ZipFile(archivo_subido, 'r') as zip_ref:
                    archivos_zip = zip_ref.namelist()
                    st.write("Archivos contenidos en el ZIP:")
                    for archivo in archivos_zip:
                        st.write(f"- {archivo}")
                    
                    # Opción para extraer archivos
                    if st.button("Extraer archivos"):
                        ruta_extraccion = os.path.join(os.getcwd(), "extraidos")
                        os.makedirs(ruta_extraccion, exist_ok=True)  # Crear la carpeta si no existe
                        zip_ref.extractall(ruta_extraccion)
                        st.success(f"Archivos extraídos en la carpeta: {ruta_extraccion}")
            except zipfile.BadZipFile:
                st.error("El archivo subido no es un archivo ZIP válido.")
            except Exception as e:
                st.error(f"Error al procesar el archivo ZIP: {e}")
        else:
            # Si el archivo no es legible, mostrar un mensaje
            st.warning("No se puede mostrar el contenido de este tipo de archivo.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.info("Por favor, sube un archivo para analizar.")

# Footer
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y Plotly")
