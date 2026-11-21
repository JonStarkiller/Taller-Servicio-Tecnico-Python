# TalentoTech - Proyecto Final: Módulo de Inventario, Categorías y Precios
# Comisión 26205
# Autor: J. Luis Rey
# Descripción: Gestiona el ABM de productos, categorías, ajuste porcentual de precios (subir/bajar) y reportes de stock.
#
# Fecha: 2026-11-20
# Version 1.02

import sqlite3
from colorama import Fore, Style
from base_datos import conectar
from logs_y_reportes import (
    registrar_log,
    guardar_informe_txt,
    limpiar_pantalla,
    pausar,
    imprimir_encabezado,
    mostrar_lista_interactiva
)
from validaciones import (
    capitalizar_primera_letra,
    validar_texto_obligatorio,
    validar_entero_minimo,
    validar_decimal_mayor_cero,
    validar_porcentaje_ajuste
)

# Obtiene la lista ordenada de categorías desde la base de datos
def obtener_categorias():
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT id, nombre FROM categorias ORDER BY id ASC")
        return cursor.fetchall()
    except sqlite3.Error as error:
        print(f"{Fore.RED}[ERROR] Error al consultar categorías: {error}{Style.RESET_ALL}")
        return []
    finally:
        conexion.close()

# Permite seleccionar una categoría existente o crear una nueva si aún no existe
def seleccionar_o_crear_categoria(permitir_vacio=False, categoria_actual=None):
    categorias = obtener_categorias()

    print(f"\n{Fore.BLUE}--- Categorías Disponibles ---{Style.RESET_ALL}")
    if categorias:
        for cat in categorias:
            print(f"  {Fore.WHITE}{cat[0]}. {cat[1]}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.YELLOW}No hay categorías cargadas aún.{Style.RESET_ALL}")

    print(f"  {Fore.GREEN}N. Crear una nueva categoría{Style.RESET_ALL}")
    if permitir_vacio and categoria_actual:
        print(f"  {Fore.CYAN}[Enter] Conservar actual ({categoria_actual}){Style.RESET_ALL}")

    while True:
        entrada = input(f"\n{Fore.CYAN}Seleccione número de categoría o 'N' para crear: {Style.RESET_ALL}").strip()

        if permitir_vacio and entrada == "" and categoria_actual:
            return True, categoria_actual

        if entrada.lower() == "n":
            nuevo_nombre = capitalizar_primera_letra(input("Ingrese el nombre de la nueva categoría: "))
            if not validar_texto_obligatorio(nuevo_nombre):
                print(f"{Fore.RED}[ERROR] El nombre de la categoría no puede estar vacío.{Style.RESET_ALL}")
                continue

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("SELECT nombre FROM categorias WHERE LOWER(nombre) = LOWER(?)", (nuevo_nombre,))
                existente = cursor.fetchone()
                if existente:
                    conexion.rollback()
                    print(f"{Fore.YELLOW}[INFO] La categoría '{existente[0]}' ya existe. Se seleccionará esa.{Style.RESET_ALL}")
                    return True, existente[0]

                cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nuevo_nombre,))
                conexion.commit()
                print(f"{Fore.GREEN}[ÉXITO] Categoría '{nuevo_nombre}' creada y seleccionada.{Style.RESET_ALL}")
                registrar_log("CATEGORIA_ALTA", f"Nueva categoría '{nuevo_nombre}'")
                return True, nuevo_nombre
            except sqlite3.Error as error:
                conexion.rollback()
                print(f"{Fore.RED}[ERROR] No se pudo crear la categoría: {error}{Style.RESET_ALL}")
                return False, None
            finally:
                conexion.close()

        ok_id, id_cat = validar_entero_minimo(entrada, minimo=1)
        if not ok_id:
            print(f"{Fore.RED}[ERROR] Ingrese un número válido o 'N' para crear una categoría.{Style.RESET_ALL}")
            continue

        for cat in categorias:
            if cat[0] == id_cat:
                return True, cat[1]

        print(f"{Fore.RED}[ERROR] No existe una categoría con el ID {id_cat}.{Style.RESET_ALL}")

# Menú de administración de categorías: listar, crear, modificar y eliminar
def gestionar_categorias():
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Gestión de Categorías", Fore.MAGENTA)
        categorias = obtener_categorias()

        if categorias:
            for cat in categorias:
                print(f"  {Fore.WHITE}ID {cat[0]}: {cat[1]}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}[INFO] No hay categorías registradas.{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}1. Crear nueva categoría{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Modificar categoría existente{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Eliminar categoría existente{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}0. Volver al menú principal{Style.RESET_ALL}")

        opcion = input(f"\n{Fore.CYAN}Seleccione una opción: {Style.RESET_ALL}").strip()

        if opcion == "0":
            break

        elif opcion == "1":
            nuevo_nombre = capitalizar_primera_letra(input("Nombre de la nueva categoría: "))
            if not validar_texto_obligatorio(nuevo_nombre):
                print(f"{Fore.RED}[ERROR] El nombre no puede estar vacío.{Style.RESET_ALL}")
                pausar()
                continue

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("SELECT id FROM categorias WHERE LOWER(nombre) = LOWER(?)", (nuevo_nombre,))
                if cursor.fetchone():
                    conexion.rollback()
                    print(f"{Fore.YELLOW}[INFO] Esa categoría ya existe.{Style.RESET_ALL}")
                else:
                    cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nuevo_nombre,))
                    conexion.commit()
                    print(f"{Fore.GREEN}[ÉXITO] Categoría '{nuevo_nombre}' agregada.{Style.RESET_ALL}")
                    registrar_log("CATEGORIA_ALTA", f"Creada categoría '{nuevo_nombre}'")
            except sqlite3.Error as error:
                conexion.rollback()
                print(f"{Fore.RED}[ERROR] Error al crear categoría: {error}{Style.RESET_ALL}")
            finally:
                conexion.close()
            pausar()

        elif opcion == "2":
            if not categorias:
                print(f"{Fore.YELLOW}[INFO] No hay categorías para modificar.{Style.RESET_ALL}")
                pausar()
                continue

            id_txt = input("Ingrese el ID de la categoría a modificar: ").strip()
            ok_id, id_cat = validar_entero_minimo(id_txt, minimo=1)
            if not ok_id:
                print(f"{Fore.RED}[ERROR] ID inválido.{Style.RESET_ALL}")
                pausar()
                continue

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                cursor.execute("SELECT nombre FROM categorias WHERE id = ?", (id_cat,))
                actual = cursor.fetchone()
                if not actual:
                    print(f"{Fore.YELLOW}[INFO] No existe una categoría con ID {id_cat}.{Style.RESET_ALL}")
                    conexion.close()
                    pausar()
                    continue

                nuevo_nombre = capitalizar_primera_letra(input(f"Nuevo nombre para '{actual[0]}': "))
                if not validar_texto_obligatorio(nuevo_nombre):
                    print(f"{Fore.RED}[ERROR] El nuevo nombre no puede estar vacío.{Style.RESET_ALL}")
                    conexion.close()
                    pausar()
                    continue

                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("UPDATE categorias SET nombre = ? WHERE id = ?", (nuevo_nombre, id_cat))
                cursor.execute("UPDATE productos SET categoria = ? WHERE categoria = ?", (nuevo_nombre, actual[0]))
                conexion.commit()

                print(f"{Fore.GREEN}[ÉXITO] Categoría '{actual[0]}' actualizada a '{nuevo_nombre}'.{Style.RESET_ALL}")
                registrar_log("CATEGORIA_MOD", f"ID {id_cat}: '{actual[0]}' -> '{nuevo_nombre}'")
            except sqlite3.Error as error:
                conexion.rollback()
                print(f"{Fore.RED}[ERROR] Error al modificar categoría (verifique que no esté duplicada): {error}{Style.RESET_ALL}")
            finally:
                conexion.close()
            pausar()

        elif opcion == "3":
            if not categorias:
                print(f"{Fore.YELLOW}[INFO] No hay categorías para eliminar.{Style.RESET_ALL}")
                pausar()
                continue

            id_txt = input("Ingrese el ID de la categoría a eliminar: ").strip()
            ok_id, id_cat = validar_entero_minimo(id_txt, minimo=1)
            if not ok_id:
                print(f"{Fore.RED}[ERROR] ID inválido.{Style.RESET_ALL}")
                pausar()
                continue

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                cursor.execute("SELECT nombre FROM categorias WHERE id = ?", (id_cat,))
                actual = cursor.fetchone()
                if not actual:
                    print(f"{Fore.YELLOW}[INFO] No existe una categoría con ID {id_cat}.{Style.RESET_ALL}")
                    conexion.close()
                    pausar()
                    continue

                confirmacion = input(
                    f"{Fore.YELLOW}¿Confirma eliminar la categoría '{actual[0]}'? (s/N, Enter = No): {Style.RESET_ALL}"
                ).strip().lower()
                if confirmacion != "s":
                    print(f"{Fore.BLUE}[INFO] Eliminación cancelada.{Style.RESET_ALL}")
                    conexion.close()
                    pausar()
                    continue

                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("DELETE FROM categorias WHERE id = ?", (id_cat,))
                cursor.execute(
                    "UPDATE productos SET categoria = 'Repuestos Varios' WHERE categoria = ?",
                    (actual[0],)
                )
                conexion.commit()

                print(f"{Fore.GREEN}[ÉXITO] Categoría '{actual[0]}' eliminada.{Style.RESET_ALL}")
                registrar_log("CATEGORIA_BAJA", f"Eliminada categoría '{actual[0]}'")
            except sqlite3.Error as error:
                conexion.rollback()
                print(f"{Fore.RED}[ERROR] Error al eliminar categoría: {error}{Style.RESET_ALL}")
            finally:
                conexion.close()
            pausar()

        else:
            print(f"{Fore.RED}[ERROR] Opción no válida.{Style.RESET_ALL}")
            pausar()

# Convierte filas de productos en líneas de texto legibles para consola y navegación
def formatear_lineas_productos(productos):
    lineas = []
    for prod in productos:
        descripcion = prod[2] if prod[2] else "Sin descripción"
        categoria = prod[5] if prod[5] else "Repuestos Varios"
        lineas.append(
            f"ID: {prod[0]} | {prod[1]} | Cat: {categoria} | "
            f"Stock: {prod[3]} | Precio: ${prod[4]:.2f} | Desc: {descripcion}"
        )
    return lineas

# Alta de productos con opción de añadir otro o volver al menú principal al finalizar
def registrar_producto():
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Registrar Nuevo Producto / Componente", Fore.CYAN)

        nombre = capitalizar_primera_letra(input("Nombre del producto: "))
        if not validar_texto_obligatorio(nombre):
            print(f"{Fore.RED}[ERROR] El nombre del producto no puede estar vacío.{Style.RESET_ALL}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar el registro? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar == "s":
                continue
            break

        descripcion = capitalizar_primera_letra(input("Descripción (opcional): "))

        ok_cat, categoria = seleccionar_o_crear_categoria(permitir_vacio=False)
        if not ok_cat:
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar el registro? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar == "s":
                continue
            break

        cantidad_texto = input("Cantidad inicial en stock: ").strip()
        ok_cant, cantidad = validar_entero_minimo(cantidad_texto, minimo=0)
        if not ok_cant:
            print(f"{Fore.RED}[ERROR] La cantidad debe ser un número entero mayor o igual a 0.{Style.RESET_ALL}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar el registro? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar == "s":
                continue
            break

        precio_texto = input("Precio unitario ($): ").strip()
        ok_precio, precio = validar_decimal_mayor_cero(precio_texto)
        if not ok_precio:
            print(f"{Fore.RED}[ERROR] El precio debe ser un número mayor que 0.{Style.RESET_ALL}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar el registro? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar == "s":
                continue
            break

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("""
                INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, descripcion, cantidad, precio, categoria))
            conexion.commit()

            print(f"\n{Fore.GREEN}[ÉXITO] Producto '{nombre}' registrado en '{categoria}'.{Style.RESET_ALL}")
            registrar_log("INVENTARIO_ALTA", f"Producto '{nombre}' [{categoria}] (Stock: {cantidad}, Precio: ${precio:.2f})")
        except sqlite3.Error as error:
            conexion.rollback()
            print(f"{Fore.RED}[ERROR] No se pudo registrar el producto: {error}{Style.RESET_ALL}")
            registrar_log("ERROR_BD", f"Fallo al registrar producto '{nombre}': {error}")
        finally:
            conexion.close()

        agregar_otro = input(
            f"\n{Fore.CYAN}¿Desea añadir otro producto? (s para añadir otro / N o Enter para volver al menú): {Style.RESET_ALL}"
        ).strip().lower()
        if agregar_otro != "s":
            break

# Consulta todos los productos almacenados en el inventario
def listar_productos():
    limpiar_pantalla()
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT id, nombre, descripcion, cantidad, precio, categoria
            FROM productos
            ORDER BY id ASC
        """)
        productos = cursor.fetchall()

        if not productos:
            imprimir_encabezado("Inventario de Componentes y Repuestos", Fore.CYAN)
            print(f"{Fore.YELLOW}[INFO] No hay productos cargados en el inventario.{Style.RESET_ALL}")
        else:
            lineas = formatear_lineas_productos(productos)
            mostrar_lista_interactiva("Inventario de Componentes y Repuestos", lineas, Fore.CYAN)
    except sqlite3.Error as error:
        print(f"{Fore.RED}[ERROR] Error al consultar productos: {error}{Style.RESET_ALL}")
    finally:
        conexion.close()
    pausar()

# Busca productos permitiendo reintentar ante error/sin resultados y volver al menú principal
def buscar_productos():
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Buscar Productos", Fore.CYAN)
        print("1. Buscar por ID")
        print("2. Buscar por nombre")
        print("3. Buscar por categoría")
        print("0. Salir y volver al menú principal")
        opcion = input(f"\n{Fore.CYAN}Seleccione una opción: {Style.RESET_ALL}").strip()

        if opcion == "0":
            break

        conexion = conectar()
        cursor = conexion.cursor()
        productos = []
        titulo_res = ""
        error_entrada = False

        try:
            if opcion == "1":
                id_texto = input("Ingrese el ID del producto: ").strip()
                ok_id, id_prod = validar_entero_minimo(id_texto, minimo=1)
                if not ok_id:
                    print(f"{Fore.RED}[ERROR] El ID debe ser un número entero positivo.{Style.RESET_ALL}")
                    error_entrada = True
                else:
                    cursor.execute("""
                        SELECT id, nombre, descripcion, cantidad, precio, categoria
                        FROM productos
                        WHERE id = ?
                    """, (id_prod,))
                    productos = cursor.fetchall()
                    titulo_res = f"Búsqueda por ID: {id_prod}"

            elif opcion == "2":
                nombre_buscar = input("Ingrese el nombre o parte del nombre: ").strip()
                if not validar_texto_obligatorio(nombre_buscar):
                    print(f"{Fore.RED}[ERROR] Debe ingresar un texto para buscar.{Style.RESET_ALL}")
                    error_entrada = True
                else:
                    cursor.execute("""
                        SELECT id, nombre, descripcion, cantidad, precio, categoria
                        FROM productos
                        WHERE nombre LIKE ?
                        ORDER BY nombre ASC
                    """, (f"%{nombre_buscar}%",))
                    productos = cursor.fetchall()
                    titulo_res = f"Búsqueda por nombre: '{nombre_buscar}'"

            elif opcion == "3":
                ok_cat, cat_buscar = seleccionar_o_crear_categoria(permitir_vacio=False)
                if not ok_cat:
                    error_entrada = True
                else:
                    cursor.execute("""
                        SELECT id, nombre, descripcion, cantidad, precio, categoria
                        FROM productos
                        WHERE categoria = ?
                        ORDER BY nombre ASC
                    """, (cat_buscar,))
                    productos = cursor.fetchall()
                    titulo_res = f"Categoría: {cat_buscar}"

            else:
                print(f"{Fore.RED}[ERROR] Opción de búsqueda no válida.{Style.RESET_ALL}")
                error_entrada = True

            if not error_entrada:
                if not productos:
                    print(f"\n{Fore.YELLOW}[INFO] No se encontraron productos con ese criterio.{Style.RESET_ALL}")
                    pausar()
                else:
                    lineas = formatear_lineas_productos(productos)
                    mostrar_lista_interactiva(titulo_res, lineas, Fore.GREEN)
                    pausar()
            else:
                pausar()

        except sqlite3.Error as error:
            print(f"{Fore.RED}[ERROR] Error al buscar productos: {error}{Style.RESET_ALL}")
            pausar()
        finally:
            conexion.close()

        seguir = input(
            f"\n{Fore.CYAN}¿Desea volver a buscar? (s para buscar de nuevo / N o Enter para volver al menú): {Style.RESET_ALL}"
        ).strip().lower()
        if seguir != "s":
            break

# Modifica un producto permitiendo reintentar ante error o volver al menú principal
def actualizar_producto():
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Actualizar Producto por ID", Fore.CYAN)

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT id, nombre, descripcion, cantidad, precio, categoria
                FROM productos
                ORDER BY id ASC
            """)
            todos = cursor.fetchall()
            if not todos:
                print(f"{Fore.YELLOW}[INFO] No hay productos cargados.{Style.RESET_ALL}")
                pausar()
                break

            for linea in formatear_lineas_productos(todos):
                print(f"{Fore.WHITE}{linea}{Style.RESET_ALL}")

            id_texto = input(f"\n{Fore.BLUE}Ingrese el ID del producto a modificar (o '0' para volver al menú): {Style.RESET_ALL}").strip()
            if id_texto == "0":
                break

            ok_id, id_prod = validar_entero_minimo(id_texto, minimo=1)
            if not ok_id:
                print(f"{Fore.RED}[ERROR] ID inválido.{Style.RESET_ALL}")
                reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
                if reintentar == "s":
                    continue
                break

            cursor.execute("""
                SELECT id, nombre, descripcion, cantidad, precio, categoria
                FROM productos
                WHERE id = ?
            """, (id_prod,))
            actual = cursor.fetchone()

            if not actual:
                print(f"{Fore.YELLOW}[INFO] No existe un producto con el ID {id_prod}.{Style.RESET_ALL}")
                reintentar = input(f"\n{Fore.YELLOW}¿Desea intentar con otro ID? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
                if reintentar == "s":
                    continue
                break

            print(f"\n{Fore.BLUE}Deje en blanco (Enter) para conservar el valor actual.{Style.RESET_ALL}")

            nuevo_nombre = capitalizar_primera_letra(input(f"Nombre [{actual[1]}]: "))
            nombre_final = actual[1] if nuevo_nombre == "" else nuevo_nombre

            nueva_desc = capitalizar_primera_letra(input(f"Descripción [{actual[2] or 'Sin descripción'}]: "))
            desc_final = actual[2] if nueva_desc == "" else nueva_desc

            ok_cat, cat_final = seleccionar_o_crear_categoria(
                permitir_vacio=True,
                categoria_actual=actual[5] or "Repuestos Varios"
            )
            if not ok_cat:
                reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar la actualización? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
                if reintentar == "s":
                    continue
                break

            nueva_cant_texto = input(f"Cantidad en stock [{actual[3]}]: ").strip()
            if nueva_cant_texto == "":
                cant_final = actual[3]
            else:
                ok_cant, cant_final = validar_entero_minimo(nueva_cant_texto, minimo=0)
                if not ok_cant:
                    print(f"{Fore.RED}[ERROR] Cantidad inválida. Debe ser un entero mayor o igual a 0.{Style.RESET_ALL}")
                    reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar la actualización? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
                    if reintentar == "s":
                        continue
                    break

            nuevo_precio_texto = input(f"Precio [${actual[4]:.2f}]: ").strip()
            if nuevo_precio_texto == "":
                precio_final = actual[4]
            else:
                ok_precio, precio_final = validar_decimal_mayor_cero(nuevo_precio_texto)
                if not ok_precio:
                    print(f"{Fore.RED}[ERROR] Precio inválido. Debe ser mayor que 0.{Style.RESET_ALL}")
                    reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar la actualización? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
                    if reintentar == "s":
                        continue
                    break

            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("""
                UPDATE productos
                SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?
                WHERE id = ?
            """, (nombre_final, desc_final, cant_final, precio_final, cat_final, id_prod))
            conexion.commit()

            print(f"\n{Fore.GREEN}[ÉXITO] Producto ID {id_prod} actualizado correctamente.{Style.RESET_ALL}")
            registrar_log(
                "INVENTARIO_MODIFICACION",
                f"ID {id_prod} ('{nombre_final}') [{cat_final}] -> Stock: {cant_final}, Precio: ${precio_final:.2f}"
            )
            pausar()
            break

        except sqlite3.Error as error:
            conexion.rollback()
            print(f"{Fore.RED}[ERROR] Error al actualizar producto: {error}{Style.RESET_ALL}")
            registrar_log("ERROR_BD", f"Fallo al modificar producto ID {id_prod}: {error}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar != "s":
                break
        finally:
            conexion.close()

# Elimina un producto aclarando Enter = No y permitiendo elegir otro o volver al menú si se cancela/falla
def eliminar_producto():
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Eliminar Producto por ID", Fore.RED)

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id, nombre, cantidad, precio, categoria FROM productos ORDER BY id ASC")
            todos = cursor.fetchall()
            if not todos:
                print(f"{Fore.YELLOW}[INFO] No hay productos cargados.{Style.RESET_ALL}")
                pausar()
                break

            for prod in todos:
                print(
                    f"{Fore.WHITE}ID: {prod[0]} | {prod[1]} | Cat: {prod[4] or 'General'} | "
                    f"Stock: {prod[2]} | Precio: ${prod[3]:.2f}{Style.RESET_ALL}"
                )

            id_texto = input(f"\n{Fore.BLUE}Ingrese el ID del producto a eliminar (o '0' para volver al menú): {Style.RESET_ALL}").strip()
            if id_texto == "0":
                break

            ok_id, id_prod = validar_entero_minimo(id_texto, minimo=1)
            if not ok_id:
                print(f"{Fore.RED}[ERROR] ID inválido.{Style.RESET_ALL}")
                reintentar = input(f"\n{Fore.YELLOW}¿Desea ingresar otro ID o cancelar? (s para otro / N o Enter para volver al menú): {Style.RESET_ALL}").strip().lower()
                if reintentar == "s":
                    continue
                break

            cursor.execute("SELECT id, nombre, cantidad, precio FROM productos WHERE id = ?", (id_prod,))
            prod = cursor.fetchone()

            if not prod:
                print(f"{Fore.YELLOW}[INFO] No se encontró ningún producto con el ID {id_prod}.{Style.RESET_ALL}")
                reintentar = input(f"\n{Fore.YELLOW}¿Desea ingresar otro ID o cancelar? (s para otro / N o Enter para volver al menú): {Style.RESET_ALL}").strip().lower()
                if reintentar == "s":
                    continue
                break

            print(
                f"\n{Fore.YELLOW}Seleccionado -> ID: {prod[0]} | Nombre: {prod[1]} | "
                f"Stock: {prod[2]} | Precio: ${prod[3]:.2f}{Style.RESET_ALL}"
            )
            confirmacion = input(
                f"{Fore.YELLOW}¿Confirma eliminar este producto? (s/N, Enter = No): {Style.RESET_ALL}"
            ).strip().lower()

            if confirmacion != "s":
                print(f"{Fore.BLUE}[INFO] Eliminación cancelada.{Style.RESET_ALL}")
                otro = input(
                    f"\n{Fore.CYAN}¿Desea seleccionar otro producto para eliminar o cancelar para volver al menú? (s para otro / N o Enter para volver): {Style.RESET_ALL}"
                ).strip().lower()
                if otro == "s":
                    continue
                break

            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
            conexion.commit()

            print(f"\n{Fore.GREEN}[ÉXITO] Producto '{prod[1]}' eliminado correctamente.{Style.RESET_ALL}")
            registrar_log("INVENTARIO_BAJA", f"Eliminado ID {prod[0]} ('{prod[1]}')")
            pausar()
            break

        except sqlite3.Error as error:
            conexion.rollback()
            print(f"{Fore.RED}[ERROR] No se pudo eliminar el producto (puede estar asociado a un caso): {error}{Style.RESET_ALL}")
            registrar_log("ERROR_BD", f"Fallo al eliminar producto ID {id_prod}: {error}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea intentar con otro producto? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar != "s":
                break
        finally:
            conexion.close()

# Aplica un aumento o rebaja porcentual general a todos los precios del inventario
def ajustar_precios_porcentaje():
    while True:
        limpiar_pantalla()
        imprimir_encabezado("Ajuste General de Precios por Porcentaje", Fore.CYAN)
        print("1. Aumentar precios en general (%)")
        print("2. Bajar precios en general (%)")
        print("0. Volver al menú principal")

        modo = input(f"\n{Fore.CYAN}Seleccione tipo de ajuste: {Style.RESET_ALL}").strip()
        if modo == "0":
            break

        if modo not in ("1", "2"):
            print(f"{Fore.RED}[ERROR] Opción no válida.{Style.RESET_ALL}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar == "s":
                continue
            break

        accion_txt = "aumentar" if modo == "1" else "bajar"
        signo_txt = "+" if modo == "1" else "-"

        porcentaje_texto = input(f"Ingrese el porcentaje a {accion_txt} (ej. 15 para {signo_txt}15%): ").strip()
        ok_porc, porcentaje = validar_porcentaje_ajuste(porcentaje_texto)
        if not ok_porc:
            print(f"{Fore.RED}[ERROR] El porcentaje debe ser un número mayor que 0.{Style.RESET_ALL}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar == "s":
                continue
            break

        if modo == "2" and porcentaje >= 100:
            print(f"{Fore.RED}[ERROR] No se puede bajar un {porcentaje:.2f}% porque dejaría precios en 0 o negativos.{Style.RESET_ALL}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar con otro porcentaje? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar == "s":
                continue
            break

        confirmacion = input(
            f"{Fore.YELLOW}¿Está seguro de aplicar un {signo_txt}{porcentaje:.2f}% a TODOS los productos? (s/N, Enter = No): {Style.RESET_ALL}"
        ).strip().lower()
        if confirmacion != "s":
            print(f"{Fore.BLUE}[INFO] Ajuste cancelado.{Style.RESET_ALL}")
            pausar()
            break

        if modo == "1":
            factor = 1 + (porcentaje / 100.0)
        else:
            factor = 1 - (porcentaje / 100.0)

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("SELECT COUNT(*) FROM productos")
            total_productos = cursor.fetchone()[0]

            if total_productos == 0:
                conexion.rollback()
                print(f"{Fore.YELLOW}[INFO] No hay productos para actualizar.{Style.RESET_ALL}")
                pausar()
                break

            cursor.execute("SELECT MIN(ROUND(precio * ?, 2)) FROM productos", (factor,))
            min_nuevo = cursor.fetchone()[0]
            if min_nuevo is None or min_nuevo <= 0:
                conexion.rollback()
                print(f"{Fore.RED}[ERROR] El ajuste dejaría algún precio en $0.00 o menor. Operación cancelada.{Style.RESET_ALL}")
                pausar()
                break

            cursor.execute("UPDATE productos SET precio = ROUND(precio * ?, 2)", (factor,))
            conexion.commit()

            print(f"\n{Fore.GREEN}[ÉXITO] Se aplicó un {signo_txt}{porcentaje:.2f}% a {total_productos} producto(s).{Style.RESET_ALL}")
            registrar_log("AJUSTE_PRECIOS", f"{signo_txt}{porcentaje:.2f}% aplicado a {total_productos} productos")
            pausar()
            break
        except sqlite3.Error as error:
            conexion.rollback()
            print(f"{Fore.RED}[ERROR] Error al actualizar precios: {error}{Style.RESET_ALL}")
            registrar_log("ERROR_BD", f"Fallo en ajuste de precios {signo_txt}{porcentaje:.2f}%: {error}")
            reintentar = input(f"\n{Fore.YELLOW}¿Desea reintentar? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
            if reintentar != "s":
                break
        finally:
            conexion.close()

# Genera un reporte de productos con stock igual o inferior a un límite indicado
def reporte_bajo_stock():
    limpiar_pantalla()
    imprimir_encabezado("Reporte de Stock Bajo o Igual al Límite", Fore.CYAN)

    limite_texto = input("Ingrese el límite máximo de stock a consultar: ").strip()
    ok_lim, limite = validar_entero_minimo(limite_texto, minimo=0)
    if not ok_lim:
        print(f"{Fore.RED}[ERROR] El límite debe ser un número entero mayor o igual a 0.{Style.RESET_ALL}")
        pausar()
        return

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT id, nombre, categoria, cantidad, precio
            FROM productos
            WHERE cantidad <= ?
            ORDER BY cantidad ASC, nombre ASC
        """, (limite,))
        productos = cursor.fetchall()

        if not productos:
            print(f"\n{Fore.GREEN}[INFO] Todos los productos superan el límite de {limite} unidades.{Style.RESET_ALL}")
            pausar()
            return

        lineas_reporte = []
        for prod in productos:
            lineas_reporte.append(
                f"ID: {prod[0]} | Nombre: {prod[1]} | Categoría: {prod[2] or 'General'} | "
                f"Stock: {prod[3]} | Precio: ${prod[4]:.2f}"
            )

        mostrar_lista_interactiva(f"Stock <= {limite}", lineas_reporte, Fore.YELLOW)

        guardar = input(f"\n{Fore.BLUE}¿Desea exportar este reporte a informes.txt? (s/N, Enter = No): {Style.RESET_ALL}").strip().lower()
        if guardar == "s":
            contenido = "\n".join(lineas_reporte)
            if guardar_informe_txt(f"REPORTE DE STOCK <= {limite}", contenido):
                print(f"{Fore.GREEN}[ÉXITO] Reporte guardado en informes.txt.{Style.RESET_ALL}")
                registrar_log("REPORTE_STOCK", f"Exportado reporte stock <= {limite} ({len(productos)} ítems)")
    except sqlite3.Error as error:
        print(f"{Fore.RED}[ERROR] Error al generar reporte de stock: {error}{Style.RESET_ALL}")
    finally:
        conexion.close()
    pausar()