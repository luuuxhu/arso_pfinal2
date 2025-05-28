# Lucía Xiaoshu García García
# Valeria Teran Cruz
# Martina Montesdeoca Luzuriaga

## OPERACIONES CREAR/EMPEZAR/LISTAR/BORRAR ##
import sys
import subprocess
import logging
import time
from crear import crear_escenario
from crear import crear_contenedor
from list_contenedores import list
from start_escenario import start
from stop_escenario import stop
from delete_escenario import delete
from configurar_remoto import conectarB, obtener_ipB
from configurar_local import configA, bridge_remoto
from configure import configurar_servidores, configurar_basedatos, configurar_balanceador, configurar_haproxy
from instalar_node_servidores import instalar_app_en_servidores

accion = sys.argv[1]  # esto va a ser el primer argumento del comando --> se usa abajo en el main

# Configuración para guardar los logs en un archivo y añadirlos en cada ejecución
logging.basicConfig(
    filename='logs.log',  # Archivo donde se guardarán los logs
    level=logging.DEBUG,     # Nivel de los mensajes a registrar
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del mensaje / fecha nivel mensaje
    filemode='a'   # 'a' para añadir los nuevos logs al final del archivo (en vez de sobrescribir)
)



## MENÚ DE AYUDA


def mostrar_ayuda():
   print("""
*.*.* USO DE NUESTRO SCRIPT *.*.*


Comandos disponibles:


 python3 pfinal1.py help                       - Mostrar esta ayuda
 python3 pfinal1.py create [num_servidores]    - Crear escenario (2 servidores por defecto y 5 como máximo)
 python3 pfinal1.py create_contenedor <nombre> - Crear contenedor individual
 python3 pfinal1.py start                      - Iniciar todos los componentes del escenario o uno en concreto. Siga las instrucciones.
 python3 pfinal1.py list                       - Listar contenedores
 python3 pfinal1.py delete                     - Eliminar todos los componentes del escenario o uno en concreto. Siga las instrucciones.
 python3 pfinal2.py configure                  - Configurar app web, base de datos y balanceador
 python3 pfinal2.py stop                       - Parar todos los componentes del escenario o uno en concreto. Siga las instrucciones.


""")

# LOGICA SEGUN LA ACCION --> main

if accion == "create":
    servidores = 2  # Valor por defecto
    if len(sys.argv) == 3:
        try:
            servidores = int(sys.argv[2])
            if not (1 <= servidores <= 5):
                logging.error("El número de servidores debe estar entre 1 y 5.")
                print("El número de servidores debe estar entre 1 y 5.")
                sys.exit(1)
        except ValueError:
            logging.error("El número de servidores debe ser un entero.")
            sys.exit(1)
    crear_escenario(servidores)

if accion == "create_contenedor":
    crear_contenedor()

if accion == "start":
    start()
    time.sleep(3)
    subprocess.run(["lxc", "list"])

if accion == "stop":
    stop()

if accion == "list":
    list()

if accion == "delete":
    delete()

if accion == "help":
    mostrar_ayuda()

# PRACTICA 2

if accion == "instalar_node":
    instalar_app_en_servidores()

if accion == "configure_basic":
    servidores = 2  # Valor por defecto
    if len(sys.argv) == 3:
        try:
            servidores = int(sys.argv[2])
            if not (1 <= servidores <= 5):
                logging.error("El número de servidores debe estar entre 1 y 5.")
                print("El número de servidores debe estar entre 1 y 5.")
                sys.exit(1)
        except ValueError:
            logging.error("El número de servidores debe ser un entero.")
            sys.exit(1)

    configurar_basedatos()
    # configurar_servidores(servidores)
    
    configurar_balanceador()
    configurar_haproxy(servidores)


if accion == "configure_local":
    configA()
    bridge_remoto()

if accion == "verIP":
    obtener_ipB()
    
if accion == "configure_remoto":
    conectarB()


# configure.py creo que para parte opcional...
# if accion == "configure":
#     if len(sys.argv) < 3:
#         print("Uso: python3 pfinal2.py configure <local|remoto> [ip_remota]")
#         print("Ejemplo local: python3 pfinal2.py configure local")
#         print("Ejemplo remoto: python3 pfinal2.py configure remoto 192.168.1.100")
#         sys.exit(1)
    
#     modo = sys.argv[2]
#     ip_remota = None
    
#     if modo == "remoto":
#         if len(sys.argv) < 4:
#             print("Debe especificar la IP remota")
#             sys.exit(1)
#         ip_remota = sys.argv[3]
    
#     try:
#         # Obtener número de servidores del archivo de configuración
#         with open(ARCHIVO_CONFIG, "r") as f:
#             num_servidores = len([line for line in f.readlines() if line.startswith("s")])
        
#         configurar_escenario(modo, ip_remota, num_servidores)
#         print("Configuración completada exitosamente")
#     except Exception as e:
#         print(f"Error durante la configuración: {str(e)}")
#         sys.exit(1)