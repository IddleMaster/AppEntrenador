import flet as ft
from database.models import Cliente, Ejercicio, Evaluacion, obtener_sesion
from logic.calculations import calcular_cargas
from logic.pdf_generator import generar_pdf_rutina
import os

# --- 1. PERMANENCIA DE DATOS ---
rutina_mensual = {
    "Semana 1": [],
    "Semana 2": [],
    "Semana 3": [],
    "Semana 4": []
}
semana_activa = ["Semana 1"]

def RoutinesView(page: ft.Page):

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
        query = session.query(Ejercicio)
        
        if filtro_categoria.value and filtro_categoria.value != "Todos":
            query = query.filter(Ejercicio.categoria_implemento == filtro_categoria.value)
            
        if filtro_musculo.value and filtro_musculo.value != "Todos":
            query = query.filter(Ejercicio.grupo_muscular == filtro_musculo.value)
            
        if filtro_dificultad.value and filtro_dificultad.value != "Todos":
            query = query.filter(Ejercicio.nivel_dificultad == filtro_dificultad.value)
            
        ejercicios_filtrados = query.all()
        session.close()
        
        ejercicio_dropdown.options.clear()
        for ej in ejercicios_filtrados:
            ejercicio_dropdown.options.append(ft.dropdown.Option(text=ej.nombre, key=str(ej.id)))
            
        ejercicio_dropdown.value = None
        page.update()

    def agregar_ejercicio(e):
        try: 
            if not cliente_dropdown.value or not ejercicio_dropdown.value or not fase_dropdown.value or not dia_dropdown.value:
                page.snack_bar = ft.SnackBar(ft.Text("Faltan datos por seleccionar"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            id_ejercicio = ejercicio_dropdown.value
            nombre_ejercicio = [opt.text for opt in ejercicio_dropdown.options if opt.key == id_ejercicio][0]
            fase = fase_dropdown.value
            dia_seleccionado = dia_dropdown.value
            
            session = obtener_sesion()
            ej_db = session.query(Ejercicio).filter_by(id=id_ejercicio).first()
            url_video = ej_db.url_video if ej_db else ""
            
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

            item = {
                "dia": dia_seleccionado,
                "nombre": nombre_ejercicio,
                "series": series_field.value,
                "reps": reps_field.value,
                "descanso": descanso_field.value, 
                "peso": rango_peso,
                "url": url_video
            }
            
            rutina_mensual[semana_activa[0]].append(item)
            actualizar_tabla_visual()
            
            page.snack_bar = ft.SnackBar(ft.Text(f"Agregado a {semana_activa[0]}"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al agregar: {str(ex)}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def borrar_fila(item_a_borrar):
        if item_a_borrar in rutina_mensual[semana_activa[0]]:
            rutina_mensual[semana_activa[0]].remove(item_a_borrar)
        actualizar_tabla_visual()

    def actualizar_tabla_visual():
        tabla_rutina.rows.clear()
        lista_actual = rutina_mensual[semana_activa[0]]
        lista_actual.sort(key=lambda x: x["dia"]) 
        
        def actualizar_peso_manual(e, item_actual):
            item_actual["peso"] = e.control.value

        def actualizar_descanso_manual(e, item_actual):
            item_actual["descanso"] = e.control.value

        for item in lista_actual:
            campo_carga = ft.TextField(
                value=item["peso"],  
                width=120, text_size=13, dense=True, 
                border=ft.InputBorder.UNDERLINE, content_padding=5,
                on_change=lambda e, i=item: actualizar_peso_manual(e, i)
            )
            
            campo_descanso = ft.TextField(
                value=item.get("descanso", "90s"),  
                width=80, text_size=13, dense=True, 
                border=ft.InputBorder.UNDERLINE, content_padding=5,
                on_change=lambda e, i=item: actualizar_descanso_manual(e, i)
            )

            fila = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item["dia"], color="blue", weight="bold")),
                    ft.DataCell(ft.Text(item["nombre"])),
                    ft.DataCell(ft.Text(item["series"])),
                    ft.DataCell(ft.Text(item["reps"])),
                    ft.DataCell(ft.Container(content=campo_descanso, width=80)), 
                    ft.DataCell(ft.Container(content=campo_carga, width=120)),   
                    ft.DataCell(ft.IconButton(icon=ft.icons.DELETE, icon_color="red", on_click=lambda e, i=item: borrar_fila(i)))
                ]
            )
            tabla_rutina.rows.append(fila)
        page.update()

    def cambiar_semana(e):
        semanas = ["Semana 1", "Semana 2", "Semana 3", "Semana 4"]
        semana_activa[0] = semanas[e.control.selected_index]
        actualizar_tabla_visual()

    # --- LÓGICA DE EXPORTACIÓN ARREGLADA ---
    def guardar_pdf_dialog(e: ft.FilePickerResultEvent):
        if not e.path: return 
        
        if not cliente_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("Falta seleccionar cliente"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        nombre_cliente = [opt.text for opt in cliente_dropdown.options if opt.key == cliente_dropdown.value][0]
        
        try:
            rutina_plana = []
            for sem, items in rutina_mensual.items():
                for i in items:
                    i_copia = i.copy()
                    i_copia["dia"] = f"{sem} - {i['dia']}"
                    rutina_plana.append(i_copia)
            
            # ¡AQUÍ ESTÁ LA MAGIA! Le pasamos e.path como 4to argumento
            archivo = generar_pdf_rutina(nombre_cliente, fase_dropdown.value, rutina_plana, e.path)
            
            page.snack_bar = ft.SnackBar(ft.Text(f"PDF guardado exitosamente"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
            os.startfile(archivo)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al exportar: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    file_picker = ft.FilePicker(on_result=guardar_pdf_dialog)
    page.overlay.append(file_picker)

    def abrir_guardar_como(e):
        file_picker.save_file(dialog_title="Guardar PDF como...", file_name="Rutina_Mensual.pdf", allowed_extensions=["pdf"])

    # --- UI ---
    titulo = ft.Text("Generador de Rutinas Pro", size=30, weight="bold")
    btn_pdf = ft.ElevatedButton("Exportar PDF", icon=ft.icons.PICTURE_AS_PDF, bgcolor="red", color="white", on_click=abrir_guardar_como)
    encabezado = ft.Row([titulo, btn_pdf], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # ¡CARDIO ELIMINADO DE CATEGORÍA!
    filtro_categoria = ft.Dropdown(
        label="Categoría", width=150, 
        options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Gym"), ft.dropdown.Option("HomeGym"), ft.dropdown.Option("Calisthenics")],
        value="Todos", on_change=filtrar_ejercicios_dropdown
    )
    
    # ¡CARDIO AGREGADO A MÚSCULO!
    filtro_musculo = ft.Dropdown(
        label="Músculo", width=150, 
        options=[
            ft.dropdown.Option("Todos"), ft.dropdown.Option("Chest"), ft.dropdown.Option("Back"), 
            ft.dropdown.Option("Legs (Quads)"), ft.dropdown.Option("Hamstrings"), ft.dropdown.Option("Glutes"),    
            ft.dropdown.Option("Shoulders"), ft.dropdown.Option("Biceps"), ft.dropdown.Option("Triceps"), 
            ft.dropdown.Option("Core/Abs"), ft.dropdown.Option("Cardio") 
        ], value="Todos", on_change=filtrar_ejercicios_dropdown
    )

    filtro_dificultad = ft.Dropdown(
        label="Dificultad", width=150,
        options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Beginner"), ft.dropdown.Option("Intermediate"), ft.dropdown.Option("Advanced")],
        value="Todos", on_change=filtrar_ejercicios_dropdown
    )

    cliente_dropdown = ft.Dropdown(label="Cliente", width=300)
    fase_dropdown = ft.Dropdown(label="Fase", width=150, options=[
        ft.dropdown.Option("Ajuste"), ft.dropdown.Option("Carga"), ft.dropdown.Option("Choque"), ft.dropdown.Option("Descarga")
    ])

    dia_dropdown = ft.Dropdown(label="Día de Sesión", width=130, options=[
        ft.dropdown.Option("Día 1"), ft.dropdown.Option("Día 2"), 
        ft.dropdown.Option("Día 3"), ft.dropdown.Option("Día 4"), ft.dropdown.Option("Día 5")
    ])

    ejercicio_dropdown = ft.Dropdown(label="Ejercicio", width=300)
    series_field = ft.TextField(label="Series", width=70, value="4")
    reps_field = ft.TextField(label="Reps", width=70, value="10")
    descanso_field = ft.TextField(label="Descanso", width=80, value="90s")
    
    btn_agregar = ft.ElevatedButton("Agregar", icon=ft.icons.ADD, bgcolor="green", color="white", on_click=agregar_ejercicio)

    tabs_semanas = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[ft.Tab(text="Semana 1"), ft.Tab(text="Semana 2"), ft.Tab(text="Semana 3"), ft.Tab(text="Semana 4")],
        on_change=cambiar_semana
    )

    tabla_rutina = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Día")), 
            ft.DataColumn(ft.Text("Ejercicio")),
            ft.DataColumn(ft.Text("Series")),
            ft.DataColumn(ft.Text("Reps")),
            ft.DataColumn(ft.Text("Descanso")),
            ft.DataColumn(ft.Text("Carga")),
            ft.DataColumn(ft.Text("X")),
        ], rows=[]
    )

    contenido = ft.Column([
        encabezado, 
        ft.Row([cliente_dropdown, fase_dropdown]),
        ft.Divider(),
        ft.Text("Armar Bloque Semanal:", weight="bold", color="blue"),
        ft.Row([dia_dropdown, filtro_categoria, filtro_musculo, filtro_dificultad]), 
        ft.Row([ejercicio_dropdown, series_field, reps_field, descanso_field, btn_agregar]),
        ft.Divider(),
        tabs_semanas, 
        tabla_rutina
    ], scroll=ft.ScrollMode.AUTO, expand=True) 
    
    cargar_datos()
    actualizar_tabla_visual() 
    return contenido