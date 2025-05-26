import subprocess
import logging
import sys
import time
from funciones_utiles import existe_contenedor

# Configuración de logging
logging.basicConfig(
filename='logs.log',
level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(message)s',
filemode='a'
)

# Constantes
ARCHIVO_CONFIG = "servidores.txt"
INSTALL_SCRIPT = "install.sh"

def configurar_servidores(n): # node.js
    """
    Configura los servidores s1..sn con Node.js y la aplicación web
    """

    
## ESTO YA LO HA HECHO CHAT Y HAY QUE REVISAR
    # Configurar base de datos en contenedor db 
    print(f"Configurando base de datos en MongoDB...")
    subprocess.run(["lxc", "file", "push", "install.sh", "db/root/"])
    subprocess.run(["lxc", "exec", "db", "--", "bash", "/root/install.sh"])


# LO DEL HAPROXY HAY QUE VERLO, PORQUE CREO QUE HAY QUE EDITAR EL ARCHIVO Y SUPONGO QUE SE PUEDE HACER MANUALMENTE O DESDE COMANDOS.

    # Configurar balanceador (con HAProxy)  
    print(f"Configurando balanceador lb..")
    subprocess.run(["lxc", "file", "push", "haproxy.cfg", "lb/etc/haproxy/haproxy.cfg"])
    subprocess.run(["lxc", "exec", "lb", "--", "systemctl", "restart", "haproxy"])   

    try:
        subprocess.run(["lxc", "exec", "db", "--", "systemctl", "restart", "mongodb"], check=True)
    except subprocess.CalledProcessError:
        logging.error("¡Error al reiniciar MongoDB!")


def configurar_basedatos(local=True, ip_remota=None):
    """
    Configura la base de datos MongoDB
    local: True para instalación local, False para remota
    ip_remota: IP del servidor remoto si es instalación remota
    """
    
    nombre = "db"

    if existe_contenedor(nombre):
        # Instalar MongoDB
        logging.info("Instalando MongoDB...")
        subprocess.run(["lxc", "exec", nombre, "--", "apt", "update"]) # si no funciona es SU CULPA
        subprocess.run(["lxc", "exec", nombre, "--", "apt", "install", "-y", "mongodb"])

        # Configurar MongoDB (bind IP y reinicio)
        logging.info("Configurando MongoDB...")

        # sed https://www.sysadmit.com/2015/07/linux-reemplazar-texto-en-archivos-con-sed.html para sustituir la linea, nano no es automático
        subprocess.run([
            "lxc", "exec", "db", "--", "sed", "-i",
            "s/bind_ip = 127.0.0.1/bind_ip = 127.0.0.1,134.3.0.20/",  # IP de db en la red según práctica 6.2
            "/etc/mongodb.conf"
        ])
        subprocess.run(["lxc", "restart", nombre]) 
    else: logging.error(f"El contenedor {nombre} no existe. No se puede configurar.")




    # PARA EL REMOTO, YA LO VEREMOS :D
    # try:
    #     logging.info(f"Configurando base de datos MongoDB ({'local' if local else 'remota'})...")

        
    #     # Configurar MongoDB para aceptar conexiones remotas
    #     config_mongo = """
    #     storage:
    #       dbPath: /var/lib/mongodb
    #       journal:
    #         enabled: true
        
    #     systemLog:
    #       destination: file
    #       logAppend: true
    #       path: /var/log/mongodb/mongod.log
        
    #     net:
    #       port: 27017
    #       bindIp: 0.0.0.0
    #     """
        
    #     subprocess.run(["lxc", "exec", nombre, "--", "bash", "-c", f"echo '{config_mongo}' > /etc/mongod.conf"])
        
    #     # Reiniciar MongoDB
    #     subprocess.run(["lxc", "exec", nombre, "--", "systemctl", "restart", "mongodb"])
        
    #     # Configurar servicio
    #     setup_service(nombre, "mongodb")
        
    #     if not local:
    #         configurar_bd_remota(nombre, ip_remota)
        
    #     logging.info("Base de datos configurada correctamente")
        
    # except subprocess.CalledProcessError as e:
    #     logging.error(f"Error al configurar la base de datos: {e}")