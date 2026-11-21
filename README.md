# Sistema de Gestión Integral para Taller y Servicio Técnico (v1.04)

**Proyecto Final — TalentoTech | Comisión 26205 — Introducción a Python**  
**Autor:** J. Luis Rey (Jonathan Rey)  
**Fecha:** 2026-11-20  

---

## Descripción General

Aplicación de consola desarrollada en Python para la administración integral de un taller y servicio técnico informático/electrónico. Permite gestionar el inventario de repuestos y componentes, controlar categorías, aplicar ajustes porcentuales de precios, administrar la cartera de clientes y hacer el seguimiento completo de casos de reparación con cálculo automático de mano de obra, repuestos utilizados y exportación de comprobantes.

El sistema persiste toda la información en una base de datos local **SQLite** (`inventario.db`) mediante transacciones seguras (`commit()` y `rollback()`), registra actividad automática en `Logs/actividad.log` (con rotación automática al alcanzar 50 MB) y exporta reportes y detalles de casos en formato `.txt` dentro de la subcarpeta `Informes/`.

---

## Funcionalidades Principales

### 1. Inventario y Precios
1. **Registrar producto / componente:** Alta de ítems con nombre (capitalizando la primera letra y respetando mayúsculas internas como `USB`), descripción opcional, categoría, stock inicial y precio unitario.
2. **Listar todos los productos:** Visualización completa del inventario con navegación interactiva mediante flechas cuando la lista supera los 8 registros.
3. **Buscar producto:** Búsqueda por ID exacto, coincidencia parcial de nombre o por categoría.
4. **Actualizar producto por ID:** Edición selectiva de campos (presionando `Enter` se conserva el valor actual).
5. **Eliminar producto por ID:** Baja confirmada con opción por defecto en `No` (`Enter = No`) y posibilidad de seleccionar otro producto o cancelar al menú.
6. **Ajustar precios en general (Subir / Bajar %):** Incremento o rebaja porcentual global sobre todos los productos del inventario, validando que ningún precio quede en cero o negativo.
7. **Reporte de stock bajo o igual a un límite:** Filtrado de productos con existencias iguales o inferiores a un umbral definido y exportación opcional a `Informes/informes.txt`.
8. **Gestionar categorías:** Creación, modificación y eliminación de categorías (con precarga automática de categorías base del taller).

### 2. Clientes y Casos de Servicio Técnico
9. **Registrar cliente:** Alta con nombre completo, teléfono, dirección, email y situación fiscal (`Consumidor Final`, `Responsable Inscripto`, `Monotributista`, `Exento` o `No especificada`).
10. **Listar clientes:** Consulta de todos los clientes registrados.
11. **Abrir nuevo caso de servicio:** Asociación a un cliente existente (o alta rápida de uno nuevo), carga de descripción de falla/trabajo en estado inicial `Abierto` y opción de cargar ítems al momento.
12. **Listar todos los casos:** Visualización general con código de colores por estado (`Abierto`, `En reparación`, `Finalizado`, `Entregado`) y total cobrado.
13. **Filtrar casos por estado:** Consulta segmentada según la etapa del servicio técnico.
14. **Modificar un caso:** Edición integral desde un único menú:
    - Modificar descripción del trabajo (`Enter` pasa sin modificar).
    - Cambiar estado del caso (`Enter` pasa sin modificar).
    - Gestionar ítems (añadir mano de obra o repuestos descontando stock, modificar cantidad/valores o eliminar ítems reintegrando stock y recalculando el total).
15. **Ver detalle de caso y exportar a TXT:** Vista detallada del cliente, trabajos, ítems y total cobrado, con exportación a `Informes/[Caso xxx] - [Nombre Cliente] - [AAAA-MM-DD].txt`.

---

## Estructura del Proyecto

```text
Proyecto-Final/
├── main.py                # Punto de entrada principal (inicializa Logs, BD y menú)
├── menu.py                # Menú interactivo subdividido y navegación principal
├── base_datos.py          # Creación de inventario.db, tablas y claves foráneas
├── inventario.py          # ABM de productos, categorías, ajuste de precios y reportes
├── clientes_y_casos.py    # Gestión de clientes, casos, ítems y exportación
├── validaciones.py        # Validaciones de texto, números, porcentajes y contactos
├── logs_y_reportes.py     # Manejo de consola, colores, Logs (tope 50 MB) e Informes
├── README.md              # Documentación en formato Markdown
└── README.txt             # Documentación en texto plano
```

*(Nota: Los archivos y carpetas `inventario.db`, `Logs/`, `Informes/` y `__pycache__/` se generan automáticamente al ejecutar la aplicación y no se incluyen en el repositorio).*

---

## Requisitos e Instalación

- **Sistema Operativo:** Windows (utiliza `msvcrt` y `cls` para navegación e interfaz en consola).
- **Python:** Python 3.10 o superior.
- **Dependencia externa:** `colorama`

Para instalar `colorama` desde la terminal:

```bash
pip install colorama
```

---

## Ejecución

Ubicado en la carpeta raíz del proyecto, ejecutar:

```bash
python main.py
```