# TalentoTech - Proyecto Final: Módulo de Base de Datos
# Comisión 26205
# Autor: J. Luis Rey
# Descripción: Crea y gestiona la base de datos SQLite inventario.db, categorías predeterminadas y tablas del taller.
#
# Fecha: 2026-11-20
# Version 1.02

import sqlite3

# Nombre del archivo de base de datos SQLite en la carpeta del proyecto
NOMBRE_BD = "inventario.db"

# Categorías fijas predeterminadas del taller de servicio técnico
CATEGORIAS_PREDETERMINADAS = [
    "Periféricos",
    "Procesadores",
    "Mothers",
    "Fuentes",
    "Memorias RAM",
    "Almacenamiento",
    "Gabinetes",
    "Refrigeración",
    "Repuestos Varios"
]

# Obtiene una conexión a la base de datos SQLite con claves foráneas habilitadas
def conectar():
    conexion = sqlite3.connect(NOMBRE_BD)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion

# Crea la base de datos, las tablas y precarga las categorías predeterminadas
def inicializar_base_datos():
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        # Iniciamos transacción para crear estructura y datos base de forma atómica
        cursor.execute("BEGIN TRANSACTION")

        # Tabla de categorías de productos y componentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        """)

        # Tabla principal de productos / componentes del taller
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
                precio REAL NOT NULL CHECK (precio > 0),
                categoria TEXT NOT NULL DEFAULT 'Repuestos Varios'
            )
        """)

        # Tabla de clientes del servicio técnico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                telefono TEXT NOT NULL,
                direccion TEXT,
                email TEXT,
                situacion_fiscal TEXT
            )
        """)

        # Tabla de casos / órdenes de reparación asociadas a un cliente
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS casos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                descripcion_trabajo TEXT NOT NULL,
                estado TEXT NOT NULL,
                total_cobrado REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)

        # Tabla de ítems de cada caso (mano de obra o repuestos del inventario)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items_caso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caso_id INTEGER NOT NULL,
                tipo_item TEXT NOT NULL,
                producto_id INTEGER,
                detalle TEXT NOT NULL,
                cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
                subtotal REAL NOT NULL CHECK (subtotal >= 0),
                FOREIGN KEY (caso_id) REFERENCES casos(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)

        # Precargamos las categorías predeterminadas si aún no existen
        for cat in CATEGORIAS_PREDETERMINADAS:
            cursor.execute(
                "INSERT OR IGNORE INTO categorias (nombre) VALUES (?)",
                (cat,)
            )

        conexion.commit()
    except sqlite3.Error as error:
        conexion.rollback()
        print(f"[ERROR] No se pudo inicializar la base de datos: {error}")
    finally:
        conexion.close()