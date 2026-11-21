# TalentoTech - Proyecto Final: Módulo de Validaciones
# Comisión 26205
# Autor: J. Luis Rey
# Descripción: Funciones de validación de entradas de texto, números, porcentajes, contactos y situación fiscal.
#
# Fecha: 2026-11-20
# Version 1.02

# Lista de situaciones fiscales habituales para clientes
SITUACIONES_FISCALES = [
    "Consumidor Final",
    "Responsable Inscripto",
    "Monotributista",
    "Exento"
]

# Pone en mayúscula solo la primera letra tras strip(), conservando mayúsculas internas (ej. "teclado USB" -> "Teclado USB")
def capitalizar_primera_letra(texto):
    limpio = texto.strip()
    if not limpio:
        return ""
    return limpio[0].upper() + limpio[1:]

# Valida que un texto obligatorio no quede vacío tras quitar espacios
def validar_texto_obligatorio(texto):
    return len(texto.strip()) > 0

# Valida que un valor ingresado sea un número entero mayor o igual a un mínimo
def validar_entero_minimo(valor_texto, minimo=0):
    try:
        numero = int(valor_texto.strip())
        if numero >= minimo:
            return True, numero
        return False, None
    except ValueError:
        return False, None

# Valida que un valor ingresado sea un número decimal mayor que cero
def validar_decimal_mayor_cero(valor_texto):
    texto_limpio = valor_texto.strip().replace(",", ".")
    try:
        numero = float(texto_limpio)
        if numero > 0:
            return True, numero
        return False, None
    except ValueError:
        return False, None

# Valida un porcentaje de ajuste mayor que cero (usado tanto para subir como para bajar)
def validar_porcentaje_ajuste(valor_texto):
    return validar_decimal_mayor_cero(valor_texto)

# Valida que el teléfono no esté vacío y tenga dígitos suficientes
def validar_telefono(telefono_texto):
    limpio = (
        telefono_texto.strip()
        .replace("-", "")
        .replace(" ", "")
        .replace("(", "")
        .replace(")", "")
    )
    if limpio.startswith("+"):
        limpio = limpio[1:]
    return len(limpio) >= 6 and limpio.isdigit()

# Valida un email opcional: vacío es válido; si tiene texto, exige '@' y '.' sin espacios
def validar_email_opcional(email_texto):
    email_limpio = email_texto.strip().lower()
    if email_limpio == "":
        return True, ""
    if " " in email_limpio or "@" not in email_limpio or "." not in email_limpio:
        return False, None
    return True, email_limpio

# Normaliza la situación fiscal opcional o devuelve "No especificada" si queda vacía
def validar_situacion_fiscal_opcional(opcion_texto):
    limpio = opcion_texto.strip()
    if limpio == "":
        return True, "No especificada"
    if limpio.isdigit():
        indice = int(limpio) - 1
        if 0 <= indice < len(SITUACIONES_FISCALES):
            return True, SITUACIONES_FISCALES[indice]
        return False, None
    for situacion in SITUACIONES_FISCALES:
        if limpio.lower() == situacion.lower():
            return True, situacion
    return False, None