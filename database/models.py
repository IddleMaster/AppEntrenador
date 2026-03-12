from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# 1. Configuración de la Base de Datos (GLOBAL)
# Esto es lo que faltaba: definir engine fuera de las funciones
engine = create_engine('sqlite:///entrenador.db', echo=False)

# Configuración de sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Definición de Tablas
class Cliente(Base):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rut = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    genero = Column(String)
    correo = Column(String)
    telefono = Column(String)
    peso_actual = Column(Float) 
    estatura = Column(Float)
    
    evaluaciones = relationship("Evaluacion", back_populates="cliente", cascade="all, delete-orphan")
    rutinas = relationship("Rutina", back_populates="cliente")

class Ejercicio(Base):
    __tablename__ = 'ejercicios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    url_video = Column(String)
    grupo_muscular = Column(String)
    categoria_implemento = Column(String)
    nivel_dificultad = Column(String)
    descripcion = Column(String, nullable=True)

class Evaluacion(Base):
    __tablename__ = 'evaluaciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    fecha = Column(DateTime, default=datetime.now)
    
    peso = Column(Float)
    imc = Column(Float)
    porcentaje_grasa = Column(Float)
    perimetro_cintura = Column(Float)
    perimetro_cadera = Column(Float)
    #--Añadido
    perimetro_brazos = Column(Float)
    perimetro_piernas = Column(Float)
    
    rm_sentadilla = Column(Float)
    rm_hip_thrust = Column(Float)
    rm_peso_muerto = Column(Float)
    rm_press_banca = Column(Float)
    rm_curl_biceps = Column(Float)
    rm_dominadas = Column(Float)
    
    cliente = relationship("Cliente", back_populates="evaluaciones")

class Rutina(Base):
    __tablename__ = 'rutinas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    fecha_creacion = Column(DateTime, default=datetime.now)
    nombre_archivo = Column(String)
    
    cliente = relationship("Cliente", back_populates="rutinas")

# 3. Función simplificada para obtener sesión
def obtener_sesion():
    return SessionLocal()