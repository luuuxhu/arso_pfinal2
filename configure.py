import subprocess
import logging
import sys
import time
from funciones_utiles import existe_contenedor, contar_servidores
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


# 1.
def configurar_basedatos():
    """
    Instalar y configurar mongoDB en el contenedor "db"
    """
    # si se verifica que el contenedor con la db existe, instala mongoDB y lo configura
    if existe_contenedor("db"):
        
        # instala mongoDB
        logging.info("Instalando MongoDB...")
        subprocess.run(["lxc", "exec", "db", "--", "apt", "update"])
        subprocess.run(["lxc", "exec", "db", "--", "apt", "install", "-y", "mongodb"])

        # configura MongoDB (bind IP y reinicia)
        logging.info("Configurando MongoDB...")
        # sed https://www.sysadmit.com/2015/07/linux-reemplazar-texto-en-archivos-con-sed.html para sustituir la linea, nano no es automático
        subprocess.run([
            "lxc", "exec", "db", "--", "sed", "-i",
            "s/bind_ip = 127.0.0.1/bind_ip = 127.0.0.1,134.3.0.20/",  # cambiar a la IP de la bd
            "/etc/mongodb.conf"
        ])
        subprocess.run(["lxc", "restart", "db"])

    # si no existe, lanza un error
    else: 
        logging.error("El contenedor db no existe. No se puede configurar.")


# 2. 
def configurar_balanceador():
    """
    Instalar HAProxy en el contenedor lb
    """
    print(f"Configurando balanceador lb...")
    # instala HAProxy para el balanceador lb
    subprocess.run(["lxc", "exec", "lb", "--", "apt", "update"])
    subprocess.run(["lxc", "exec", "lb", "--", "apt", "install", "-y", "haproxy"])


# 3.
def configurar_haproxy():
    """
    Configura HAProxy con backend dinamico segun el numero de servidores
    """
    # documento base para el HAProxy
    config_inicial="""
global
	log /dev/log	local0
	log /dev/log	local1 notice
	chroot /var/lib/haproxy
	stats socket /run/haproxy/admin.sock mode 660 level admin
	stats timeout 30s
	user haproxy
	group haproxy
	daemon

	# Default SSL material locations
	ca-base /etc/ssl/certs
	crt-base /etc/ssl/private

	# Default ciphers to use on SSL-enabled listening sockets.
	# For more information, see ciphers(1SSL). This list is from:
	#  https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
	ssl-default-bind-ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS
	ssl-default-bind-options no-sslv3

defaults
	log	global
	mode	http
	option	httplog
	option	dontlognull
	timeout connect 5000
	timeout client  50000
	timeout server  50000
	errorfile 400 /etc/haproxy/errors/400.http
	errorfile 403 /etc/haproxy/errors/403.http
	errorfile 408 /etc/haproxy/errors/408.http
	errorfile 500 /etc/haproxy/errors/500.http
	errorfile 502 /etc/haproxy/errors/502.http
	errorfile 503 /etc/haproxy/errors/503.http
	errorfile 504 /etc/haproxy/errors/504.http

    """
    # siempre va a empezar con esta configuracion
    with open("haproxy.cfg", "w") as h:
        h.write(config_inicial)

    # CONFIGURACION DEL frontend Y DEL backend QUE CAMBIA DINAMICAMENTE
    
    num_servidores = int(contar_servidores())
    # lineas a incluir por cada servidor creado
    servidores_config = "\n".join([
        f"    server s{i} 134.3.0.1{i}:8001 check"
        for i in range(1, num_servidores + 1)
    ])

    # configuración completa para incluir a continuacion de la configuracion inicial
    nueva_config = f"""
frontend firstbalance
    bind *:80
    option forwardfor
    default_backend webservers

backend webservers
    balance roundrobin
    option httpchk GET /patients
{servidores_config}
"""
    # guarda el archivo HAProxy temporal local
    with open("haproxy.cfg", "a") as f:
        f.write(nueva_config)

    # y lo copia al contenedor lb
    subprocess.run(["lxc", "file", "push", "haproxy.cfg", "lb/etc/haproxy/haproxy.cfg"])

    # reinicia HAProxy dentro del contenedor lb
    subprocess.run(["lxc", "restart", "lb"])

    print("HAProxy configurado y reiniciado con éxito.") # esto salta aunque no haya sido con exito pero bueno...

    
    



