import subprocess
import logging
import sys
import time
from funciones_utiles import existe_contenedor


def instalar_app_en_servidores():
    # Lista de servidores para recorrer 
    with open("servidores.txt", "r") as f:
        servidores = [line.strip() for line in f.readlines()]

    # Verificar contenedores
    for contenedor in  servidores: # ["db", "lb"] + lo hemos eliminado. Habrá que añadirlos a servidores
        if not existe_contenedor(contenedor):
            logging.error(f"El contenedor '{contenedor}' no existe. Ejecuta 'python3 pfinal1.py create'.")
            print(f"El contenedor '{contenedor}' no existe. Ejecuta 'python3 pfinal1.py create'.")
            return 

        # Instalar app en los servidores
        for servidor in servidores:
            print(f"Instalando app en servidor {servidor}...")
            subprocess.run(["lxc", "file", "push", "-r", "app.tar.gz", f"{servidor}/root/"]) # copia app.tar.gz al directorio 'root' del contenedor s1 porque tiene permisos  
            subprocess.run(["lxc", "exec", servidor, "--", "tar", "oxvf", "/root/app.tar.gz"]) # descomprime TAR
            subprocess.run([
                "lxc", "exec", servidor, "--", "sed", "-i",
                "s/mongodb:\/\/localhost/mongodb:\/\/134.3.0.20/",  # IP de db
                "/root/app/rest_server.js"
            ])
            subprocess.run(["lxc", "exec", servidor, "--", "/root/install.sh"])
            subprocess.run(["lxc", "restart", servidor]) 
            subprocess.run(["lxc", "exec", servidor, "--", "forever", "start", "app/rest_server.js"]) 
            # abrir  http://134.3.0.servidor(11):8001 -> http://134.3.0.11:8001