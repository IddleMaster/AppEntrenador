import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from database.models import Evaluacion, obtener_sesion
import os

def generar_grafico_progreso(cliente_id, tipo_dato="rm_sentadilla"):
    session = obtener_sesion()
    
    # 1. Obtener historial ordenado por fecha
    evaluaciones = session.query(Evaluacion)\
        .filter_by(cliente_id=cliente_id)\
        .order_by(Evaluacion.fecha.asc())\
        .all()
    session.close()

    if not evaluaciones or len(evaluaciones) < 2:
        return None # Necesitamos al menos 2 puntos para una línea

    fechas = [e.fecha for e in evaluaciones]

    # 3. Crear el Gráfico base
    fig, ax1 = plt.subplots(figsize=(8, 4)) # ax1 es el eje izquierdo

    # --- CASO ESPECIAL: GRÁFICO DOBLE (PESO Y GRASA) ---
    if tipo_dato == "peso_y_grasa":
        pesos = [e.peso for e in evaluaciones]
        grasas = [e.porcentaje_grasa for e in evaluaciones]

        # Dibujar Peso (Línea Azul - Eje Izquierdo)
        ax1.plot(fechas, pesos, marker='o', linestyle='-', color='#3498db', linewidth=2, label="Peso (kg)")
        ax1.set_ylabel("Peso (kg)", color='#3498db', weight='bold')
        ax1.tick_params(axis='y', labelcolor='#3498db')
        
        # Dibujar Grasa (Línea Roja - Eje Derecho)
        ax2 = ax1.twinx() # Magia: Crea un segundo eje Y compartiendo el mismo eje X
        ax2.plot(fechas, grasas, marker='s', linestyle='--', color='#e74c3c', linewidth=2, label="% Grasa")
        ax2.set_ylabel("% Grasa", color='#e74c3c', weight='bold')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')

        plt.title("Evolución de Peso y Porcentaje de Grasa", weight='bold', color='#2c3e50')
        
        # Juntar ambas leyendas para que se vean bonitas
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right")

    # --- CASO NORMAL: UNA SOLA LÍNEA (FUERZA / RMs) ---
    else:
        valores = [getattr(e, tipo_dato) for e in evaluaciones] 
        ax1.plot(fechas, valores, marker='o', linestyle='-', color='#2ecc71', linewidth=2)
        titulo_limpio = tipo_dato.replace('_', ' ').title().replace('Rm', 'RM')
        plt.title(f"Evolución de {titulo_limpio}", weight='bold', color='#2c3e50')

    # Decoración general
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m')) 
    fig.tight_layout()

    # 4. Guardar imagen temporal
    nombre_img = f"chart_{cliente_id}_{tipo_dato}.png"
    ruta_assets = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    if not os.path.exists(ruta_assets):
        os.makedirs(ruta_assets)
        
    ruta_completa = os.path.join(ruta_assets, nombre_img)
    plt.savefig(ruta_completa)
    plt.close() 
    
    return ruta_completa