# TalentoTech - Proyecto Final: Módulo de Menú Principal
# Comisión 26205
# Autor: J. Luis Rey
# Descripción: Presenta el menú principal subdividido con encabezado continuo, ajuste general de precios y modificación de casos.
#
# Fecha: 2026-11-20
# Version 1.04

import sys
from colorama import Fore, Style
from logs_y_reportes import registrar_log, limpiar_pantalla, pausar
from inventario import (
    registrar_producto,
    listar_productos,
    buscar_productos,
    actualizar_producto,
    eliminar_producto,
    ajustar_precios_porcentaje,
    reporte_bajo_stock,
    gestionar_categorias
)
from clientes_y_casos import (
    registrar_cliente,
    listar_clientes,
    abrir_caso,
    listar_casos,
    filtrar_casos_por_estado,
    modificar_caso,
    ver_detalle_caso
)

# Muestra el menú interactivo subdividido y deriva cada opción a su función
def ejecutar_menu():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    registrar_log("SISTEMA", "Inicio del menú principal del taller (v1.04)")

    while True:
        limpiar_pantalla()
        ancho = 62
        titulo_principal = "TALLER Y SERVICIO TÉCNICO - GESTIÓN INTEGRAL (v1.04)"
        subtitulo = "por Jonathan Rey"

        print(f"{Fore.CYAN}{Style.BRIGHT}╔{'═' * ancho}╗{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}{Style.BRIGHT}║{Style.RESET_ALL}"
            f"{Fore.WHITE}{Style.BRIGHT}{titulo_principal.center(ancho)}{Style.RESET_ALL}"
            f"{Fore.CYAN}{Style.BRIGHT}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}{Style.BRIGHT}║{Style.RESET_ALL}"
            f"{Fore.YELLOW}{subtitulo.center(ancho)}{Style.RESET_ALL}"
            f"{Fore.CYAN}{Style.BRIGHT}║{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}{Style.BRIGHT}╚{'═' * ancho}╝{Style.RESET_ALL}")

        # Subsección 1: Inventario y Precios
        print(f"\n{Fore.GREEN}{Style.BRIGHT}[ INVENTARIO Y PRECIOS ]{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}1.{Style.RESET_ALL} Registrar producto / componente")
        print(f"  {Fore.WHITE}2.{Style.RESET_ALL} Listar todos los productos")
        print(f"  {Fore.WHITE}3.{Style.RESET_ALL} Buscar producto (ID / Nombre / Categoría)")
        print(f"  {Fore.WHITE}4.{Style.RESET_ALL} Actualizar producto por ID")
        print(f"  {Fore.WHITE}5.{Style.RESET_ALL} Eliminar producto por ID")
        print(f"  {Fore.WHITE}6.{Style.RESET_ALL} Ajustar precios en general (Subir / Bajar %)")
        print(f"  {Fore.WHITE}7.{Style.RESET_ALL} Reporte de stock igual o menor a un límite")
        print(f"  {Fore.WHITE}8.{Style.RESET_ALL} Gestionar categorías (Crear / Modificar / Eliminar)")

        # Subsección 2: Clientes y Casos
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}[ CLIENTES Y CASOS ]{Style.RESET_ALL}")
        print(f"  {Fore.WHITE} 9.{Style.RESET_ALL} Registrar cliente")
        print(f"  {Fore.WHITE}10.{Style.RESET_ALL} Listar clientes")
        print(f"  {Fore.WHITE}11.{Style.RESET_ALL} Abrir nuevo caso de servicio")
        print(f"  {Fore.WHITE}12.{Style.RESET_ALL} Listar todos los casos")
        print(f"  {Fore.WHITE}13.{Style.RESET_ALL} Filtrar casos por estado")
        print(f"  {Fore.WHITE}14.{Style.RESET_ALL} Modificar un caso")
        print(f"  {Fore.WHITE}15.{Style.RESET_ALL} Ver detalle de caso y exportar a TXT")

        print(f"\n{Fore.RED}{Style.BRIGHT}  0. Salir del sistema{Style.RESET_ALL}")

        opcion = input(f"\n{Fore.CYAN}{Style.BRIGHT}Seleccione una opción: {Style.RESET_ALL}").strip()

        if opcion == "1":
            registrar_producto()
        elif opcion == "2":
            listar_productos()
        elif opcion == "3":
            buscar_productos()
        elif opcion == "4":
            actualizar_producto()
        elif opcion == "5":
            eliminar_producto()
        elif opcion == "6":
            ajustar_precios_porcentaje()
        elif opcion == "7":
            reporte_bajo_stock()
        elif opcion == "8":
            gestionar_categorias()
        elif opcion == "9":
            registrar_cliente()
        elif opcion == "10":
            listar_clientes()
        elif opcion == "11":
            abrir_caso()
        elif opcion == "12":
            listar_casos()
        elif opcion == "13":
            filtrar_casos_por_estado()
        elif opcion == "14":
            modificar_caso()
        elif opcion == "15":
            ver_detalle_caso()
        elif opcion == "0":
            registrar_log("SISTEMA", "Cierre del sistema por el usuario")
            print(f"\n{Fore.GREEN}[INFO] Cerrando el sistema. ¡Hasta luego!{Style.RESET_ALL}")
            break
        else:
            print(f"\n{Fore.RED}[ERROR] Opción no válida. Intente nuevamente.{Style.RESET_ALL}")
            pausar()