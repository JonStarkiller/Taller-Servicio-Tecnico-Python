# TalentoTech - Proyecto Final: Punto de Entrada Principal
# Comisión 26205
# Autor: J. Luis Rey
# Descripción: Inicializa entorno, carpeta Logs, base de datos SQLite y arranca el menú principal.
#
# Fecha: 2026-11-20
# Version 1.02

from colorama import init
from base_datos import inicializar_base_datos
from logs_y_reportes import inicializar_logs
from menu import ejecutar_menu

# Inicializamos Colorama para toda la aplicación
init(autoreset=True)

# Preparamos carpeta Logs, base de datos SQLite y lanzamos el menú
inicializar_logs()
inicializar_base_datos()
ejecutar_menu()