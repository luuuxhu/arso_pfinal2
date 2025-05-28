import subprocess
import logging

ARCHIVO_CONFIG = "servidores.txt"
ARCHIVO_RUNNING = "contenedores_running.txt"


def delete():
    with open(ARCHIVO_CONFIG, "r") as file:
        contenedores = [line.strip() for line in file.readlines()]
    with open(ARCHIVO_RUNNING, "r") as file:
        c_run = [line.strip() for line in file.readlines()]

    while True:
        ans = input("Si desea borrar todos los contenedores y bridges escriba TODOS.\n" 
                    "Si desea borrar un contenedor o bridge individual escriba el nombre: \n"
                    "Si desea salir escriba S \n").strip()
        if ans == "TODOS" or ans =="todos" or ans == "Todos":
            for c in contenedores:
                print(f"Eliminando el contenedor {c}...")
                subprocess.run(["lxc", "delete", c, "--force"])
            subprocess.run(["lxc", "network", "delete", "lxdbr1"])
            print(f"Eliminando el bridge lxdbr1...")
            with open(ARCHIVO_CONFIG, "w") as file:
                file.write("")
            with open(ARCHIVO_RUNNING, "w") as file:
                file.write("")


        elif ans in contenedores:
            subprocess.run(["lxc", "delete", ans, "--force"])
            # eliminarlo de la lista contenedores (esta en memoria)
            contenedores.remove(ans)
            c_run.remove(ans)
            # eliminar del archivo servidores
            with open(ARCHIVO_CONFIG, "w") as file:
                file.write("\n".join(contenedores))
            # eliminar del archivo contenedores running
            with open(ARCHIVO_RUNNING, "w") as file:
                file.write("\n".join(c_run))
            subprocess.run(["lxc", "list"])
        
        elif ans == "lxdbr1":
            subprocess.run(["lxc", "network", "detach", ans, "cl"])
            subprocess.run(["lxc", "network", "detach", ans, "lb"])
            subprocess.run(["lxc", "network", "delete", ans])
            subprocess.run(["lxc", "network", "list"])

        
        elif ans == "s" or ans == "S":
            return

        else:
            print("Nombre no válido. Inténtelo de nuevo")
        

