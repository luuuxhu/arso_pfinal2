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