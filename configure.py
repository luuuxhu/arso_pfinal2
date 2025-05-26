import subprocess
import logging
import sys
import time
import funciones_utiles

def configurar_servidores(n):

    # Configuración de logging
    logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)
    """
    Configura los servidores s1..sn con Node.js y la aplicación web
    """
    logging.info("Configurando escenario completo...")
    
    # Lista de servidores para recorrer 
    with open("servidores.txt", "r") as f:
    servidores = [line.strip() for line in f.readlines() if line.startswith("s")]

    # Verificar contenedores
    for contenedor in ["db", "lb"] + servidores:
        if not existe_contenedor(contenedor):
            logging.error(f"El contenedor '{contenedor}' no existe. Ejecuta 'python3 pfinal1.py create'.")
            return 


    # Configurar MongoDB (bind IP y reinicio)
    logging.info("Configurando MongoDB...")
    subprocess.run([
        "lxc", "exec", "db", "--", "sed", "-i",
        "s/bind_ip = 127.0.0.1/bind_ip = 127.0.0.1,134.3.0.20/",  # IP de db en la red según práctica 6.2
        "/etc/mongodb.conf"
    ])
    subprocess.run(["lxc", "exec", "db", "--", "systemctl", "restart", "mongodb"]) 


    # Instalar app en los servidores
    for servidor in servidores:
        print(f"Instalando app en servidor {servidor}...")
        subprocess.run(["lxc", "file", "push", "app.tar.gz", f"{servidor}/root/"]) # copia app.tar.gz al directorio 'root' del contenedor s1 porque tiene permisos  
        subprocess.run(["lxc", "exec", servidor, "--", "tar", "xzf", "/root/app.tar.gz", "-C", "/root/"])
        subprocess.run([
            "lxc", "exec", servidor, "--", "sed", "-i",
            "s/mongodb:\/\/localhost/mongodb:\/\/134.3.0.20/",  # IP de db
            "/root/app/rest_server.js"
        ])
        subprocess.run(["lxc", "exec", servidor, "--", "bash", "/root/install.sh"])


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
    
    if not funciones_utiles.existe_contenedor(nombre):
        logging.error(f"El contenedor {nombre} no existe. No se puede configurar.")
        return
    
    try:
        logging.info(f"Configurando base de datos MongoDB ({'local' if local else 'remota'})...")
        
        # Instalar MongoDB
        subprocess.run(["lxc", "exec", nombre, "--", "apt", "update"])
        subprocess.run(["lxc", "exec", nombre, "--", "apt", "install", "-y", "mongodb"])
        
        # Configurar MongoDB para aceptar conexiones remotas
        config_mongo = """
        storage:
          dbPath: /var/lib/mongodb
          journal:
            enabled: true
        
        systemLog:
          destination: file
          logAppend: true
          path: /var/log/mongodb/mongod.log
        
        net:
          port: 27017
          bindIp: 0.0.0.0
        """
        
        subprocess.run(["lxc", "exec", nombre, "--", "bash", "-c", f"echo '{config_mongo}' > /etc/mongod.conf"])
        
        # Reiniciar MongoDB
        subprocess.run(["lxc", "exec", nombre, "--", "systemctl", "restart", "mongodb"])
        
        # Configurar servicio
        setup_service(nombre, "mongodb")
        
        if not local:
            configurar_bd_remota(nombre, ip_remota)
        
        logging.info("Base de datos configurada correctamente")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al configurar la base de datos: {e}")