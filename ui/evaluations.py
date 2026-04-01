import flet as ft
from database.models import Cliente, Evaluacion, obtener_sesion
from logic.charts import generar_grafico_progreso
from logic.pdf_generator import generar_pdf_grafico # <--- IMPORTAMOS EL NUEVO GENERADOR
import datetime
import os
import base64

def EvaluationsView(page: ft.Page):
    
    id_eval_seleccionada = ft.Ref[int]()
    MAPEO_GRAFICOS = {
        "Peso y % Grasa": "peso_y_grasa", # <--- ESTO ES LO QUE CAMBIÓ
        "RM Sentadilla": "rm_sentadilla",
        "RM Banca": "rm_press_banca",
        "RM Muerto": "rm_peso_muerto",
        "RM Hip Thrust": "rm_hip_thrust",
        "RM Bíceps": "rm_curl_biceps",
        "RM Dominadas": "rm_dominadas"
    }

    cliente_dropdown = ft.Dropdown(label="Seleccionar Cliente", width=400)
    peso_field = ft.TextField(label="Peso (kg)", width=120) 
    imc_field = ft.TextField(label="IMC", width=120, disabled=True, color="blue")
    grasa_field = ft.TextField(label="% Grasa", width=120)
    metodo_grasa_dropdown = ft.Dropdown(label="Método % Grasa", width=180, options=[ft.dropdown.Option("Bioimpedancia"), ft.dropdown.Option("Pliegues Cutáneos")], value="Bioimpedancia")
    pliegues_field = ft.TextField(label="Suma Pliegues", width=140)
    brazos_field = ft.TextField(label="Brazo (cm)", width=120)
    piernas_field = ft.TextField(label="Pierna (cm)", width=120)
    cintura_field = ft.TextField(label="Cintura (cm)", width=120)
    cadera_field = ft.TextField(label="Cadera (cm)", width=120)
    rm_sentadilla = ft.TextField(label="RM Sentadilla", width=140)
    rm_banca = ft.TextField(label="RM Banca", width=140)
    rm_muerto = ft.TextField(label="RM Muerto", width=140)
    rm_hip = ft.TextField(label="RM Hip Thrust", width=140)
    rm_curl = ft.TextField(label="RM Bíceps", width=140)
    rm_dominadas = ft.TextField(label="RM Dominadas", width=140)

    btn_guardar = ft.ElevatedButton("Guardar Evaluación", icon=ft.icons.SAVE, bgcolor="blue", color="white")
    btn_cancelar = ft.ElevatedButton("Cancelar Edición", icon=ft.icons.CANCEL, bgcolor="grey", color="white", visible=False)

    def safe_float(valor):
        if not valor: return 0.0
        try: return float(str(valor).replace(',', '.'))
        except ValueError: return 0.0

    def calcular_imc_dinamico(e):
        if not cliente_dropdown.value or not peso_field.value: return
        try:
            session = obtener_sesion()
            cliente = session.query(Cliente).get(int(cliente_dropdown.value))
            session.close()
            peso = safe_float(peso_field.value)
            if cliente and cliente.estatura > 0:
                imc = peso / (cliente.estatura ** 2)
                imc_field.value = f"{imc:.1f}"
                page.update()
        except Exception: pass

    peso_field.on_change = calcular_imc_dinamico

    def limpiar_formulario():
        for field in [peso_field, imc_field, grasa_field, pliegues_field, brazos_field, piernas_field, cintura_field, cadera_field, rm_sentadilla, rm_banca, rm_muerto, rm_hip, rm_curl, rm_dominadas]:
            field.value = ""
        id_eval_seleccionada.current = None
        btn_guardar.text = "Guardar Evaluación"
        btn_guardar.icon = ft.icons.SAVE
        btn_cancelar.visible = False
        page.update()

    btn_cancelar.on_click = lambda e: limpiar_formulario()

    def cargar_clientes():
        session = obtener_sesion()
        clientes = session.query(Cliente).all()
        session.close()
        cliente_dropdown.options.clear()
        for c in clientes:
            cliente_dropdown.options.append(ft.dropdown.Option(text=f"{c.nombre} {c.apellido}", key=str(c.id)))
        page.update()

    def guardar_evaluacion(e):
        if not cliente_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona un cliente primero"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        try:
            session = obtener_sesion()
            if id_eval_seleccionada.current is None:
                ev = Evaluacion(
                    cliente_id=int(cliente_dropdown.value), fecha=datetime.datetime.now(),
                    peso=safe_float(peso_field.value), imc=safe_float(imc_field.value),
                    porcentaje_grasa=safe_float(grasa_field.value), metodo_grasa=metodo_grasa_dropdown.value,
                    suma_pliegues=safe_float(pliegues_field.value), perimetro_brazos=safe_float(brazos_field.value),
                    perimetro_piernas=safe_float(piernas_field.value), perimetro_cintura=safe_float(cintura_field.value),
                    perimetro_cadera=safe_float(cadera_field.value), rm_sentadilla=safe_float(rm_sentadilla.value),
                    rm_press_banca=safe_float(rm_banca.value), rm_peso_muerto=safe_float(rm_muerto.value),
                    rm_hip_thrust=safe_float(rm_hip.value), rm_curl_biceps=safe_float(rm_curl.value), rm_dominadas=safe_float(rm_dominadas.value)
                )
                session.add(ev)
                mensaje = "Evaluación Guardada"
            else:
                ev = session.query(Evaluacion).get(id_eval_seleccionada.current)
                ev.peso = safe_float(peso_field.value)
                ev.imc = safe_float(imc_field.value)
                ev.porcentaje_grasa = safe_float(grasa_field.value)
                ev.metodo_grasa = metodo_grasa_dropdown.value
                ev.suma_pliegues = safe_float(pliegues_field.value)
                ev.perimetro_brazos = safe_float(brazos_field.value)
                ev.perimetro_piernas = safe_float(piernas_field.value)
                ev.perimetro_cintura = safe_float(cintura_field.value)
                ev.perimetro_cadera = safe_float(cadera_field.value)
                ev.rm_sentadilla = safe_float(rm_sentadilla.value)
                ev.rm_press_banca = safe_float(rm_banca.value)
                ev.rm_peso_muerto = safe_float(rm_muerto.value)
                ev.rm_hip_thrust = safe_float(rm_hip.value)
                ev.rm_curl_biceps = safe_float(rm_curl.value)
                ev.rm_dominadas = safe_float(rm_dominadas.value)
                mensaje = "Evaluación Actualizada"
            session.commit()
            session.close()
            page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor="green")
            page.snack_bar.open = True
            limpiar_formulario()
            cargar_historial(None) 
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    btn_guardar.on_click = guardar_evaluacion

    def editar_eval(id_eval):
        session = obtener_sesion()
        ev = session.query(Evaluacion).get(id_eval)
        session.close()

        peso_field.value = str(ev.peso)
        imc_field.value = str(ev.imc or 0.0)
        grasa_field.value = str(ev.porcentaje_grasa)
        metodo_grasa_dropdown.value = ev.metodo_grasa or "Bioimpedancia"
        pliegues_field.value = str(ev.suma_pliegues or 0.0)
        brazos_field.value = str(ev.perimetro_brazos or 0.0)
        piernas_field.value = str(ev.perimetro_piernas or 0.0)
        cintura_field.value = str(ev.perimetro_cintura or 0.0)
        cadera_field.value = str(ev.perimetro_cadera or 0.0)
        rm_sentadilla.value = str(ev.rm_sentadilla)
        rm_banca.value = str(ev.rm_press_banca)
        rm_muerto.value = str(ev.rm_peso_muerto)
        rm_hip.value = str(ev.rm_hip_thrust)
        rm_curl.value = str(ev.rm_curl_biceps)
        rm_dominadas.value = str(ev.rm_dominadas)

        id_eval_seleccionada.current = id_eval
        btn_guardar.text = "Actualizar"
        btn_guardar.icon = ft.icons.UPDATE
        btn_cancelar.visible = True
        page.update()

    def eliminar_eval(id_eval):
        session = obtener_sesion()
        ev = session.query(Evaluacion).get(id_eval)
        session.delete(ev)
        session.commit()
        session.close()
        page.snack_bar = ft.SnackBar(ft.Text("Evaluación Eliminada"), bgcolor="orange")
        page.snack_bar.open = True
        cargar_historial(None)

    def cargar_grafico(e=None):
        if not cliente_dropdown.value: return
        cliente_id = int(cliente_dropdown.value)
        columna_db = MAPEO_GRAFICOS.get(tipo_grafico_dropdown.value, "rm_sentadilla")
        ruta_img = generar_grafico_progreso(cliente_id, columna_db)
        
        if ruta_img and os.path.exists(ruta_img):
            with open(ruta_img, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            contenedor_grafico.content = ft.Image(src_base64=encoded_string, width=700, height=350, fit=ft.ImageFit.CONTAIN)
        else:
            contenedor_grafico.content = ft.Text("Faltan evaluaciones para generar gráfico.", italic=True, color="grey")
        page.update()

    def cargar_historial(e):
        if not cliente_dropdown.value: return
        session = obtener_sesion()
        evals = session.query(Evaluacion).filter_by(cliente_id=int(cliente_dropdown.value)).order_by(Evaluacion.fecha.desc()).all()
        dias_semana = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
        tabla_historial.rows.clear()
        
        for ev in evals:
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"{dias_semana[ev.fecha.weekday()]}, {ev.fecha.strftime('%d/%m')}")),
                ft.DataCell(ft.Text(f"{ev.peso} kg")), ft.DataCell(ft.Text(f"{ev.rm_sentadilla}")),
                ft.DataCell(ft.Text(f"{ev.rm_press_banca}")), ft.DataCell(ft.Text(f"{ev.rm_peso_muerto}")),
                ft.DataCell(ft.Text(f"{ev.rm_hip_thrust}")), ft.DataCell(ft.Text(f"{ev.rm_curl_biceps}")),
                ft.DataCell(ft.Text(f"{ev.rm_dominadas}")),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.icons.EDIT, icon_color="blue", on_click=lambda e, id=ev.id: editar_eval(id)),
                    ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e, id=ev.id: eliminar_eval(id))
                ]))
            ])
            tabla_historial.rows.append(row)
        session.close()
        cargar_grafico()

    cliente_dropdown.on_change = cargar_historial

    # --- NUEVA LÓGICA DE EXPORTAR GRÁFICO (FILEPICKER) ---
    def guardar_grafico_dialog(e: ft.FilePickerResultEvent):
        if not e.path or not cliente_dropdown.value: return
        nombre_cliente = [opt.text for opt in cliente_dropdown.options if opt.key == cliente_dropdown.value][0]
        metrica = tipo_grafico_dropdown.value
        cliente_id = int(cliente_dropdown.value)
        columna_db = MAPEO_GRAFICOS.get(metrica, "rm_sentadilla")
        
        ruta_img = generar_grafico_progreso(cliente_id, columna_db)
        try:
            generar_pdf_grafico(nombre_cliente, metrica, ruta_img, e.path)
            page.snack_bar = ft.SnackBar(ft.Text("Gráfico exportado exitosamente"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
            os.startfile(e.path)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    file_picker_eval = ft.FilePicker(on_result=guardar_grafico_dialog)
    page.overlay.append(file_picker_eval)

    def abrir_exportar_grafico(e):
        if not cliente_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona un cliente primero", color="red"))
            page.snack_bar.open = True
            page.update()
            return
        file_picker_eval.save_file(dialog_title="Guardar Gráfico como PDF...", file_name="Reporte_Evolucion.pdf", allowed_extensions=["pdf"])

    tipo_grafico_dropdown = ft.Dropdown(label="Métrica", width=200, options=[ft.dropdown.Option(k) for k in MAPEO_GRAFICOS.keys()], value="RM Sentadilla", on_change=cargar_grafico)
    btn_exportar_grafico = ft.ElevatedButton("Exportar a PDF", icon=ft.icons.PICTURE_AS_PDF, bgcolor="red", color="white", on_click=abrir_exportar_grafico)
    
    contenedor_grafico = ft.Container(padding=10, alignment=ft.alignment.center)
    tabla_historial = ft.DataTable(columns=[ft.DataColumn(ft.Text(x, weight="bold")) for x in ["Fecha","Peso","Sentadilla","Banca","Muerto","Hip","Bíceps","Dominadas","Acciones"]], rows=[])
    tabla_con_scroll = ft.Row([tabla_historial], scroll=ft.ScrollMode.ALWAYS)

    cabecera_grafico = ft.Row([
        ft.Text("Análisis de Progreso", size=20, weight="bold"),
        ft.Row([tipo_grafico_dropdown, btn_exportar_grafico]) # <--- AQUI AGREGAMOS EL BOTON
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    columna_principal = ft.Column([
        ft.Text("Registro y Progreso de Evaluaciones", size=30, weight="bold"),
        cliente_dropdown, ft.Divider(),
        ft.Text("1. Datos Corporales y Antropometría", weight="bold", color="blue"),
        ft.Row([peso_field, imc_field, grasa_field, metodo_grasa_dropdown, pliegues_field]),
        ft.Row([cintura_field, cadera_field, brazos_field, piernas_field]),
        ft.Text("2. Fuerza Máxima (RMs)", weight="bold", color="blue"),
        ft.Row([rm_sentadilla, rm_banca, rm_muerto]), ft.Row([rm_hip, rm_curl, rm_dominadas]),
        ft.Container(height=10), ft.Row([btn_guardar, btn_cancelar]), ft.Divider(),
        cabecera_grafico, contenedor_grafico,
        ft.Text("Historial Completo", size=20, weight="bold"), tabla_con_scroll
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    cargar_clientes()
    return columna_principal