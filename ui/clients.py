import flet as ft
from database.models import Cliente, obtener_sesion

def ClientesView(page: ft.Page):
    
    # Variable para saber si estamos editando (None) o creando (ID)
    id_cliente_seleccionado = ft.Ref[int]()
    
    # --- Lógica CRUD ---
    def guardar_o_actualizar(e):
        try:
            if not rut_field.value or not nombre_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("RUT y Nombre obligatorios"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            session = obtener_sesion()
            
            if id_cliente_seleccionado.current is None:
                # MODO CREAR
                nuevo = Cliente(
                    rut=rut_field.value,
                    nombre=nombre_field.value,
                    apellido=apellido_field.value,
                    correo=correo_field.value,
                    telefono=telefono_field.value,
                    genero=genero_dropdown.value,
                    estatura=float(estatura_field.value) if estatura_field.value else 0.0,
                    peso_actual=float(peso_field.value) if peso_field.value else 0.0
                )
                session.add(nuevo)
                mensaje = "Cliente creado con éxito"
            else:
                # MODO ACTUALIZAR
                cliente = session.query(Cliente).get(id_cliente_seleccionado.current)
                cliente.rut = rut_field.value
                cliente.nombre = nombre_field.value
                cliente.apellido = apellido_field.value
                cliente.correo = correo_field.value
                cliente.telefono = telefono_field.value
                cliente.genero = genero_dropdown.value
                cliente.estatura = float(estatura_field.value) if estatura_field.value else 0.0
                cliente.peso_actual = float(peso_field.value) if peso_field.value else 0.0
                mensaje = "Cliente actualizado correctamente"
                
                # Resetear modo
                id_cliente_seleccionado.current = None
                boton_guardar.text = "Guardar Nuevo Socio"
                boton_guardar.icon = ft.icons.SAVE
                boton_cancelar.visible = False

            session.commit()
            session.close()
            
            limpiar_formulario()
            cargar_tabla()
            
            page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor="green")
            page.snack_bar.open = True
            page.update()
            
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def cargar_tabla():
        session = obtener_sesion()
        clientes = session.query(Cliente).all()
        
        tabla_clientes.rows.clear()
        for c in clientes:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(c.rut)),
                    ft.DataCell(ft.Text(f"{c.nombre} {c.apellido}")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.EDIT, icon_color="blue", on_click=lambda e, id=c.id: editar_cliente(id)),
                        ft.IconButton(icon=ft.icons.DELETE, icon_color="red", on_click=lambda e, id=c.id: eliminar_cliente(id)),
                    ]))
                ]
            )
            tabla_clientes.rows.append(row)
        
        session.close()
        page.update()

    def editar_cliente(id):
        session = obtener_sesion()
        c = session.query(Cliente).get(id)
        session.close()
        
        # Rellenar campos
        rut_field.value = c.rut
        nombre_field.value = c.nombre
        apellido_field.value = c.apellido
        correo_field.value = c.correo
        telefono_field.value = c.telefono
        genero_dropdown.value = c.genero
        estatura_field.value = str(c.estatura)
        peso_field.value = str(c.peso_actual)
        
        # Cambiar estado del botón
        id_cliente_seleccionado.current = id
        boton_guardar.text = "Actualizar Cliente"
        boton_guardar.icon = ft.icons.UPDATE
        boton_cancelar.visible = True
        page.update()

    def cancelar_edicion(e):
        limpiar_formulario()
        id_cliente_seleccionado.current = None
        boton_guardar.text = "Guardar Nuevo Socio"
        boton_guardar.icon = ft.icons.SAVE
        boton_cancelar.visible = False
        page.update()

    def eliminar_cliente(id):
        try:
            session = obtener_sesion()
            c = session.query(Cliente).get(id)
            session.delete(c)
            session.commit()
            session.close()
            cargar_tabla()
            page.snack_bar = ft.SnackBar(ft.Text("Cliente eliminado"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text("Error: No se puede eliminar si tiene rutinas asociadas"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def limpiar_formulario():
        rut_field.value = ""
        nombre_field.value = ""
        apellido_field.value = ""
        correo_field.value = ""
        telefono_field.value = ""
        estatura_field.value = ""
        peso_field.value = ""

    # --- Elementos UI ---
    rut_field = ft.TextField(label="RUT (ID)", width=250)
    nombre_field = ft.TextField(label="Nombre", width=250)
    apellido_field = ft.TextField(label="Apellido", width=250)
    correo_field = ft.TextField(label="Correo", width=250)
    telefono_field = ft.TextField(label="Teléfono", width=250)
    genero_dropdown = ft.Dropdown(label="Género", width=250, options=[ft.dropdown.Option("Masculino"), ft.dropdown.Option("Femenino")])
    estatura_field = ft.TextField(label="Estatura", width=120)
    peso_field = ft.TextField(label="Peso", width=120)

    boton_guardar = ft.ElevatedButton(text="Guardar Nuevo Socio", icon=ft.icons.SAVE, bgcolor="blue", color="white", on_click=guardar_o_actualizar)
    boton_cancelar = ft.ElevatedButton(text="Cancelar Edición", icon=ft.icons.CANCEL, bgcolor="grey", color="white", visible=False, on_click=cancelar_edicion)

    tabla_clientes = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("RUT")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    form_col = ft.Column([
        ft.Text("Datos del Cliente", size=20, weight="bold"),
        rut_field, nombre_field, apellido_field, correo_field, telefono_field, genero_dropdown,
        ft.Row([estatura_field, peso_field]),
        ft.Row([boton_guardar, boton_cancelar])
    ], scroll=ft.ScrollMode.AUTO, width=300)

    list_col = ft.Column([
        ft.Text("Listado de Socios", size=20, weight="bold"),
        # Envolvemos la tabla de clientes igual que hicimos con evaluaciones
        ft.Row([tabla_clientes], scroll=ft.ScrollMode.ALWAYS) 
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    contenido = ft.Row([
        ft.Container(content=form_col, padding=10, border=ft.border.only(right=ft.BorderSide(1, "grey"))),
        ft.Container(content=list_col, padding=10, expand=True)
    ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)

    cargar_tabla()
    return contenido