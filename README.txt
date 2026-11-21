================================================================================
  SISTEMA DE GESTIÓN INTEGRAL PARA TALLER Y SERVICIO TÉCNICO (v1.04)
================================================================================
  Proyecto Final - TalentoTech | Comisión 26205 - Introducción a Python
  Autor: J. Luis Rey (Jonathan Rey)
  Fecha: 2026-11-20
================================================================================

1. DESCRIPCIÓN GENERAL
----------------------
Aplicación de consola desarrollada en Python para la gestión integral de un
taller y servicio técnico. Permite administrar el inventario de repuestos y
componentes, gestionar categorías, aplicar aumentos o rebajas porcentuales
generales de precios, registrar clientes y controlar casos de reparación con
detalle de mano de obra, repuestos utilizados y exportación de comprobantes.

Toda la información se almacena en una base de datos local SQLite
(inventario.db) utilizando transacciones seguras (commit y rollback). Además,
el sistema registra eventos en Logs/actividad.log (con reinicio automático al
alcanzar los 50 MB) y exporta reportes y casos en la subcarpeta Informes/.


2. FUNCIONALIDADES DEL MENÚ PRINCIPAL
-------------------------------------
[ INVENTARIO Y PRECIOS ]
  1. Registrar producto / componente
  2. Listar todos los productos (con desplazamiento por flechas si es extensa)
  3. Buscar producto (por ID, Nombre o Categoría)
  4. Actualizar producto por ID (Enter conserva los valores actuales)
  5. Eliminar producto por ID (con confirmación s/N, Enter = No)
  6. Ajustar precios en general (Subir o Bajar por porcentaje %)
  7. Reporte de stock igual o menor a un límite (exportable a TXT)
  8. Gestionar categorías (Crear, Modificar o Eliminar)

[ CLIENTES Y CASOS ]
   9. Registrar cliente (datos de contacto y situación fiscal)
  10. Listar clientes
  11. Abrir nuevo caso de servicio
  12. Listar todos los casos (con colores diferenciados por estado)
  13. Filtrar casos por estado (Abierto, En reparación, Finalizado, Entregado)
  14. Modificar un caso (descripción, estado y gestión de ítems unificada)
  15. Ver detalle de caso y exportar a TXT en:
      Informes\[Caso xxx] - [Nombre Cliente] - [AAAA-MM-DD].txt

  0. Salir del sistema


3. ESTRUCTURA DE ARCHIVOS DEL PROYECTO
--------------------------------------
  - main.py             : Punto de entrada principal del programa.
  - menu.py             : Menú principal subdividido en consola.
  - base_datos.py       : Inicialización de inventario.db y tablas SQLite.
  - inventario.py       : Gestión de productos, categorías, precios y stock.
  - clientes_y_casos.py : Gestión de clientes, casos, ítems y exportación.
  - validaciones.py     : Validaciones de entradas y formato de texto.
  - logs_y_reportes.py  : Control de Logs (50 MB), Informes y visualización.
  - README.md           : Documentación del proyecto en Markdown.
  - README.txt          : Documentación del proyecto en texto plano.

Nota: El archivo inventario.db y las carpetas Logs/, Informes/ y __pycache__/
se crean automáticamente al ejecutar el sistema y se omiten al subir el código.


4. REQUISITOS Y EJECUCIÓN
-------------------------
  - Sistema operativo: Windows (consola con soporte UTF-8).
  - Python 3.10 o superior.
  - Librería externa: colorama

  Instalación de dependencia:
    pip install colorama

  Ejecución del sistema:
    python main.py
================================================================================