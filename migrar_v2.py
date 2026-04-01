import sqlite3

def migrar_v2():
    conn = sqlite3.connect('entrenador.db')
    cursor = conn.cursor()

    nuevas_columnas = [
        "metodo_grasa TEXT",
        "suma_pliegues FLOAT"
    ]

    print("Iniciando migración v2...")
    for col in nuevas_columnas:
        try:
            cursor.execute(f"ALTER TABLE evaluaciones ADD COLUMN {col}")
            print(f"Columna {col} agregada con éxito.")
        except sqlite3.OperationalError as e:
            print(f"Aviso con {col}: {e}")

    conn.commit()
    conn.close()
    print("¡Migración terminada!")

if __name__ == "__main__":
    migrar_v2()