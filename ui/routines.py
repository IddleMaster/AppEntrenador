import flet as ft
from database.models import Cliente, Ejercicio, Evaluacion, obtener_sesion
from logic.calculations import calcular_cargas
from logic.pdf_generator import generar_pdf_rutina
import os

def RoutinesView(page: ft.Page):
    
    # Lista global
    sesion_actual = [] 

    def cargar_datos():
        session = obtener_sesion()
        clientes = session.query(Cliente).all()
        ejercicios = session.query(Ejercicio).all()
        session.close()
        
        cliente_dropdown.options.clear()
        for c in clientes:
            cliente_dropdown.options.append(ft.dropdown.Option(text=f"{c.nombre} {c.apellido}", key=str(c.id)))
            
        ejercicio_dropdown.options.clear()
        for e in ejercicios:
            ejercicio_dropdown.options.append(ft.dropdown.Option(text=e.nombre, key=str(e.id)))
        page.update()
    def filtrar_ejercicios_dropdown(e):
        session = obtener_sesion()
        # Empezamos con todos los ejercicios
        query = session.query(Ejercicio)
        
        # Filtramos por Categoría si seleccionó alguna
        if filtro_categoria.value and filtro_categoria.value != "Todos":
            query = query.filter(Ejercicio.categoria_implemento == filtro_categoria.value)
            
        # Filtramos por Músculo si seleccionó alguno
        if filtro_musculo.value and filtro_musculo.value != "Todos":
            query = query.filter(Ejercicio.grupo_muscular == filtro_musculo.value)
            
        ejercicios_filtrados = query.all()
        session.close()
        
        # Limpiamos y rellenamos el dropdown de ejercicios
        ejercicio_dropdown.options.clear()
        for ej in ejercicios_filtrados:
            ejercicio_dropdown.options.append(ft.dropdown.Option(text=ej.nombre, key=str(ej.id)))
            
        # Limpiamos la selección actual para evitar errores
        ejercicio_dropdown.value = None
        page.update()

    def agregar_ejercicio(e):
        # Validar también el DÍA
        if not cliente_dropdown.value or not ejercicio_dropdown.value or not fase_dropdown.value or not dia_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("Falta seleccionar Cliente, Fase, Día o Ejercicio"))
            page.snack_bar.open = True
            page.update()
            return

        id_ejercicio = ejercicio_dropdown.value
        nombre_ejercicio = [opt.text for opt in ejercicio_dropdown.options if opt.key == id_ejercicio][0]
        fase = fase_dropdown.value
        dia_seleccionado = dia_dropdown.value # <--- NUEVO
        
        # Obtener URL
        session = obtener_sesion()
        ej_db = session.query(Ejercicio).filter_by(id=id_ejercicio).first()
        url_video = ej_db.url_video if ej_db else ""
        
        # Buscar RM (Lógica inteligente)
        ultima_eval = session.query(Evaluacion).filter_by(cliente_id=int(cliente_dropdown.value)).order_by(Evaluacion.fecha.desc()).first()
        session.close()
        
        rm_usado = 0.0
        nombre_lower = nombre_ejercicio.lower()
        
        if ultima_eval:
            if "sentadilla" in nombre_lower: rm_usado = ultima_eval.rm_sentadilla
            elif "banca" in nombre_lower: rm_usado = ultima_eval.rm_press_banca
            elif "muerto" in nombre_lower: rm_usado = ultima_eval.rm_peso_muerto
            elif "hip" in nombre_lower: rm_usado = ultima_eval.rm_hip_thrust
            elif "curl" in nombre_lower: rm_usado = ultima_eval.rm_curl_biceps
            elif "dominada" in nombre_lower: rm_usado = ultima_eval.rm_dominadas

        rango_peso = calcular_cargas(rm_usado, fase) if rm_usado > 0 else "Manual / RPE"

        # Guardar datos INCLUYENDO EL DÍA
        item = {
            "dia": dia_seleccionado,  # <--- NUEVO
            "nombre": nombre_ejercicio,
            "series": series_field.value,
            "reps": reps_field.value,
            "peso": rango_peso,
            "url": url_video
        }
        sesion_actual.append(item)

        # Agregar a tabla visual
        fila = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(dia_seleccionado, weight="bold")), # Columna Día
                ft.DataCell(ft.Text(nombre_ejercicio)),
                ft.DataCell(ft.Text(series_field.value)),
                ft.DataCell(ft.Text(reps_field.value)),
                ft.DataCell(ft.Text(rango_peso)),
                ft.DataCell(ft.IconButton(icon=ft.icons.DELETE, icon_color="red", on_click=lambda e: borrar_fila(item)))
            ]
        )
        # Guardamos la referencia de la fila en el item para poder borrarla luego visualmente si hiciera falta, 
        # pero por simplicidad recargamos la tabla.
        actualizar_tabla_visual()
        
        page.update()

    def borrar_fila(item_a_borrar):
        if item_a_borrar in sesion_actual:
            sesion_actual.remove(item_a_borrar)
        actualizar_tabla_visual()

    def actualizar_tabla_visual():
        tabla_rutina.rows.clear()
        # Ordenar por día para que se vea bonito
        sesion_actual.sort(key=lambda x: x["dia"]) 
        
        # Función interna para guardar lo que tu amigo escriba
        def actualizar_peso_manual(e, item_actual):
            item_actual["peso"] = e.control.value

        for item in sesion_actual:
            # Creamos el campo de texto (ya sin el width aquí, se lo damos al contenedor)
            campo_carga = ft.TextField(
                value=item["peso"],  
                text_size=13,
                dense=True,
                border=ft.InputBorder.UNDERLINE, 
                content_padding=5,
                on_change=lambda e, i=item: actualizar_peso_manual(e, i)
            )

            fila = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item["dia"], color="blue", weight="bold")),
                    ft.DataCell(ft.Text(item["nombre"])),
                    ft.DataCell(ft.Text(item["series"])),
                    ft.DataCell(ft.Text(item["reps"])),
                    # MAGIA AQUI: Envolvemos el TextField en un Container con ancho estricto
                    ft.DataCell(ft.Container(content=campo_carga, width=150)), 
                    ft.DataCell(ft.IconButton(icon=ft.icons.DELETE, icon_color="red", on_click=lambda e, i=item: borrar_fila(i)))
                ]
            )
            tabla_rutina.rows.append(fila)
        page.update()
    def generar_pdf(e):
        if not cliente_dropdown.value or not sesion_actual:
            page.snack_bar = ft.SnackBar(ft.Text("Faltan datos"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        nombre_cliente = [opt.text for opt in cliente_dropdown.options if opt.key == cliente_dropdown.value][0]
        
        try:
            archivo = generar_pdf_rutina(nombre_cliente, fase_dropdown.value, sesion_actual)
            page.snack_bar = ft.SnackBar(ft.Text(f"PDF Creado: {archivo}"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
            os.startfile(archivo)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # --- UI ---
    titulo = ft.Text("Generador de Rutinas", size=30, weight="bold")
    
    btn_pdf = ft.ElevatedButton("Exportar PDF", icon=ft.icons.PICTURE_AS_PDF, bgcolor="red", color="white", on_click=generar_pdf)
    
    encabezado = ft.Row([titulo, btn_pdf], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    filtro_categoria = ft.Dropdown(
        label="Filtrar Categoría", width=150, 
        options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Gym"), ft.dropdown.Option("HomeGym"), ft.dropdown.Option("Calisthenics")],
        value="Todos", on_change=filtrar_ejercicios_dropdown
    )
    
    filtro_musculo = ft.Dropdown(
        label="Filtrar Músculo", width=150, 
        options=[
            ft.dropdown.Option("Todos"), 
            ft.dropdown.Option("Chest"), 
            ft.dropdown.Option("Back"), 
            ft.dropdown.Option("Legs (Quads)"), 
            ft.dropdown.Option("Hamstrings"),
            ft.dropdown.Option("Glutes"),    
            ft.dropdown.Option("Shoulders"),
            ft.dropdown.Option("Biceps"), 
            ft.dropdown.Option("Triceps"), 
            ft.dropdown.Option("Core/Abs")
        ],
        value="Todos", on_change=filtrar_ejercicios_dropdown
    )

    cliente_dropdown = ft.Dropdown(label="Cliente", width=300)
    fase_dropdown = ft.Dropdown(label="Fase", width=150, options=[
        ft.dropdown.Option("Ajuste"), ft.dropdown.Option("Carga"), 
        ft.dropdown.Option("Choque"), ft.dropdown.Option("Descarga")
    ])

    # NUEVO: Selector de Día
    dia_dropdown = ft.Dropdown(label="Día de Sesión", width=150, options=[
        ft.dropdown.Option("Día 1"), ft.dropdown.Option("Día 2"), 
        ft.dropdown.Option("Día 3"), ft.dropdown.Option("Día 4"),
        ft.dropdown.Option("Día 5"), ft.dropdown.Option("Extra")
    ])

    ejercicio_dropdown = ft.Dropdown(label="Ejercicio", width=300)
    series_field = ft.TextField(label="Series", width=70, value="4")
    reps_field = ft.TextField(label="Reps", width=70, value="10")
    
    btn_agregar = ft.ElevatedButton("Agregar", icon=ft.icons.ADD, bgcolor="green", color="white", on_click=agregar_ejercicio)

    tabla_rutina = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Día")), # Nueva columna
            ft.DataColumn(ft.Text("Ejercicio")),
            ft.DataColumn(ft.Text("Series")),
            ft.DataColumn(ft.Text("Reps")),
            ft.DataColumn(ft.Text("Carga")),
            ft.DataColumn(ft.Text("X")),
        ], rows=[]
    )
    
    

    contenido = ft.Column([
        encabezado, # <--- El encabezado con el botón está de lo primero
        ft.Row([cliente_dropdown, fase_dropdown]),
        ft.Divider(),
        ft.Text("Armar Bloque:", weight="bold"),
        ft.Row([dia_dropdown, filtro_categoria, filtro_musculo]), # Fila nueva con filtros
        ft.Row([ejercicio_dropdown, series_field, reps_field, btn_agregar]),
        ft.Divider(),
        tabla_rutina
        # Nota: Ya quitamos el ft.Row([btn_pdf]) que estaba aquí abajo
    ], scroll=ft.ScrollMode.AUTO, expand=True) # <-- expand=True es vital para el scroll
    
    cargar_datos()
    return contenido