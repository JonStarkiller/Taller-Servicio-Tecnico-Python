# TalentoTech - Proyecto Final: Módulo de Clientes y Casos de Servicio Técnico
# Comisión 26205
# Autor: J. Luis Rey
# Descripción: Gestiona clientes, casos, gestión unificada de ítems y exportación en subcarpeta Informes.
#
# Fecha: 2026-11-20
# Version 1.04

import os
import datetime
import sqlite3
from colorama import Fore, Style
from base_datos import conectar
from logs_y_reportes import (
    registrar_log,
    guardar_informe_txt,
    construir_nombre_archivo_caso,
    limpiar_pantalla,
    pausar,
    imprimir_encabezado,
    mostrar_lista_interactiva,
    formatear_estado_con_color
)
from validaciones import (
    capitalizar_primera_letra,
    validar_texto_obligatorio,
    validar_telefono,
    validar_email_opcional,
    validar_situacion_fiscal_opcional,
    validar_entero_minimo,
    validar_decimal_mayor_cero,
    SITUACIONES_FISCALES
)

# Estados permitidos para un caso de reparación o servicio técnico
ESTADOS_CASO = ["Abierto", "En reparación", "Finalizado", "Entregado"]

# Inserta un cliente en la base de datos y devuelve su nuevo ID (o None si falla)
def insertar_cliente_en_bd(nombre_completo, telefono, direccion, email, situacion_fiscal):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
            INSERT INTO clientes (nombre_completo, telefono, direccion, email, situacion_fiscal)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre_completo, telefono, direccion, email, situacion_fiscal))
        nuevo_id = cursor.lastrowid
        conexion.commit()
        registrar_log("CLIENTE_ALTA", f"ID {nuevo_id} - {nombre_completo} (Tel: {telefono})")
        return nuevo_id
    except sqlite3.Error as error:
        conexion.rollback()
        print(f"{Fore.RED}[ERROR] No se pudo guardar el cliente: {error}{Style.RESET_ALL}")
        registrar_log("ERROR_BD", f"Fallo al registrar cliente '{nombre_completo}': {error}")
        return None
    finally:
        conexion.close()

# Registra clientes con opción de reintentar o cancelar ante error y agregar otro o volver al menú
def registrar_cliente(usar_pausa=True):
    ultimo_id = None

    while True:
        limpiar_pantalla()
        imprimir_encabezado("Registrar Nuevo Cliente", Fore.CYAN)

        nombre = capitalizar_primera_letra(input("Nombre completo (obligatorio): "))
        if not validar_texto_obligatorio(nombre):
            print(f"{Fore.RED}[ERROR] El nombre completo es obligatorio.{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a intentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            return ultimo_id

        telefono = input("Teléfono (obligatorio): ").strip()
        if not validar_telefono(telefono):
            print(f"{Fore.RED}[ERROR] Ingrese un teléfono válido (al menos 6 dígitos).{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a intentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            return ultimo_id

        direccion = capitalizar_primera_letra(input("Dirección (opcional): "))
        email_input = input("Email (opcional): ").strip()
        ok_email, email = validar_email_opcional(email_input)
        if not ok_email:
            print(f"{Fore.RED}[ERROR] El formato del email no es válido.{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a intentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            return ultimo_id

        print(f"\n{Fore.BLUE}Situación fiscal (opcional, Enter para 'No especificada'):{Style.RESET_ALL}")
        for idx, situacion in enumerate(SITUACIONES_FISCALES, start=1):
            print(f"  {idx}. {situacion}")
        fiscal_input = input("Seleccione número o escriba la situación: ").strip()
        ok_fiscal, situacion_fiscal = validar_situacion_fiscal_opcional(fiscal_input)
        if not ok_fiscal:
            print(f"{Fore.RED}[ERROR] Situación fiscal no válida.{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a intentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            return ultimo_id

        cliente_id = insertar_cliente_en_bd(nombre, telefono, direccion, email, situacion_fiscal)
        if cliente_id is not None:
            ultimo_id = cliente_id
            print(f"\n{Fore.GREEN}[ÉXITO] Cliente '{nombre}' registrado con ID {cliente_id}.{Style.RESET_ALL}")
        else:
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a intentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            return ultimo_id

        if not usar_pausa:
            return ultimo_id

        otro = input(
            f"\n{Fore.CYAN}¿Desea agregar otro cliente? (s para otro / N o Enter para volver al menú): {Style.RESET_ALL}"
        ).strip().lower()
        if otro != "s":
            return ultimo_id

# Formatea filas de clientes para consola
def formatear_lineas_clientes(clientes):
    lineas = []
    for cli in clientes:
        dir_txt = cli[3] if cli[3] else "No informada"
        mail_txt = cli[4] if cli[4] else "No informado"
        fis_txt = cli[5] if cli[5] else "No especificada"
        lineas.append(
            f"ID: {cli[0]} | {cli[1]} | Tel: {cli[2]} | "
            f"Fiscal: {fis_txt} | Dir: {dir_txt} | Email: {mail_txt}"
        )
    return lineas

# Lista todos los clientes registrados en la base de datos
def listar_clientes(usar_pausa=True):
    limpiar_pantalla()
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT id, nombre_completo, telefono, direccion, email, situacion_fiscal
            FROM clientes
            ORDER BY id ASC
        """)
        clientes = cursor.fetchall()

        if not clientes:
            imprimir_encabezado("Clientes Registrados", Fore.CYAN)
            print(f"{Fore.YELLOW}[INFO] No hay clientes registrados todavía.{Style.RESET_ALL}")
            if usar_pausa:
                pausar()
            return False

        lineas = formatear_lineas_clientes(clientes)
        mostrar_lista_interactiva("Clientes Registrados", lineas, Fore.CYAN)
        if usar_pausa:
            pausar()
        return True
    except sqlite3.Error as error:
        print(f"{Fore.RED}[ERROR] Error al consultar clientes: {error}{Style.RESET_ALL}")
        if usar_pausa:
            pausar()
        return False
    finally:
        conexion.close()

# Selecciona un cliente existente por ID o permite cargarlo si no existe
def obtener_o_crear_cliente_para_caso():
    hay_clientes = listar_clientes(usar_pausa=False)

    if hay_clientes:
        respuesta = input(
            f"\n{Fore.CYAN}Ingrese el ID del cliente existente o 'N' para cargar uno nuevo: {Style.RESET_ALL}"
        ).strip()
        if respuesta.lower() == "n":
            return registrar_cliente(usar_pausa=False)

        ok_id, cliente_id = validar_entero_minimo(respuesta, minimo=1)
        if not ok_id:
            print(f"{Fore.RED}[ERROR] ID de cliente inválido.{Style.RESET_ALL}")
            return None

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id, nombre_completo FROM clientes WHERE id = ?", (cliente_id,))
            encontrado = cursor.fetchone()
            if not encontrado:
                print(f"{Fore.YELLOW}[INFO] No existe un cliente con ID {cliente_id}.{Style.RESET_ALL}")
                crear = input("¿Desea registrarlo ahora? (s/N, Enter = No): ").strip().lower()
                if crear == "s":
                    return registrar_cliente(usar_pausa=False)
                return None
            print(f"{Fore.GREEN}[INFO] Cliente seleccionado: {encontrado[1]} (ID {encontrado[0]}){Style.RESET_ALL}")
            return encontrado[0]
        except sqlite3.Error as error:
            print(f"{Fore.RED}[ERROR] Error al verificar cliente: {error}{Style.RESET_ALL}")
            return None
        finally:
            conexion.close()
    else:
        crear = input("No hay clientes cargados. ¿Desea registrar uno ahora? (s/N, Enter = No): ").strip().lower()
        if crear == "s":
            return registrar_cliente(usar_pausa=False)
        return None

# Recalcula la suma de subtotales de un caso y actualiza total_cobrado
def recalcular_total_caso(cursor, caso_id):
    cursor.execute("SELECT COALESCE(SUM(subtotal), 0) FROM items_caso WHERE caso_id = ?", (caso_id,))
    total = float(cursor.fetchone()[0])
    cursor.execute("UPDATE casos SET total_cobrado = ? WHERE id = ?", (total, caso_id))
    return total

# Formatea filas de casos aplicando color a cada estado
def formatear_lineas_casos(casos):
    lineas = []
    for caso in casos:
        estado_coloreado = formatear_estado_con_color(caso[3])
        lineas.append(
            f"Caso #{caso[0]} | Cliente: {caso[1]} (Tel: {caso[2]}) | "
            f"Estado: {estado_coloreado} | Total: ${caso[5]:.2f} | Trabajo: {caso[4]}"
        )
    return lineas

# Añade ítems de Mano de Obra o Repuestos a un caso existente
def agregar_items_a_caso(caso_id):
    while True:
        limpiar_pantalla()
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT estado, total_cobrado FROM casos WHERE id = ?", (caso_id,))
            datos_caso = cursor.fetchone()
            if not datos_caso:
                print(f"{Fore.RED}[ERROR] No existe el caso #{caso_id}.{Style.RESET_ALL}")
                pausar()
                return

            estado_visual = formatear_estado_con_color(datos_caso[0])
            total_actual = float(datos_caso[1])

            imprimir_encabezado(f"Añadir Ítems al Caso #{caso_id}", Fore.CYAN)
            print(f"Estado: {estado_visual} | Total actual: {Fore.GREEN}${total_actual:.2f}{Style.RESET_ALL}")
            print("1. Mano de obra")
            print("2. Repuesto / Componente del inventario")
            print("0. Volver")
            tipo_op = input(f"\n{Fore.CYAN}Seleccione una opción: {Style.RESET_ALL}").strip()

            if tipo_op == "0":
                break

            elif tipo_op == "1":
                detalle = capitalizar_primera_letra(input("Detalle de la mano de obra: "))
                if not validar_texto_obligatorio(detalle):
                    print(f"{Fore.RED}[ERROR] El detalle de la mano de obra no puede estar vacío.{Style.RESET_ALL}")
                    pausar()
                    continue

                cant_texto = input("Cantidad de horas / unidades de servicio [1, Enter = 1]: ").strip()
                if cant_texto == "":
                    cantidad = 1
                else:
                    ok_c, cantidad = validar_entero_minimo(cant_texto, minimo=1)
                    if not ok_c:
                        print(f"{Fore.RED}[ERROR] La cantidad debe ser un entero mayor que 0.{Style.RESET_ALL}")
                        pausar()
                        continue

                monto_texto = input("Valor unitario de mano de obra ($): ").strip()
                ok_m, valor_unit = validar_decimal_mayor_cero(monto_texto)
                if not ok_m:
                    print(f"{Fore.RED}[ERROR] El valor debe ser mayor que 0.{Style.RESET_ALL}")
                    pausar()
                    continue

                subtotal = round(cantidad * valor_unit, 2)

                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("""
                    INSERT INTO items_caso (caso_id, tipo_item, producto_id, detalle, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, NULL, ?, ?, ?, ?)
                """, (caso_id, "Mano de obra", detalle, cantidad, valor_unit, subtotal))
                nuevo_total = recalcular_total_caso(cursor, caso_id)
                conexion.commit()

                print(
                    f"\n{Fore.GREEN}[ÉXITO] Mano de obra agregada "
                    f"(Subtotal: ${subtotal:.2f} | Total caso: ${nuevo_total:.2f}).{Style.RESET_ALL}"
                )
                registrar_log("CASO_ITEM", f"Caso #{caso_id}: +Mano de obra '{detalle}' (${subtotal:.2f})")
                pausar()

            elif tipo_op == "2":
                cursor.execute("SELECT id, nombre, cantidad, precio, categoria FROM productos WHERE cantidad > 0 ORDER BY id ASC")
                disponibles = cursor.fetchall()
                if not disponibles:
                    print(f"\n{Fore.YELLOW}[INFO] No hay repuestos con stock disponible en el inventario.{Style.RESET_ALL}")
                    pausar()
                    continue

                lineas_disp = [
                    f"ID: {p[0]} | {p[1]} | Cat: {p[4] or 'General'} | Stock: {p[2]} | Precio: ${p[3]:.2f}"
                    for p in disponibles
                ]
                mostrar_lista_interactiva("Repuestos Disponibles con Stock", lineas_disp, Fore.BLUE)

                id_prod_txt = input(f"\n{Fore.CYAN}Ingrese el ID del repuesto: {Style.RESET_ALL}").strip()
                ok_p, prod_id = validar_entero_minimo(id_prod_txt, minimo=1)
                if not ok_p:
                    print(f"{Fore.RED}[ERROR] ID de repuesto inválido.{Style.RESET_ALL}")
                    pausar()
                    continue

                cant_rep_txt = input("Cantidad de repuestos a utilizar: ").strip()
                ok_cr, cant_rep = validar_entero_minimo(cant_rep_txt, minimo=1)
                if not ok_cr:
                    print(f"{Fore.RED}[ERROR] La cantidad debe ser un entero mayor que 0.{Style.RESET_ALL}")
                    pausar()
                    continue

                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("SELECT nombre, cantidad, precio FROM productos WHERE id = ?", (prod_id,))
                prod_datos = cursor.fetchone()
                if not prod_datos:
                    conexion.rollback()
                    print(f"{Fore.RED}[ERROR] Repuesto no encontrado.{Style.RESET_ALL}")
                    pausar()
                    continue

                nombre_rep, stock_actual, precio_rep = prod_datos[0], prod_datos[1], float(prod_datos[2])
                if cant_rep > stock_actual:
                    conexion.rollback()
                    print(f"{Fore.RED}[ERROR] Stock insuficiente para '{nombre_rep}' (Disponible: {stock_actual}).{Style.RESET_ALL}")
                    pausar()
                    continue

                subtotal = round(cant_rep * precio_rep, 2)
                cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (cant_rep, prod_id))
                cursor.execute("""
                    INSERT INTO items_caso (caso_id, tipo_item, producto_id, detalle, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (caso_id, "Repuesto", prod_id, nombre_rep, cant_rep, precio_rep, subtotal))
                nuevo_total = recalcular_total_caso(cursor, caso_id)
                conexion.commit()

                print(
                    f"\n{Fore.GREEN}[ÉXITO] Repuesto '{nombre_rep}' x{cant_rep} agregado "
                    f"(Subtotal: ${subtotal:.2f} | Total caso: ${nuevo_total:.2f}).{Style.RESET_ALL}"
                )
                registrar_log("CASO_ITEM", f"Caso #{caso_id}: +Repuesto '{nombre_rep}' x{cant_rep} (${subtotal:.2f})")
                pausar()

            else:
                print(f"{Fore.RED}[ERROR] Opción no válida.{Style.RESET_ALL}")
                pausar()

        except sqlite3.Error as error:
            conexion.rollback()
            print(f"{Fore.RED}[ERROR] Error al agregar ítem al caso: {error}{Style.RESET_ALL}")
            registrar_log("ERROR_BD", f"Fallo al agregar ítem a caso #{caso_id}: {error}")
            pausar()
        finally:
            conexion.close()

# Edita o elimina ítems existentes de un caso; si se presiona Enter sin escribir, pasa sin modificar
def editar_o_quitar_items_caso(caso_id):
    while True:
        limpiar_pantalla()
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT id, tipo_item, producto_id, detalle, cantidad, precio_unitario, subtotal
                FROM items_caso
                WHERE caso_id = ?
                ORDER BY id ASC
            """, (caso_id,))
            items = cursor.fetchall()

            imprimir_encabezado(f"Ítems del Caso #{caso_id}", Fore.CYAN)
            if not items:
                print(f"{Fore.YELLOW}[INFO] Este caso no tiene ítems cargados.{Style.RESET_ALL}")
                pausar()
                break

            for it in items:
                print(
                    f"{Fore.WHITE}Ítem ID: {it[0]} | [{it[1]}] {it[3]} | "
                    f"Cant: {it[4]} | Unitario: ${it[5]:.2f} | Subtotal: ${it[6]:.2f}{Style.RESET_ALL}"
                )

            print(f"\n{Fore.CYAN}1. Modificar un ítem existente{Style.RESET_ALL}")
            print(f"{Fore.RED}2. Eliminar un ítem del caso{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}0. Volver{Style.RESET_ALL}")

            sub_op = input(f"\n{Fore.CYAN}Seleccione una opción: {Style.RESET_ALL}").strip()
            if sub_op == "0":
                break

            elif sub_op == "1":
                id_it_txt = input("Ingrese el ID del ítem a modificar: ").strip()
                ok_id, id_it = validar_entero_minimo(id_it_txt, minimo=1)
                if not ok_id:
                    print(f"{Fore.RED}[ERROR] ID de ítem inválido.{Style.RESET_ALL}")
                    pausar()
                    continue

                cursor.execute("""
                    SELECT id, tipo_item, producto_id, detalle, cantidad, precio_unitario
                    FROM items_caso
                    WHERE id = ? AND caso_id = ?
                """, (id_it, caso_id))
                actual = cursor.fetchone()
                if not actual:
                    print(f"{Fore.YELLOW}[INFO] No se encontró el ítem #{id_it} en este caso.{Style.RESET_ALL}")
                    pausar()
                    continue

                tipo_it = actual[1]
                prod_id = actual[2]
                detalle_act = actual[3]
                cant_act = int(actual[4])
                precio_act = float(actual[5])

                if tipo_it == "Mano de obra":
                    nuevo_det = capitalizar_primera_letra(input(f"Detalle [{detalle_act}]: "))
                    if nuevo_det == "":
                        detalle_fin = detalle_act
                        print(f"{Fore.YELLOW}[INFO] Detalle sin modificar.{Style.RESET_ALL}")
                    else:
                        detalle_fin = nuevo_det
                else:
                    detalle_fin = detalle_act
                    print(f"{Fore.BLUE}[INFO] Repuesto: {detalle_act} (el nombre del repuesto no se altera).{Style.RESET_ALL}")

                cant_txt = input(f"Cantidad [{cant_act}]: ").strip()
                if cant_txt == "":
                    cant_fin = cant_act
                    print(f"{Fore.YELLOW}[INFO] Cantidad sin modificar.{Style.RESET_ALL}")
                else:
                    ok_c, cant_fin = validar_entero_minimo(cant_txt, minimo=1)
                    if not ok_c:
                        print(f"{Fore.RED}[ERROR] Cantidad inválida. No se modificó la cantidad.{Style.RESET_ALL}")
                        pausar()
                        continue

                if tipo_it == "Mano de obra":
                    precio_txt = input(f"Valor unitario [${precio_act:.2f}]: ").strip()
                    if precio_txt == "":
                        precio_fin = precio_act
                        print(f"{Fore.YELLOW}[INFO] Valor unitario sin modificar.{Style.RESET_ALL}")
                    else:
                        ok_p, precio_fin = validar_decimal_mayor_cero(precio_txt)
                        if not ok_p:
                            print(f"{Fore.RED}[ERROR] Valor inválido. No se modificó el valor.{Style.RESET_ALL}")
                            pausar()
                            continue
                else:
                    precio_fin = precio_act

                nuevo_subtotal = round(cant_fin * precio_fin, 2)
                dif_cant = cant_fin - cant_act

                cursor.execute("BEGIN TRANSACTION")
                if tipo_it == "Repuesto" and prod_id is not None and dif_cant != 0:
                    cursor.execute("SELECT cantidad FROM productos WHERE id = ?", (prod_id,))
                    fila_prod = cursor.fetchone()
                    if not fila_prod:
                        conexion.rollback()
                        print(f"{Fore.RED}[ERROR] Repuesto asociado no encontrado.{Style.RESET_ALL}")
                        pausar()
                        continue
                    stock_disp = int(fila_prod[0])
                    if dif_cant > 0 and dif_cant > stock_disp:
                        conexion.rollback()
                        print(f"{Fore.RED}[ERROR] Stock insuficiente para aumentar cantidad (Disponible: {stock_disp}).{Style.RESET_ALL}")
                        pausar()
                        continue
                    cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (dif_cant, prod_id))

                cursor.execute("""
                    UPDATE items_caso
                    SET detalle = ?, cantidad = ?, precio_unitario = ?, subtotal = ?
                    WHERE id = ? AND caso_id = ?
                """, (detalle_fin, cant_fin, precio_fin, nuevo_subtotal, id_it, caso_id))
                nuevo_total = recalcular_total_caso(cursor, caso_id)
                conexion.commit()

                print(f"\n{Fore.GREEN}[ÉXITO] Ítem #{id_it} actualizado. Nuevo total del caso: ${nuevo_total:.2f}.{Style.RESET_ALL}")
                registrar_log("CASO_ITEM_MOD", f"Caso #{caso_id}: editado ítem #{id_it} (Total: ${nuevo_total:.2f})")
                pausar()

            elif sub_op == "2":
                id_it_txt = input("Ingrese el ID del ítem a eliminar: ").strip()
                ok_id, id_it = validar_entero_minimo(id_it_txt, minimo=1)
                if not ok_id:
                    print(f"{Fore.RED}[ERROR] ID de ítem inválido.{Style.RESET_ALL}")
                    pausar()
                    continue

                cursor.execute("""
                    SELECT id, tipo_item, producto_id, detalle, cantidad
                    FROM items_caso
                    WHERE id = ? AND caso_id = ?
                """, (id_it, caso_id))
                actual = cursor.fetchone()
                if not actual:
                    print(f"{Fore.YELLOW}[INFO] No se encontró el ítem #{id_it} en este caso.{Style.RESET_ALL}")
                    pausar()
                    continue

                conf = input(
                    f"{Fore.YELLOW}¿Confirma eliminar '{actual[3]}' del caso? (s/N, Enter = No): {Style.RESET_ALL}"
                ).strip().lower()
                if conf != "s":
                    print(f"{Fore.BLUE}[INFO] Eliminación de ítem cancelada.{Style.RESET_ALL}")
                    pausar()
                    continue

                cursor.execute("BEGIN TRANSACTION")
                if actual[1] == "Repuesto" and actual[2] is not None:
                    cursor.execute("UPDATE productos SET cantidad = cantidad + ? WHERE id = ?", (actual[4], actual[2]))
                cursor.execute("DELETE FROM items_caso WHERE id = ? AND caso_id = ?", (id_it, caso_id))
                nuevo_total = recalcular_total_caso(cursor, caso_id)
                conexion.commit()

                print(f"\n{Fore.GREEN}[ÉXITO] Ítem eliminado. Nuevo total del caso: ${nuevo_total:.2f}.{Style.RESET_ALL}")
                registrar_log("CASO_ITEM_BAJA", f"Caso #{caso_id}: eliminado ítem '{actual[3]}' (Total: ${nuevo_total:.2f})")
                pausar()

            else:
                print(f"{Fore.RED}[ERROR] Opción no válida.{Style.RESET_ALL}")
                pausar()

        except sqlite3.Error as error:
            conexion.rollback()
            print(f"{Fore.RED}[ERROR] Error al gestionar ítems del caso: {error}{Style.RESET_ALL}")
            pausar()
        finally:
            conexion.close()

# Menú unificado para añadir, modificar o eliminar ítems de un caso
def gestionar_items_caso(caso_id):
    while True:
        limpiar_pantalla()
        imprimir_encabezado(f"Gestionar Ítems del Caso #{caso_id}", Fore.CYAN)
        print("1. Añadir ítems (Mano de obra / Repuestos)")
        print("2. Modificar o eliminar ítems existentes")
        print("0. Volver a modificar caso")

        op_item = input(f"\n{Fore.CYAN}Seleccione una opción: {Style.RESET_ALL}").strip()
        if op_item == "0":
            break
        elif op_item == "1":
            agregar_items_a_caso(caso_id)
        elif op_item == "2":
            editar_o_quitar_items_caso(caso_id)
        else:
            print(f"{Fore.RED}[ERROR] Opción no válida.{Style.RESET_ALL}")
            pausar()

# Abre un nuevo caso asociado a un cliente y permite cargar su descripción e ítems
def abrir_caso():
    cliente_id = obtener_o_crear_cliente_para_caso()
    if cliente_id is None:
        print(f"\n{Fore.YELLOW}[INFO] Apertura de caso cancelada.{Style.RESET_ALL}")
        pausar()
        return

    imprimir_encabezado("Datos del Nuevo Caso", Fore.CYAN)
    descripcion = capitalizar_primera_letra(input("Descripción del trabajo realizado / falla reportada: "))
    if not validar_texto_obligatorio(descripcion):
        print(f"{Fore.RED}[ERROR] La descripción del trabajo no puede estar vacía.{Style.RESET_ALL}")
        pausar()
        return

    estado_inicial = ESTADOS_CASO[0]

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
            INSERT INTO casos (cliente_id, descripcion_trabajo, estado, total_cobrado)
            VALUES (?, ?, ?, 0)
        """, (cliente_id, descripcion, estado_inicial))
        nuevo_caso_id = cursor.lastrowid
        conexion.commit()

        estado_visual = formatear_estado_con_color(estado_inicial)
        print(f"\n{Fore.GREEN}[ÉXITO] Caso #{nuevo_caso_id} abierto en estado {estado_visual}.{Style.RESET_ALL}")
        registrar_log("CASO_NUEVO", f"Caso #{nuevo_caso_id} creado para cliente ID {cliente_id}")
    except sqlite3.Error as error:
        conexion.rollback()
        print(f"{Fore.RED}[ERROR] No se pudo abrir el caso: {error}{Style.RESET_ALL}")
        registrar_log("ERROR_BD", f"Fallo al abrir caso para cliente ID {cliente_id}: {error}")
        pausar()
        return
    finally:
        conexion.close()

    cargar_ahora = input(
        f"\n{Fore.BLUE}¿Desea cargar ítems (mano de obra / repuestos) ahora? (s/N, Enter = No): {Style.RESET_ALL}"
    ).strip().lower()
    if cargar_ahora == "s":
        agregar_items_a_caso(nuevo_caso_id)
    else:
        pausar()

# Lista todos los casos registrados junto con los datos del cliente y color de estado
def listar_casos(usar_pausa=True):
    limpiar_pantalla()
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT c.id, cl.nombre_completo, cl.telefono, c.estado, c.descripcion_trabajo, c.total_cobrado
            FROM casos c
            INNER JOIN clientes cl ON c.cliente_id = cl.id
            ORDER BY c.id DESC
        """)
        casos = cursor.fetchall()

        if not casos:
            imprimir_encabezado("Casos de Servicio Técnico", Fore.CYAN)
            print(f"{Fore.YELLOW}[INFO] No hay casos registrados todavía.{Style.RESET_ALL}")
            if usar_pausa:
                pausar()
            return False

        lineas = formatear_lineas_casos(casos)
        mostrar_lista_interactiva("Casos de Servicio Técnico", lineas, Fore.CYAN)
        if usar_pausa:
            pausar()
        return True
    except sqlite3.Error as error:
        print(f"{Fore.RED}[ERROR] Error al consultar casos: {error}{Style.RESET_ALL}")
        if usar_pausa:
            pausar()
        return False
    finally:
        conexion.close()

# Menú para filtrar casos según su estado (Abierto, En reparación, Finalizado, Entregado)
def filtrar_casos_por_estado():
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Filtrar Casos por Estado", Fore.MAGENTA)
        for idx, est in enumerate(ESTADOS_CASO, start=1):
            print(f"  {idx}. {formatear_estado_con_color(est)}")
        print(f"  {Fore.YELLOW}0. Volver al menú principal{Style.RESET_ALL}")

        op_txt = input(f"\n{Fore.CYAN}Seleccione un estado para filtrar: {Style.RESET_ALL}").strip()
        if op_txt == "0":
            break

        ok_op, op_num = validar_entero_minimo(op_txt, minimo=1)
        if not ok_op or op_num > len(ESTADOS_CASO):
            print(f"{Fore.RED}[ERROR] Opción de estado no válida.{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea reintentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            break

        estado_elegido = ESTADOS_CASO[op_num - 1]
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT c.id, cl.nombre_completo, cl.telefono, c.estado, c.descripcion_trabajo, c.total_cobrado
                FROM casos c
                INNER JOIN clientes cl ON c.cliente_id = cl.id
                WHERE c.estado = ?
                ORDER BY c.id DESC
            """, (estado_elegido,))
            casos = cursor.fetchall()

            if not casos:
                print(
                    f"\n{Fore.YELLOW}[INFO] No hay casos en estado {formatear_estado_con_color(estado_elegido)}.{Style.RESET_ALL}"
                )
            else:
                lineas = formatear_lineas_casos(casos)
                mostrar_lista_interactiva(f"Casos en estado: {estado_elegido}", lineas, Fore.MAGENTA)
        except sqlite3.Error as error:
            print(f"{Fore.RED}[ERROR] Error al filtrar casos: {error}{Style.RESET_ALL}")
        finally:
            conexion.close()

        pausar()
        otro = input(
            f"\n{Fore.CYAN}¿Desea filtrar por otro estado? (s para otro / N o Enter para volver al menú): {Style.RESET_ALL}"
        ).strip().lower()
        if otro != "s":
            break

# Modifica un caso de forma integral con menú limpio y gestión unificada de ítems
def modificar_caso():
    while True:
        listar_casos(usar_pausa=False)
        id_texto = input(f"\n{Fore.BLUE}Ingrese el ID del caso a modificar (o '0' para cancelar y volver): {Style.RESET_ALL}").strip()
        if id_texto == "0":
            break

        ok_id, caso_id = validar_entero_minimo(id_texto, minimo=1)
        if not ok_id:
            print(f"{Fore.RED}[ERROR] ID de caso inválido.{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a intentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            break

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT c.id, c.descripcion_trabajo, c.estado, c.total_cobrado, cl.nombre_completo
                FROM casos c
                INNER JOIN clientes cl ON c.cliente_id = cl.id
                WHERE c.id = ?
            """, (caso_id,))
            caso = cursor.fetchone()
            if not caso:
                print(f"{Fore.YELLOW}[INFO] No existe un caso con el ID {caso_id}.{Style.RESET_ALL}")
                reintentar = input(
                    f"\n{Fore.YELLOW}¿Desea intentar con otro ID o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
                ).strip().lower()
                if reintentar == "r":
                    continue
                break
        except sqlite3.Error as error:
            print(f"{Fore.RED}[ERROR] Error al consultar el caso: {error}{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a intentar o cancelar? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            break
        finally:
            conexion.close()

        while True:
            limpiar_pantalla()
            conexion = conectar()
            cursor = conexion.cursor()
            try:
                cursor.execute("""
                    SELECT c.id, c.descripcion_trabajo, c.estado, c.total_cobrado, cl.nombre_completo
                    FROM casos c
                    INNER JOIN clientes cl ON c.cliente_id = cl.id
                    WHERE c.id = ?
                """, (caso_id,))
                actual = cursor.fetchone()
            finally:
                conexion.close()

            imprimir_encabezado(f"Modificar Caso #{caso_id} - {actual[4]}", Fore.CYAN)
            print(f"Estado actual: {formatear_estado_con_color(actual[2])} | Total cobrado: {Fore.GREEN}${actual[3]:.2f}{Style.RESET_ALL}")
            print(f"Descripción actual: {Fore.WHITE}{actual[1]}{Style.RESET_ALL}\n")

            print("1. Modificar descripción del trabajo")
            print("2. Cambiar estado del caso")
            print("3. Gestionar ítems (Añadir / Modificar / Eliminar)")
            print("0. Volver al menú principal")

            op = input(f"\n{Fore.CYAN}Seleccione qué desea modificar: {Style.RESET_ALL}").strip()

            if op == "0":
                return

            elif op == "1":
                nueva_desc = capitalizar_primera_letra(input(f"\nNueva descripción [{actual[1]}]: "))
                if nueva_desc == "":
                    print(f"{Fore.YELLOW}[INFO] Descripción sin modificar.{Style.RESET_ALL}")
                    pausar()
                    continue

                conexion = conectar()
                cursor = conexion.cursor()
                try:
                    cursor.execute("BEGIN TRANSACTION")
                    cursor.execute("UPDATE casos SET descripcion_trabajo = ? WHERE id = ?", (nueva_desc, caso_id))
                    conexion.commit()
                    print(f"\n{Fore.GREEN}[ÉXITO] Descripción del caso #{caso_id} actualizada.{Style.RESET_ALL}")
                    registrar_log("CASO_MOD", f"Caso #{caso_id}: descripción actualizada")
                except sqlite3.Error as error:
                    conexion.rollback()
                    print(f"{Fore.RED}[ERROR] No se pudo actualizar la descripción: {error}{Style.RESET_ALL}")
                finally:
                    conexion.close()
                pausar()

            elif op == "2":
                print(f"\n{Fore.BLUE}Estados disponibles:{Style.RESET_ALL}")
                for idx, est in enumerate(ESTADOS_CASO, start=1):
                    print(f"  {idx}. {formatear_estado_con_color(est)}")

                op_est = input("Seleccione nuevo estado: ").strip()
                if op_est == "":
                    print(f"{Fore.YELLOW}[INFO] Estado sin modificar.{Style.RESET_ALL}")
                    pausar()
                    continue

                ok_e, num_e = validar_entero_minimo(op_est, minimo=1)
                if not ok_e or num_e > len(ESTADOS_CASO):
                    print(f"{Fore.RED}[ERROR] Opción de estado inválida. No se modificó el estado.{Style.RESET_ALL}")
                    pausar()
                    continue

                nuevo_estado = ESTADOS_CASO[num_e - 1]
                conexion = conectar()
                cursor = conexion.cursor()
                try:
                    cursor.execute("BEGIN TRANSACTION")
                    cursor.execute("UPDATE casos SET estado = ? WHERE id = ?", (nuevo_estado, caso_id))
                    conexion.commit()
                    print(
                        f"\n{Fore.GREEN}[ÉXITO] Caso #{caso_id} actualizado a {formatear_estado_con_color(nuevo_estado)}.{Style.RESET_ALL}"
                    )
                    registrar_log("CASO_ESTADO", f"Caso #{caso_id} -> Estado '{nuevo_estado}'")
                except sqlite3.Error as error:
                    conexion.rollback()
                    print(f"{Fore.RED}[ERROR] No se pudo cambiar el estado: {error}{Style.RESET_ALL}")
                finally:
                    conexion.close()
                pausar()

            elif op == "3":
                gestionar_items_caso(caso_id)

            else:
                print(f"{Fore.RED}[ERROR] Opción no válida.{Style.RESET_ALL}")
                pausar()

# Muestra el detalle completo de un caso y permite exportarlo en \Informes\[Caso xxx] - [Nombre Cliente] - [AAAA-MM-DD].txt
def ver_detalle_caso():
    while True:
        listar_casos(usar_pausa=False)
        id_texto = input(f"\n{Fore.BLUE}Ingrese el ID del caso a consultar en detalle (o '0' para cancelar): {Style.RESET_ALL}").strip()
        if id_texto == "0":
            break

        ok_id, caso_id = validar_entero_minimo(id_texto, minimo=1)
        if not ok_id:
            print(f"{Fore.RED}[ERROR] ID de caso inválido.{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a ingresar el valor o cancelar para volver al menú? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar == "r":
                continue
            break

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT c.id, c.descripcion_trabajo, c.estado, c.total_cobrado, cl.nombre_completo, cl.telefono, cl.direccion, cl.email, cl.situacion_fiscal
                FROM casos c
                INNER JOIN clientes cl ON c.cliente_id = cl.id
                WHERE c.id = ?
            """, (caso_id,))
            caso = cursor.fetchone()

            if not caso:
                print(f"{Fore.YELLOW}[INFO] No se encontró el caso #{caso_id}.{Style.RESET_ALL}")
                reintentar = input(
                    f"\n{Fore.YELLOW}¿Desea volver a ingresar el valor o cancelar para volver al menú? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
                ).strip().lower()
                if reintentar == "r":
                    continue
                break

            cursor.execute("""
                SELECT tipo_item, detalle, cantidad, precio_unitario, subtotal
                FROM items_caso
                WHERE caso_id = ?
                ORDER BY id ASC
            """, (caso_id,))
            items = cursor.fetchall()

            estado_visual = formatear_estado_con_color(caso[2])
            nombre_cliente = caso[4]

            fecha_mod = datetime.date.today().strftime("%Y-%m-%d")
            try:
                if os.path.exists("inventario.db"):
                    ts = os.path.getmtime("inventario.db")
                    fecha_mod = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            except OSError:
                fecha_mod = datetime.date.today().strftime("%Y-%m-%d")

            ruta_archivo_salida = construir_nombre_archivo_caso(caso[0], nombre_cliente, fecha_mod)

            lineas_txt = [
                f"Caso Nro: {caso[0]} | Estado: {caso[2]} | Última modificación: {fecha_mod}",
                f"Cliente: {nombre_cliente} | Teléfono: {caso[5]}",
                f"Situación Fiscal: {caso[8] or 'No especificada'}",
                f"Dirección: {caso[6] or 'No informada'} | Email: {caso[7] or 'No informado'}",
                f"Descripción del trabajo: {caso[1]}",
                "--- Detalle de cobro ---"
            ]

            if not items:
                lineas_txt.append("Sin ítems cargados aún.")
            else:
                for item in items:
                    lineas_txt.append(
                        f"[{item[0]}] {item[1]} | Cant: {item[2]} | "
                        f"Unitario: ${item[3]:.2f} | Subtotal: ${item[4]:.2f}"
                    )

            lineas_txt.append(f"TOTAL COBRADO: ${caso[3]:.2f}")
            resumen_txt = "\n".join(lineas_txt)

            limpiar_pantalla()
            imprimir_encabezado(f"Detalle del Caso #{caso[0]}", Fore.GREEN)
            print(f"{Fore.WHITE}Caso Nro: {caso[0]} | Estado: {estado_visual} | Fecha: {fecha_mod}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Cliente: {nombre_cliente} | Teléfono: {caso[5]}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Situación Fiscal: {caso[8] or 'No especificada'}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Dirección: {caso[6] or 'No informada'} | Email: {caso[7] or 'No informado'}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Descripción del trabajo: {caso[1]}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}--- Detalle de cobro ---{Style.RESET_ALL}")

            if not items:
                print(f"{Fore.YELLOW}Sin ítems cargados aún.{Style.RESET_ALL}")
            else:
                for item in items:
                    print(
                        f"{Fore.WHITE}[{item[0]}] {item[1]} | Cant: {item[2]} | "
                        f"Unitario: ${item[3]:.2f} | Subtotal: ${item[4]:.2f}{Style.RESET_ALL}"
                    )

            print(f"\n{Fore.GREEN}{Style.BRIGHT}TOTAL COBRADO: ${caso[3]:.2f}{Style.RESET_ALL}")

            exportar = input(
                f"\n{Fore.BLUE}¿Desea exportar este detalle a '{ruta_archivo_salida}'? (s/N, Enter = No): {Style.RESET_ALL}"
            ).strip().lower()
            if exportar == "s":
                if guardar_informe_txt(f"DETALLE DE CASO #{caso[0]}", resumen_txt, nombre_archivo=ruta_archivo_salida):
                    print(f"{Fore.GREEN}[ÉXITO] Detalle guardado en '{ruta_archivo_salida}'.{Style.RESET_ALL}")
                    registrar_log("EXPORTAR_CASO", f"Exportado caso #{caso[0]} en '{ruta_archivo_salida}'")

            pausar()
            break

        except sqlite3.Error as error:
            print(f"{Fore.RED}[ERROR] Error al obtener detalle del caso: {error}{Style.RESET_ALL}")
            reintentar = input(
                f"\n{Fore.YELLOW}¿Desea volver a ingresar el valor o cancelar para volver al menú? (r para reintentar / c para cancelar): {Style.RESET_ALL}"
            ).strip().lower()
            if reintentar != "r":
                break
        finally:
            conexion.close()