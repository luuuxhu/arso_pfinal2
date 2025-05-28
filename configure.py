import subprocess
import logging
import sys
import time
from funciones_utiles import existe_contenedor
from instalar_node_servidores import instalar_app_en_servidores


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


# 1. instalar y configurar mongoDB en el contenedor "db"
def configurar_basedatos():
    """
    Configura la base de datos MongoDB
    local: True para instalación local, False para remota
    ip_remota: IP del servidor remoto si es instalación remota
    """
    
    nombre = "db"

    if existe_contenedor(nombre):
        # Instalar MongoDB
        logging.info("Instalando MongoDB...")
        # subprocess.run(["lxc", "exec", nombre, "--", "apt", "update"]) # si no funciona es SU CULPA
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


# 2. Configurar N servidores con node.js y preparar la app web
def configurar_servidores(n): # node.js
    """
    Configura los servidores s1..sn con Node.js y la aplicación web
    """

    
    # Configurar base de datos en contenedor db 
    print(f"Configurando base de datos en MongoDB...")
    subprocess.run(["lxc", "file", "push", "install.sh", "db/root/"])
    subprocess.run(["lxc", "exec", "db", "--", "bash", "/root/install.sh"])

    try:
        subprocess.run(["lxc", "exec", "db", "restart", "mongodb"], check=True)
    except subprocess.CalledProcessError:
        logging.error("¡Error al reiniciar MongoDB!")

    instalar_app_en_servidores()

# 3. instalar HAProxy en el contenedor lb
def configurar_balanceador(): 

    # Configurar balanceador (con HAProxy)  
    print(f"Configurando balanceador lb..")
    subprocess.run(["lxc", "exec", "lb", "bash"])
    # Asegurar que HAProxy este instalado
    subprocess.run(["lxc", "exec", "lb", "--", "apt", "update"])
    subprocess.run(["lxc", "exec", "lb", "--", "apt", "install", "-y", "haproxy"])


# 4. configurar HAProxy con backend dinamico segun el numero de servidores
def configurar_haproxy(num_servidores):
    """Configura HAProxy dinámicamente según el número de servidores"""

    # 1. Generar configuración de servidores dinámicamente
    servidores_config = "\n".join([
        f"    server s{i} 134.3.0.1{i}:8001 check"
        for i in range(1, num_servidores + 1)
    ])

    # 2. Configuración completa a inyectar
    nueva_config = f"""
frontend http_front
    bind *:80
    default_backend nodejs_servers

backend nodejs_servers
    balance roundrobin
    {servidores_config}
    option httpchk
"""

    # 3. Modificar directamente el archivo en el contenedor
    subprocess.run([
        "lxc", "exec", "lb", "--", "sh", "-c",
        f"cat >> /etc/haproxy/haproxy.cfg << 'EOF'\n{nueva_config}\nEOF"
    ])

    # 4. Reiniciar HAProxy
    # subprocess.run(["lxc", "exec", "lb", "restart", "haproxy"])
    
    subprocess.run(["lxc", "exec", "lb", "service", "haproxy", "start"])




# esto siguiente no se de que serviria la verdad
    # subprocess.run(["lxc", "file", "push", "haproxy.cfg", "lb/etc/haproxy/haproxy.cfg"])
    # subprocess.run(["lxc", "exec", "lb", "--", "systemctl", "restart", "haproxy"])






    
    



