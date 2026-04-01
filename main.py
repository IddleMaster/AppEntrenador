import flet as ft
# --- 1. PRIMERO LA BASE DE DATOS ---
from database.models import Base, engine 
import sqlite3

# --- 2. LUEGO LAS VISTAS ---
from database.models import Base, engine
from ui.clients import ClientesView
from ui.exercises import ExercisesView 
from ui.routines import RoutinesView
from ui.evaluations import EvaluationsView
from ui.calculators import CalculatorsView

def main(page: ft.Page):
    page.title = "Entrenador Pro v1.0"
    page.window.width = 1200
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT 
    
    def cambiar_ruta(e):
        index = e.control.selected_index
        contenido_principal.controls.clear()
        
        if index == 0: # Clientes
            contenido_principal.controls.append(ClientesView(page))
        elif index == 1: # Ejercicios
            contenido_principal.controls.append(ExercisesView(page))
        elif index == 2: # Evaluaciones
            contenido_principal.controls.append(EvaluationsView(page))
        elif index == 3: # Rutinas
            contenido_principal.controls.append(RoutinesView(page))
        elif index == 4: # Calculadoras
         contenido_principal.controls.append(CalculatorsView(page))
        
        page.update()

    # Menú Lateral corregido (Iconos como texto)
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon="people",             # ANTES: ft.icons.PEOPLE
                selected_icon="people_outline", 
                label="Clientes"
            ),
            ft.NavigationRailDestination(
                icon="fitness_center",     # ANTES: ft.icons.FITNESS_CENTER
                selected_icon="fitness_center_outlined", 
                label="Ejercicios"
            ),
            ft.NavigationRailDestination(
                icon="assessment",      # Icono de gráfico
                selected_icon="assessment_outlined", 
                label="Evaluaciones"
            ),
            ft.NavigationRailDestination(
                icon="library_books",      # ANTES: ft.icons.LIBRARY_BOOKS
                selected_icon="library_books_outlined", 
                label="Rutinas"
            ),
            ft.NavigationRailDestination(
             icon="calculate", 
             selected_icon="calculate_outlined", 
             label="Calculadoras"
         ),
        ],
        on_change=cambiar_ruta
    )

    contenido_principal = ft.Column(
        controls=[ClientesView(page)],
        expand=True,
    )

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                contenido_principal
            ],
            expand=True,
        )
    )
def asegurar_columnas():
    conn = sqlite3.connect('entrenador.db')
    c = conn.cursor()

    # Lista de todas las columnas nuevas que hemos ido agregando con el tiempo
    columnas_nuevas = [
        ("perimetro_brazos", "FLOAT"),
        ("perimetro_piernas", "FLOAT"),
        ("metodo_grasa", "TEXT"),
        ("suma_pliegues", "FLOAT")
    ]

    # Intentamos agregar una por una
    for nombre_col, tipo_col in columnas_nuevas:
        try:
            c.execute(f"ALTER TABLE evaluaciones ADD COLUMN {nombre_col} {tipo_col}")
        except Exception:
            # Si esta columna en específico ya existe, SQLite da error. 
            # Lo ignoramos con 'pass' y el bucle sigue con la próxima columna.
            pass 

    conn.commit()
    conn.close()

# --- Iniciar la app ---
asegurar_columnas()
Base.metadata.create_all(bind=engine)
ft.app(target=main)