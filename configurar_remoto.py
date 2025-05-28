import subprocess
import logging
import sys
import time
import re
import socket


def obtener_ipB():
    subprocess.run(["ip", "addr", "show"])

    # Obtener IP local automáticamente (más fiable para redes locales)
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return str(local_ip)

def conectarB():
    # configurar lxd
    subprocess.run(["lxc", "config", "set", "core.https_address", f"{obtener_ipB()}:8443"])
    subprocess.run(["lxc", "config", "set", "core.trust_password", "mypass"])
    print(f"Configurado acceso remoto en {obtener_ipB()}:8443")



    







