import flet as ft

def CalculatorsView(page: ft.Page):
    
    # --- Lógica RM ---
    def calcular_rm(e):
        try:
            p = float(peso_rm.value.replace(',', '.'))
            r = int(reps_rm.value)
            
            # Fórmulas
            rm_epley = p * (1 + 0.0333 * r)
            rm_brzycki = p * (36 / (37 - r)) if r < 37 else 0
            
            resultado_rm.value = f"Epley: {rm_epley:.1f} kg  |  Brzycki: {rm_brzycki:.1f} kg"
            resultado_rm.color = "green"
        except ValueError:
            resultado_rm.value = "Por favor, ingresa números válidos."
            resultado_rm.color = "red"
        page.update()

    # --- Lógica Porcentaje de Grasa (Fórmula Yuhasz 6 Pliegues) ---
    def calcular_grasa(e):
        try:
            suma = float(suma_pliegues.value.replace(',', '.'))
            
            if genero_calc.value == "Masculino":
                grasa = (0.1051 * suma) + 2.585
            else:
                grasa = (0.1548 * suma) + 3.580
                
            resultado_grasa.value = f"Grasa Corporal Estimada: {grasa:.1f}%"
            resultado_grasa.color = "blue"
        except ValueError:
            resultado_grasa.value = "Ingresa la suma total de los pliegues."
            resultado_grasa.color = "red"
        page.update()

    # --- UI RM ---
    peso_rm = ft.TextField(label="Peso Levantado (kg)", width=200)
    reps_rm = ft.TextField(label="Repeticiones logradas", width=200)
    btn_rm = ft.ElevatedButton("Calcular RM", on_click=calcular_rm, bgcolor="black", color="white")
    resultado_rm = ft.Text("Esperando datos...", size=18, weight="bold")
    
    tarjeta_rm = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text("Calculadora de Repetición Máxima (RM)", size=20, weight="bold"),
                ft.Text("Ingresa cuánto peso levantaste y cuántas repeticiones lograste (máx 12 para mayor precisión)."),
                ft.Row([peso_rm, reps_rm]),
                btn_rm,
                resultado_rm
            ])
        )
    )

    # --- UI Grasa Corporal ---
    genero_calc = ft.Dropdown(label="Género", options=[ft.dropdown.Option("Masculino"), ft.dropdown.Option("Femenino")], value="Masculino", width=200)
    suma_pliegues = ft.TextField(label="Suma de 6 Pliegues (mm)", width=200, tooltip="Tríceps, Subescapular, Supraespinal, Abdominal, Muslo frontal, Pantorrilla")
    btn_grasa = ft.ElevatedButton("Calcular % Grasa", on_click=calcular_grasa, bgcolor="black", color="white")
    resultado_grasa = ft.Text("Esperando datos...", size=18, weight="bold")

    tarjeta_grasa = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text("Calculadora de % de Grasa (Yuhasz 6 Pliegues)", size=20, weight="bold"),
                ft.Text("Mide los 6 pliegues con el caliper, súmalos e ingresa el total en milímetros."),
                ft.Row([genero_calc, suma_pliegues]),
                btn_grasa,
                resultado_grasa
            ])
        )
    )

    return ft.Column([
        ft.Text("Herramientas Deportivas", size=30, weight="bold"),
        ft.Divider(),
        tarjeta_rm,
        ft.Container(height=20),
        tarjeta_grasa
    ], scroll=ft.ScrollMode.AUTO, expand=True)