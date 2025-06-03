import subprocess
import logging
import sys
import time
from funciones_utiles import existe_contenedor


def instalar_app_en_servidores():
    """
    Configurar N servidores con node.js y preparar la app web
    """
    # la app se instala solo en los servidores s1, s2, s3...
    with open("servidores.txt", "r") as f:
        lineas = f.readlines()
        # excluye de la lista los contenedores cl, db y lb
        servidores = [linea.strip() for linea in lineas if not linea.strip() in ("cl", "db", "lb")]

    """ esto es lo de usar una imagen del primer contenedor para instalar la app en el resto de servidores... es muy util porque tarda muchisimo pero no está probado """
    # # Verificar contenedores
    # if not existe_contenedor(servidores[0]):
    #     logging.error(f"El contenedor '{servidores[0]}' no existe. Ejecuta 'python3 pfinal1.py create'.")
    #     print(f"El contenedor '{servidores[0]}' no existe. Ejecuta 'python3 pfinal1.py create'.")
    #     return 

    # # Instalar app en el primer servidor
    # print(f"Instalando app en servidor {servidores[0]}...")
    # subprocess.run(["lxc", "file", "push", "install.sh", f"{servidores[0]}/root/install.sh"])
    # subprocess.run(["lxc", "exec", f"{servidores[0]}", "--", "chmod", "+x", "install.sh"])
    # subprocess.run(["lxc", "file", "push", "-r", "app.tar.gz", f"{servidores[0]}/root/"]) # copia app.tar.gz al directorio 'root' del servidor s1 porque tiene permisos  
    # subprocess.run(["lxc", "exec", servidores[0], "--", "tar", "oxvf", "/root/app.tar.gz"]) # descomprime TAR
    # subprocess.run(["lxc", "exec", servidores[0], "--", "/root/install.sh"])

    # # crear una imagen a partir del primer contenedor s1
    # subprocess.run(["lxc", "stop", servidores[0]])
    # subprocess.run(["lxc","publish",f"{servidores[0]}","--alias","imagenConApp"])
    # subprocess.run(["lxc", "start", servidores[0]])
    # time.sleep(3) 
    # subprocess.run(["lxc", "exec", servidores[0], "--", "forever", "start", "app/rest_server.js"]) 

    # # Crear los demás servidores a partir de la imagen
    # for s in servidores[1:]:
    #     print(f"Creando contenedor {s} desde imagenConApp...")
    #     subprocess.run(["lxc", "launch", "imagenConApp", s])
    #     subprocess.run(["lxc", "restart", s])
    #     time.sleep(3)
    #     subprocess.run(["lxc", "exec", s, "--", "forever", "start", "app/rest_server.js"])

    # instala la aplicacion web en cada servidor de la lista 'servidores'
    for s in servidores:

        # verifica si el contenedor existe
        if not existe_contenedor(s):
            logging.error(f"El contenedor '{s}' no existe. Ejecuta 'python3 pfinal1.py create'.")
            print(f"El contenedor '{s}' no existe. Ejecuta 'python3 pfinal1.py create'.")
            return 

        print(f"Instalando app en servidor {s}...")
        # sube al contenedor: el script de instalacion y la app 
        subprocess.run(["lxc", "file", "push", "install.sh", f"{s}/root/install.sh"])
        subprocess.run(["lxc", "exec", s, "--", "chmod", "+x", "install.sh"])
        subprocess.run(["lxc", "file", "push", "-r", "app.tar.gz", f"{s}/root/"])
        
        # descomprime y ejecuta la instalacion
        subprocess.run(["lxc", "exec", s, "--", "tar", "oxvf", "/root/app.tar.gz"])
        subprocess.run(["lxc", "exec", s, "--", "/root/install.sh"])

        # reinicia el contenedor para aplicar los cambios y lanzar la app
        subprocess.run(["lxc", "restart", s])
        time.sleep(3)
        subprocess.run(["lxc", "exec", s, "--", "forever", "start", "/root/app/rest_server.js"])


# abrir  http://134.3.0.servidor(11):8001 -> http://134.3.0.11:8001