import subprocess
import logging
import sys
import time
import re
import socket
from configurar_remoto import obtener_ipB



def configA():
    subprocess.run(["ip", "addr", "show"])

    # Obtener IP local automáticamente (más fiable para redes locales)
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)


    #SI LA AUTOMÁTICA NO FUNCIONA... a manita :)
    print(f"Detectada IP local: {local_ip}")
    print("¿Es correcta? (s/n)")
    if input().lower() != 's':
        print("Introduce la IP manualmente:")
        local_ip = input().strip()

    #validar formato ip
    ip_regex = r'^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'
    while not re.match(ip_regex, local_ip):
        print("IP no válida. Introdúcela de nuevo:")
        local_ip = input().strip()


    # configurar lxd
    subprocess.run(["lxc", "config", "set", "core.https_address", f"{local_ip}:8443"])
    subprocess.run([
    "lxc", "remote", "add", "remoto", f"{obtener_ipB()}:8443",
    "--password", "mypass", "--accept-certificate"
    ])
    print(f"Configurado acceso local en {local_ip}:8443")

    # copiar el contenedor ya configurado al equipo remoto
    subprocess.run(["lxc", "copy", "db", "remoto:db"])

    # Crear un proxy, para acceso remoto a las base de datos de manera remota
    subprocess.run([
    "lxc", "config", "device", "add", "remoto:db", "miproxy", "proxy",
    f"listen=tcp:{obtener_ipB()}:27017", "connect=tcp:134.3.0.20:27017"
    ])



def bridge_remoto():
    subprocess.run(["lxc", "network", "set", "remoto:lxdbr0", "ipv4.address", "134.3.0.1/24"])
    subprocess.run(["lxc", "network", "set", "remoto:lxdbr0", "ipv4.nat", "true"])

    
    
