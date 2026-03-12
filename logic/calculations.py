def calcular_cargas(rm_cliente, tipo_semana):
    """
    Calcula el rango de peso sugerido basado en el RM y la fase.
    rm_cliente: Float (ej: 100.0)
    tipo_semana: Str ("Ajuste", "Carga", "Choque", "Descarga")
    """
    if not rm_cliente or rm_cliente <= 0:
        return "Sin RM"

    # Definición de porcentajes según tu amigo
    fases = {
        "Ajuste":   (0.30, 0.50), # 30-50%
        "Carga":    (0.50, 0.70), # 50-70%
        "Choque":   (0.70, 1.00), # 70-100%
        "Descarga": (0.20, 0.30)  # 20-30%
    }
    
    if tipo_semana not in fases:
        return "Fase desconocida"
        
    min_pct, max_pct = fases[tipo_semana]
    
    peso_min = rm_cliente * min_pct
    peso_max = rm_cliente * max_pct
    
    # Formateamos bonito: "30kg - 50kg"
    return f"{int(peso_min)}kg - {int(peso_max)}kg"