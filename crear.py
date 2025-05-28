import sys
import subprocess
import logging
import time
import funciones_utiles

# archivo donde vamos a guardar y leer la información del escenario
ARCHIVO_CONFIG = "servidores.txt"

# verifica si se han proporcionado los parámetros necesarios
if len(sys.argv) < 2:
    print("Uso: python3 pfinal1.py <create> [num_servidores]")
    sys.exit(1) 

# guardamos los logs en un archivo
logging.basicConfig(
    filename='logs.log',  # Archivo donde se guardarán los logs
    level=logging.DEBUG,     # Nivel de los mensajes a registrar
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del mensaje --> fecha nivel mensaje
    filemode='a'   # 'a' para añadir los nuevos logs al final del archivo (en vez de sobrescribir)
)

    
def crear_escenario(n):

    # importar imagen
    subprocess.run(["lxc","image","import","/mnt/vnx/repo/arso/ubuntu2004.tar.gz","--alias","ubuntu2004"])

    with open(ARCHIVO_CONFIG, "w") as file:
        for i in range(1, n + 1): # dentro del bucle for se crean n contenedores. Si no ponemos +1 carga hasta el 3 si ponemos '4'
            nombre = f"s{i}"
            if funciones_utiles.existe_contenedor(nombre):
                logging.info(f"El contenedor {nombre} ya existe. Saltando creación.")
            else:
                subprocess.run(["lxc", "init", "ubuntu:20.04", nombre])
                # Esto es para guardar si se creó con éxito...
                file.write(nombre + "\n")

        # Fuera del bucle se crean contendores como balanceador y cliente
        if funciones_utiles.existe_contenedor("lb"):
            logging.info("El balanceador lb ya existe. Saltando creación.")
        else:
            logging.info("Creando balanceador lb...")
            subprocess.run(["lxc", "init", "ubuntu:20.04", "lb"])
            file.write("lb\n")

        if funciones_utiles.existe_contenedor("cl"):
            logging.info("El contenedor cl ya existe. Saltando creación.")
        else:
            logging.info("Creando cliente cl...")
            subprocess.run(["lxc", "init", "ubuntu:20.04", "cl"])
            file.write("cl\n")

        # PRACTICA 2
        if funciones_utiles.existe_contenedor("db"):
            logging.info("El contenedor db ya existe. Saltando creación.")
        else:
            logging.info("Creando contenedor db...")
            subprocess.run(["lxc", "init", "ubuntu:20.04", "db"])
            file.write("db\n")

    # llama a la configuración de red, después de crear los contenedores
    configurar_redes(n)
    logging.info("Red configurada correctamente.")

    logging.info("Escenario creado correctamente.")
    print("Escenario creado correctamente.")

    time.sleep(3)
    subprocess.run(["lxc", "list"])


def crear_contenedor():
   # Verificar si se ha proporcionado un nombre de contenedor
    if len(sys.argv) != 3:
        print("Uso: python3 pfinal1.py create_contenedor <nombre_contenedor>")
        sys.exit(1)

    nombre_contenedor = sys.argv[2]

   # Verificar si el contenedor ya existe
    if funciones_utiles.existe_contenedor(nombre_contenedor):
        print(f"¡El contenedor con nombre '{nombre_contenedor}' ya existe!")
        logging.warning(f"Intento de crear contenedor existente: {nombre_contenedor}") # warning -> algo inesperado, no detiene la ejecución. Un nivel más alto que info
        sys.exit(1)
    
    else:
        # Crear el contenedor
        print(f"Creando el contenedor: {nombre_contenedor} ...")
        subprocess.run(["lxc", "init", "ubuntu:20.04", nombre_contenedor])
        logging.info("El contenedor se ha creado correctamente.")
        with open(ARCHIVO_CONFIG, "a") as file:
            file.write(f"\n{nombre_contenedor}")

''' configura la infraestructura de red para el escenario 
    n --> número de servidores '''
def configurar_redes(n: int):
    logging.info("Configurando red: creando bridges...")
    
    # creamos/comprobamos que ya existen los bridge, los configuramos
    if not funciones_utiles.existe_bridge("lxdbr1"):
        try:
            subprocess.run(["lxc", "network", "create", "lxdbr1", 
                            "ipv4.address=134.3.1.1/24", "ipv4.nat=false", 
                            "ipv6.address=none", "ipv6.nat=false",
                            "dns.domain=lxd", "dns.mode=none"])
            logging.info("Bridge lxdbr1 creado correctamente.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error al crear el bridge lxdbr1: {e}")
            return
    else:
        logging.info("El bridge lxdbr1 ya existe.")
        subprocess.run(["lxc", "network", "set", "lxdbr1", 
                        "ipv4.address=134.3.1.1/24", "ipv4.nat=false",
                        "ipv6.address=none", "ipv6.nat=false",
                        "dns.domain=lxd", "dns.mode=none"])

    # if not funciones_utiles.existe_bridge("lxdbr0"):
    #     try:
    #         subprocess.run(["lxc", "network", "create", "lxdbr0", 
    #                         "ipv4.address=134.3.0.1/24", "ipv4.nat=false", 
    #                         "ipv6.address=none", "ipv6.nat=false",
    #                         "dns.domain=lxd", "dns.mode=none"])
    #     except subprocess.CalledProcessError as e:
    #         logging.error(f"Error al crear el bridge lxdbr0: {e}")
    #         return
    # else:
        # logging.info("El bridge lxdbr0 ya existe.")
    subprocess.run(["lxc", "network", "set", "lxdbr0", 
                    "ipv4.address=134.3.0.1/24", "ipv4.nat=false",
                    "ipv6.address=none", "ipv6.nat=false",
                    "dns.domain=lxd", "dns.mode=none"])

    # configura la red para el cliente y el balanceador
    try:
        # Cliente
        logging.info("Configurando la red para el cliente...")
        subprocess.run(["lxc", "network", "attach", "lxdbr1", "cl", "eth0"])
        subprocess.run(["lxc", "config", "device", "set", "cl", "eth0", "ipv4.address", "134.3.1.2"])

        # Balanceador: conectado a dos interfaces --> eth1 y eth0
        logging.info("Configurando la red para el balanceador...")
        subprocess.run(["lxc", "network", "attach", "lxdbr1", "lb", "eth0"])
        subprocess.run(["lxc", "config", "device", "set", "lb", "eth0", "ipv4.address", "134.3.1.10"])

        subprocess.run(["lxc", "network", "attach", "lxdbr0", "lb", "eth1"])
        subprocess.run(["lxc", "config", "device", "set", "lb", "eth1", "ipv4.address", "134.3.0.10"])
    
        # P2: Base de datos: que se configure con direccion IP
        logging.info("Configurando la red para la base de datos...")
        subprocess.run(["lxc", "network", "attach", "lxdbr0", "db", "eth0"])
        subprocess.run(["lxc", "config", "device", "set", "db", "eth0", "ipv4.address", "134.3.0.20"])

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al configurar las interfaces de red: {e}")
        return


    # Servidores
    try:
        for i in range(1, n + 1):
            nombre = f"s{i}"
            ip = f"134.3.0.1{i}"
            logging.info(f"Configurando la red para el servidor {nombre} con la IP {ip}...")
            subprocess.run(["lxc", "network", "attach", "lxdbr0", nombre, "eth0"])
            subprocess.run(["lxc", "config", "device", "set", nombre, "eth0", "ipv4.address", ip])
        logging.info("Red configurada correctamente para todos los servidores.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al configurar las interfaces de los servidores: {e}")
        return
