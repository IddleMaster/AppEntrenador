import flet as ft
from database.models import Ejercicio, obtener_sesion

def ExercisesView(page: ft.Page):
    
    id_ejercicio_seleccionado = ft.Ref[int]()

    def guardar_o_actualizar(e):
        try:
            if not name_field.value:
                mostrar_mensaje("El nombre es obligatorio", "red")
                return

            session = obtener_sesion()
            
            if id_ejercicio_seleccionado.current is None:
                # CREAR
                nuevo = Ejercicio(
                    nombre=name_field.value,
                    url_video=url_field.value,
                    grupo_muscular=muscle_group_dropdown.value,
                    categoria_implemento=category_dropdown.value,
                    nivel_dificultad=difficulty_dropdown.value
                )
                session.add(nuevo)
                mostrar_mensaje("Ejercicio creado", "green")
            else:
                # ACTUALIZAR
                ej = session.query(Ejercicio).get(id_ejercicio_seleccionado.current)
                ej.nombre = name_field.value
                ej.url_video = url_field.value
                ej.grupo_muscular = muscle_group_dropdown.value
                ej.categoria_implemento = category_dropdown.value
                ej.nivel_dificultad = difficulty_dropdown.value
                mostrar_mensaje("Ejercicio actualizado", "green")
                
                # Reset UI
                cancelar_edicion(None)

            session.commit()
            session.close()
            limpiar_campos()
            cargar_tabla()
            
        except Exception as ex:
            mostrar_mensaje(f"Error: {str(ex)}", "red")

    def cargar_tabla(busqueda=""):
        session = obtener_sesion()
        
        # Si hay texto, filtramos. Si no, traemos todos.
        if busqueda:
            # ilike hace que no importe si escribe en mayúsculas o minúsculas
            exercises = session.query(Ejercicio).filter(Ejercicio.nombre.ilike(f"%{busqueda}%")).all()
        else:
            exercises = session.query(Ejercicio).all()
            
        tabla.rows.clear()
        
        for ex in exercises:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(ex.nombre)),
                    ft.DataCell(ft.Text(ex.grupo_muscular)),
                    ft.DataCell(ft.Text(ex.nivel_dificultad)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, icon_color="blue", on_click=lambda e, id=ex.id: editar(id)),
                        ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e, id=ex.id: eliminar(id)),
                    ]))
                ]
            )
            tabla.rows.append(row)
        session.close()
        page.update()

    def editar(id):
        session = obtener_sesion()
        ex = session.query(Ejercicio).get(id)
        session.close()
        
        name_field.value = ex.nombre
        url_field.value = ex.url_video
        muscle_group_dropdown.value = ex.grupo_muscular
        category_dropdown.value = ex.categoria_implemento
        difficulty_dropdown.value = ex.nivel_dificultad
        
        id_ejercicio_seleccionado.current = id
        save_btn.text = "Actualizar Ejercicio"
        save_btn.icon = ft.icons.UPDATE
        cancel_btn.visible = True
        page.update()

    def eliminar(id):
        session = obtener_sesion()
        ex = session.query(Ejercicio).get(id)
        session.delete(ex)
        session.commit()
        session.close()
        cargar_tabla()
        mostrar_mensaje("Ejercicio eliminado", "orange")

    def cancelar_edicion(e):
        id_ejercicio_seleccionado.current = None
        save_btn.text = "Guardar Ejercicio"
        save_btn.icon = ft.icons.SAVE
        cancel_btn.visible = False
        limpiar_campos()
        page.update()

    def limpiar_campos():
        name_field.value = ""
        url_field.value = ""

    def mostrar_mensaje(texto, color):
        page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # --- UI ---
    name_field = ft.TextField(label="Nombre Ejercicio", width=300)
    url_field = ft.TextField(label="YouTube URL", width=300, icon=ft.icons.VIDEO_LIBRARY)
    
    # Dropdowns (copia los mismos de antes)
    muscle_group_dropdown = ft.Dropdown(label="Grupo Muscular", width=300, options=[
        ft.dropdown.Option("Chest"), 
        ft.dropdown.Option("Back"), 
        ft.dropdown.Option("Legs (Quads)"),
        ft.dropdown.Option("Hamstrings"), 
        ft.dropdown.Option("Glutes"),     
        ft.dropdown.Option("Shoulders"), 
        ft.dropdown.Option("Biceps"), 
        ft.dropdown.Option("Triceps"), 
        ft.dropdown.Option("Core/Abs"),
        ft.dropdown.Option("Cardio")
    ])
    category_dropdown = ft.Dropdown(label="Categoría", width=300, options=[
        ft.dropdown.Option("Gym"), 
        ft.dropdown.Option("HomeGym"), 
        ft.dropdown.Option("Calisthenics")
    ])
    difficulty_dropdown = ft.Dropdown(label="Dificultad", width=300, options=[
        ft.dropdown.Option("Beginner"), ft.dropdown.Option("Intermediate"), ft.dropdown.Option("Advanced")
    ])

    save_btn = ft.ElevatedButton(text="Guardar Ejercicio", icon=ft.icons.SAVE, bgcolor="blue", color="white", on_click=guardar_o_actualizar)
    cancel_btn = ft.ElevatedButton(text="Cancelar", icon=ft.icons.CANCEL, bgcolor="grey", color="white", visible=False, on_click=cancelar_edicion)

    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("Nombre")),
        ft.DataColumn(ft.Text("Músculo")),
        ft.DataColumn(ft.Text("Nivel")),
        ft.DataColumn(ft.Text("Acciones")),
    ], rows=[])

    form_col = ft.Column([
        ft.Text("Biblioteca", size=20, weight="bold"),
        name_field, url_field, muscle_group_dropdown, category_dropdown, difficulty_dropdown,
        ft.Row([save_btn, cancel_btn])
    ], width=320)

    # Campo de búsqueda (se activa cada vez que el texto cambia)
    buscador = ft.TextField(
        label="🔍 Buscar Ejercicio...", 
        width=300,
        on_change=lambda e: cargar_tabla(e.control.value) # Llama a la tabla con el texto
    )

    # Actualiza la columna de la lista para incluir el buscador
    list_col = ft.Column([
        ft.Text("Base de Datos", size=20, weight="bold"), 
        buscador, # <--- Agregamos el buscador aquí
        ft.Row([tabla], scroll=ft.ScrollMode.ALWAYS)
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    contenido = ft.Row([
        ft.Container(form_col, padding=10, border=ft.border.only(right=ft.BorderSide(1, "grey"))),
        ft.Container(list_col, padding=10, expand=True)
    ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)

    cargar_tabla()
    return contenido