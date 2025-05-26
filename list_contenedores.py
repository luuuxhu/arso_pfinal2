import subprocess

ARCHIVO_CONFIG = "servidores.txt"
def list():

    subprocess.run(["lxc", "list"])

   # PARA INFO EXTRA 
    with open(ARCHIVO_CONFIG, "r") as file:
        contenedores = [line.strip() for line in file.readlines()]

    while True:
        ans = input("Si desea más información de algún contenedor, escriba el nombre del contenedor." 
                    "Si no escriba N: \n").strip()
        
        if ans == "N" or ans =="n":
            break
        elif ans in contenedores:
                subprocess.run(["lxc", "config", "show", ans])
        else:
             print("Nombre no válido. Inténtelo de nuevo")
