import os
import sys
from logic.charts import generar_grafico_progreso
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

def generar_pdf_rutina(nombre_cliente, fase, lista_ejercicios):
    """
    Genera un PDF con la rutina organizada por DÍAS.
    lista_ejercicios: Lista de diccionarios que incluyen la clave "dia"
    """
    
    # 1. Configurar Jinja2
    ruta_templates = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(ruta_templates))
    template = env.get_template('reporte.html')
    
    # 2. Buscar ID del cliente (para el gráfico)
    session = obtener_sesion()
    cliente_id = None
    try:
        # Asumimos que el nombre viene como "Nombre Apellido"
        primer_nombre = nombre_cliente.split(" ")[0]
        cliente = session.query(Cliente).filter(Cliente.nombre.like(f"%{primer_nombre}%")).first()
        if cliente:
            cliente_id = cliente.id
    except Exception as e:
        print(f"Error buscando cliente: {e}")
    finally:
        session.close()

    # 3. Generar el Gráfico de Progreso
    ruta_grafico = ""
    if cliente_id:
        # Genera gráfico de RM Sentadilla (puedes cambiarlo si quieres)
        ruta_grafico_generada = generar_grafico_progreso(cliente_id, "rm_sentadilla")
        
        # Convertir a formato URI para WeasyPrint
        if ruta_grafico_generada:
            ruta_grafico = pathlib.Path(ruta_grafico_generada).as_uri()

    # --- 4. NUEVA LÓGICA: Agrupar ejercicios por DÍA ---
    rutina_por_dias = {}
    
    # Ordenamos primero por día para que salgan en orden (Día 1, Día 2...)
    # Nota: lista_ejercicios viene de routines.py y cada item tiene la clave "dia"
    lista_ejercicios.sort(key=lambda x: x["dia"])
    
    for item in lista_ejercicios:
        dia = item["dia"]
        if dia not in rutina_por_dias:
            rutina_por_dias[dia] = []
        rutina_por_dias[dia].append(item)
    # ---------------------------------------------------

    # 5. Preparar los datos para el HTML
    datos = {
        "nombre_cliente": nombre_cliente,
        "fase": fase,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
        "dias": rutina_por_dias,  # <--- IMPORTANTE: Enviamos el diccionario agrupado, NO la lista plana
        "grafico": ruta_grafico
    }
    
    # 6. Renderizar HTML
    html_string = template.render(datos)
    
    # 7. Crear nombre de archivo
    nombre_limpio = nombre_cliente.replace(" ", "_")
    nombre_archivo = f"Rutina_{nombre_limpio}_{fase}.pdf"
    
    # 8. Generar PDF
    print(f"Generando PDF para {nombre_cliente}...")
    HTML(string=html_string).write_pdf(nombre_archivo)
    
    return nombre_archivo