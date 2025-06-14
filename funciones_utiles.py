import subprocess
import logging

ARCHIVO_CONFIG = "servidores.txt"

# verifica si un contenedor existe
def existe_contenedor(nombre):

   # referencia para guardar la salida de la terminal: https://docs.python.org/3/library/subprocess.html#subprocess.check_output

    logging.info(f"Verificando si el contenedor {nombre} existe...")
    try:
        salida = subprocess.check_output(["lxc", "list", nombre], text=True)
        return nombre in salida
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al verificar el contenedor: {e}")
        return False


# verificarç si un bridge existe
def existe_bridge(nombre):
    logging.info(f"Verificando si el bridge {nombre} existe...")
    try:
        # Ejecutar el comando `lxc network list` para verificar si el bridge existe
        salida = subprocess.check_output(["lxc", "network", "list"], text=True)
        return nombre in salida
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al verificar el bridge {nombre}: {e}")
        return False


def contar_servidores():
    with open(ARCHIVO_CONFIG, "r") as f:
        lineas = f.readlines()

    # Filtrar solo los contenedores que no sean cl, db ni lb
    servidores = [
        linea for linea in lineas
        if not any(nombre in linea.strip() for nombre in ("cl", "db", "lb"))
    ]

    return len(servidores)