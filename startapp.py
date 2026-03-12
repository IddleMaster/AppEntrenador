from database.models import inicializar_db, Ejercicio, obtener_sesion

print("Creando base de datos...")
engine = inicializar_db()
print("¡Base de datos 'entrenador.db' creada con éxito!")

# --- Opcional: Cargar un ejercicio de prueba para ver que funcione ---
session = obtener_sesion()

# Verificamos si ya existe para no duplicar 
existe = session.query(Ejercicio).filter_by(nombre="Sentadilla con Barra").first()

if not existe:
    ejercicio_demo = Ejercicio(
        nombre="Sentadilla con Barra",
        url_video="https://www.youtube.com/watch?v=tu_video_aqui",
        grupo_muscular="Piernas",
        categoria_implemento="Gym",
        nivel_dificultad="Intermedio"
    )
    session.add(ejercicio_demo)
    session.commit()
    print("Ejercicio de prueba agregado.")
else:
    print("El ejercicio de prueba ya existía.")

session.close()