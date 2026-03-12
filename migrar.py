import sqlite3

def migrar_base_de_datos():
    # Conectarse al archivo de tu amigo
    conn = sqlite3.connect('entrenador.db')
    cursor = conn.cursor()

    nuevas_columnas = [
        "perimetro_brazos FLOAT",
        "perimetro_piernas FLOAT"
    ]

    print("Iniciando migración...")
    for col in nuevas_columnas:
        try:
            # ALTER TABLE agrega las columnas a la tabla que ya existe
            cursor.execute(f"ALTER TABLE evaluaciones ADD COLUMN {col}")
            print(f"Columna {col} agregada con éxito.")
        except sqlite3.OperationalError as e:
            # Si da error, es porque la columna ya existe (lo cual está bien)
            print(f"Aviso con {col}: {e}")

    conn.commit()
    conn.close()
    print("¡Migración terminada! La base de datos está lista para la v1.1")

if __name__ == "__main__":
    migrar_base_de_datos()