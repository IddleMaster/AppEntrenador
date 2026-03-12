import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from database.models import Evaluacion, obtener_sesion
import os

def generar_grafico_progreso(cliente_id, tipo_dato="rm_sentadilla"):
    """
    Genera un gráfico de evolución (Ej: Fecha vs RM Sentadilla) y devuelve la ruta de la imagen.
    tipo_dato puede ser: 'peso', 'porcentaje_grasa', 'rm_sentadilla', 'rm_press_banca', etc.
    """
    session = obtener_sesion()
    
    # 1. Obtener historial ordenado por fecha
    evaluaciones = session.query(Evaluacion)\
        .filter_by(cliente_id=cliente_id)\
        .order_by(Evaluacion.fecha.asc())\
        .all()
    session.close()

    if not evaluaciones or len(evaluaciones) < 2:
        return None # Necesitamos al menos 2 puntos para una línea

    # 2. Extraer datos (Eje X = Fechas, Eje Y = Valor)
    fechas = [e.fecha for e in evaluaciones]
    valores = [getattr(e, tipo_dato) for e in evaluaciones] # getattr saca el valor dinámicamente

    # 3. Crear el Gráfico con Matplotlib
    plt.figure(figsize=(8, 4)) # Tamaño en pulgadas
    plt.plot(fechas, valores, marker='o', linestyle='-', color='#2ecc71', linewidth=2)
    
    # Decoración: Limpiamos el texto para que "rm" pase a "RM"
    titulo_limpio = tipo_dato.replace('_', ' ').title().replace('Rm', 'RM')
    plt.title(f"Evolución de {titulo_limpio}")
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m')) # Formato fecha día/mes
    plt.tight_layout()

    # 4. Guardar imagen temporal
    nombre_img = f"chart_{cliente_id}_{tipo_dato}.png"
    # Guardamos en la carpeta 'assets'
    ruta_assets = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    if not os.path.exists(ruta_assets):
        os.makedirs(ruta_assets)
        
    ruta_completa = os.path.join(ruta_assets, nombre_img)
    plt.savefig(ruta_completa)
    plt.close() # Cerrar para liberar memoria
    
    return ruta_completa