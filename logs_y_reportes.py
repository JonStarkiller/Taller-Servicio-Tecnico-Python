# TalentoTech - Proyecto Final: Módulo de Logs, Reportes y Consola
# Comisión 26205
# Autor: J. Luis Rey
# Descripción: Gestiona la carpeta Logs (tope 50 MB), exportación en carpeta Informes, colores de estado y listas navegables.
#
# Fecha: 2026-11-20
# Version 1.04

import os
import msvcrt
from colorama import Fore, Style

# Carpetas y archivos de registro e informes dentro del directorio del proyecto
CARPETA_LOGS = "Logs"
CARPETA_INFORMES = "Informes"
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "actividad.log")
ARCHIVO_INFORMES = os.path.join(CARPETA_INFORMES, "informes.txt")

# Límite máximo de capacidad para el archivo de log: 50 MB en bytes
LIMITE_LOG_BYTES = 50 * 1024 * 1024

# Cantidad de filas visibles por ventana cuando la lista es extensa
TAMANO_VENTANA_LISTA = 8

# Asegura que exista la subcarpeta Informes antes de guardar un archivo exportado
def inicializar_informes():
    os.makedirs(CARPETA_INFORMES, exist_ok=True)

# Limpia caracteres no válidos para nombres de archivo en Windows manteniendo espacios y tildes básicos
def limpiar_nombre_archivo(texto):
    caracteres_prohibidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    limpio = texto.strip()
    for char in caracteres_prohibidos:
        limpio = limpio.replace(char, "")
    return limpio if limpio else "Sin_Dato"

# Construye la ruta completa en \Informes: Informes\[Caso xxx] - [Nombre Cliente] - [AAAA-MM-DD].txt
def construir_nombre_archivo_caso(caso_id, nombre_cliente, fecha_modificacion):
    cliente_seguro = limpiar_nombre_archivo(nombre_cliente)
    fecha_segura = limpiar_nombre_archivo(fecha_modificacion)
    nombre_base = f"[Caso {caso_id}] - [{cliente_seguro}] - [{fecha_segura}].txt"
    return os.path.join(CARPETA_INFORMES, nombre_base)

# Devuelve el color asignado a cada estado de un caso de servicio técnico
def obtener_color_estado(estado):
    estado_limpio = estado.strip().lower()
    if estado_limpio == "abierto":
        return Fore.YELLOW
    elif estado_limpio in ("en reparación", "en reparacion"):
        return Fore.CYAN
    elif estado_limpio == "finalizado":
        return Fore.GREEN
    elif estado_limpio == "entregado":
        return Fore.BLUE
    return Fore.WHITE

# Formatea un texto de estado con su color correspondiente
def formatear_estado_con_color(estado):
    color = obtener_color_estado(estado)
    return f"{color}{Style.BRIGHT}{estado}{Style.RESET_ALL}"

# Limpia la consola en Windows
def limpiar_pantalla():
    os.system("cls")

# Pausa la ejecución hasta que el usuario presione Enter
def pausar(mensaje="\nPresione Enter para continuar..."):
    input(f"{Fore.CYAN}{mensaje}{Style.RESET_ALL}")

# Imprime un encabezado visual destacado con colores
def imprimir_encabezado(titulo, color=Fore.CYAN):
    ancho = 62
    print(f"\n{color}{'=' * ancho}{Style.RESET_ALL}")
    print(f"{color}{Style.BRIGHT}  {titulo.upper()}{Style.RESET_ALL}")
    print(f"{color}{'=' * ancho}{Style.RESET_ALL}")

# Asegura que exista la subcarpeta Logs y el archivo de log al iniciar el programa
def inicializar_logs():
    try:
        os.makedirs(CARPETA_LOGS, exist_ok=True)
        if not os.path.exists(ARCHIVO_LOG):
            with open(ARCHIVO_LOG, "w", encoding="utf-8") as archivo:
                archivo.write("=== Registro de actividad del sistema (Tope: 50 MB) ===\n")
    except OSError as error:
        print(f"{Fore.RED}[ERROR] No se pudo preparar la carpeta Logs: {error}{Style.RESET_ALL}")

# Verifica el tamaño del log y lo reinicia si supera los 50 MB
def controlar_capacidad_log():
    try:
        if os.path.exists(ARCHIVO_LOG):
            tamano_actual = os.path.getsize(ARCHIVO_LOG)
            if tamano_actual >= LIMITE_LOG_BYTES:
                with open(ARCHIVO_LOG, "w", encoding="utf-8") as archivo:
                    archivo.write("=== Log reiniciado automáticamente por alcanzar el tope de 50 MB ===\n")
    except OSError as error:
        print(f"{Fore.RED}[ERROR] No se pudo verificar el tamaño del log: {error}{Style.RESET_ALL}")

# Registra un evento en Logs/actividad.log respetando el tope de 50 MB
def registrar_log(categoria, mensaje):
    try:
        inicializar_logs()
        controlar_capacidad_log()
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as archivo:
            archivo.write(f"[{categoria}] {mensaje}\n")
    except OSError as error:
        print(f"{Fore.RED}[ERROR] No se pudo escribir en el log: {error}{Style.RESET_ALL}")

# Guarda un texto de reporte o caso dentro de la carpeta Informes
def guardar_informe_txt(titulo, contenido, nombre_archivo=None):
    archivo_destino = nombre_archivo if nombre_archivo else ARCHIVO_INFORMES
    try:
        inicializar_informes()
        with open(archivo_destino, "w", encoding="utf-8") as archivo:
            archivo.write("=" * 60 + "\n")
            archivo.write(f"{titulo}\n")
            archivo.write("=" * 60 + "\n")
            archivo.write(contenido)
            if not contenido.endswith("\n"):
                archivo.write("\n")
            archivo.write("\n")
        return True
    except OSError as error:
        print(f"{Fore.RED}[ERROR] No se pudo guardar el informe en {archivo_destino}: {error}{Style.RESET_ALL}")
        return False

# Muestra una lista: si es corta imprime todo; si es larga permite subir/bajar con flechas y salir con Enter
def mostrar_lista_interactiva(titulo, lineas, color_titulo=Fore.CYAN):
    if not lineas:
        print(f"{Fore.YELLOW}[INFO] No hay registros para mostrar.{Style.RESET_ALL}")
        return

    if len(lineas) <= TAMANO_VENTANA_LISTA:
        imprimir_encabezado(titulo, color_titulo)
        for linea in lineas:
            print(f"{Fore.WHITE}{linea}{Style.RESET_ALL}")
        return

    indice_inicio = 0
    max_inicio = len(lineas) - TAMANO_VENTANA_LISTA

    while True:
        limpiar_pantalla()
        imprimir_encabezado(f"{titulo} ({len(lineas)} registros)", color_titulo)
        print(
            f"{Fore.MAGENTA}Use [Flecha Arriba / Abajo] para desplazar  |  "
            f"[Enter] para salir{Style.RESET_ALL}\n"
        )

        fin = indice_inicio + TAMANO_VENTANA_LISTA
        for pos in range(indice_inicio, fin):
            print(f"{Fore.WHITE}{lineas[pos]}{Style.RESET_ALL}")

        print(
            f"\n{Fore.YELLOW}Mostrando filas {indice_inicio + 1} a {fin} de {len(lineas)}{Style.RESET_ALL}"
        )

        tecla = msvcrt.getch()

        if tecla in (b"\r", b"\n"):
            break

        if tecla in (b"\xe0", b"\x00"):
            direccion = msvcrt.getch()
            if direccion == b"H":
                if indice_inicio > 0:
                    indice_inicio -= 1
            elif direccion == b"P":
                if indice_inicio < max_inicio:
                    indice_inicio += 1
        elif tecla in (b"w", b"W"):
            if indice_inicio > 0:
                indice_inicio -= 1
        elif tecla in (b"s", b"S"):
            if indice_inicio < max_inicio:
                indice_inicio += 1