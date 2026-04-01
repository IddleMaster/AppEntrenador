import os
import sys
from database.models import Cliente, obtener_sesion
import pathlib

# --- BLOQUE PARA ARREGLAR EL ERROR EN WINDOWS (GTK3) ---
if os.name == 'nt':  # Solo si estamos en Windows
    gtk3_folder = r'C:\Program Files\GTK3-Runtime Win64\bin'
    if os.path.exists(gtk3_folder):
        # Añadimos la carpeta de GTK al sistema para que WeasyPrint la vea
        os.environ['PATH'] = gtk3_folder + os.pathsep + os.environ.get('PATH', '')
        # Opción extra para Python 3.8+
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(gtk3_folder)
            except Exception:
                pass
# -------------------------------------------------------

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import datetime

def generar_pdf_rutina(nombre_cliente, fase, lista_ejercicios, ruta_destino):
    """
    Genera un PDF con la rutina organizada por DÍAS, guardándolo en ruta_destino.
    """
    
    # 1. Configurar Jinja2
    ruta_templates = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(ruta_templates))
    template = env.get_template('reporte.html')
    
    # 2. NUEVA LÓGICA: Agrupar ejercicios por DÍA
    rutina_por_dias = {}
    
    # Ordenamos primero por día para que salgan en orden (Semana 1 - Día 1, etc.)
    lista_ejercicios.sort(key=lambda x: x["dia"])
    
    for item in lista_ejercicios:
        dia = item["dia"]
        if dia not in rutina_por_dias:
            rutina_por_dias[dia] = []
        rutina_por_dias[dia].append(item)

    # 3. Preparar los datos para el HTML
    datos = {
        "nombre_cliente": nombre_cliente,
        "fase": fase,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
        "dias": rutina_por_dias  # Enviamos el diccionario agrupado
    }
    
    # 4. Renderizar HTML
    html_string = template.render(datos)
    
    # 5. Generar PDF en la ruta elegida por el usuario
    print(f"Generando PDF para {nombre_cliente} en {ruta_destino}...")
    HTML(string=html_string).write_pdf(ruta_destino)
    
    return ruta_destino


def generar_pdf_grafico(nombre_cliente, metrica, ruta_img, ruta_destino):
    """
    Genera un PDF exclusivo para el reporte de evolución (Gráfico).
    No necesita plantilla externa, usa un HTML inyectado.
    """
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    
    # Convertimos la ruta de la imagen a un formato URI que WeasyPrint pueda leer
    ruta_uri = pathlib.Path(ruta_img).as_uri() if ruta_img else ""
    
    html_string = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px; }}
            h1 {{ color: #2c3e50; font-size: 30px; }}
            h2 {{ color: #7f8c8d; font-size: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            img {{ max-width: 100%; height: auto; margin-top: 30px; border: 1px solid #ddd; border-radius: 8px; padding: 15px; }}
        </style>
    </head>
    <body>
        <h1>Reporte de Evolución Física</h1>
        <h2>Cliente: {nombre_cliente} | Métrica: {metrica} | Fecha: {fecha}</h2>
        <img src="{ruta_uri}" />
    </body>
    </html>
    """
    HTML(string=html_string).write_pdf(ruta_destino)
    return ruta_destino