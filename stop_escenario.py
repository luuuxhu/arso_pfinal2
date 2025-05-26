import subprocess
import logging
import time

ARCHIVO_CONFIG = "servidores.txt"
ARCHIVO_RUN = "contenedores_running.txt"

# parar todos los contenedores
def stop():

    with open(ARCHIVO_CONFIG, "r") as file:
        contenedores = [line.strip() for line in file.readlines()]

    while True:
        ans = input("Si desea parar todos los contenedores escriba TODOS.\n"
                    "Si desea parar un contenedor individual escriba el nombre: \n"
                    "Si desea salir escriba S \n").strip()
            
        # PARA PARAR TODOS
        if ans == "TODOS" or ans =="todos" or ans == "Todos":
            for c in contenedores:
                with open(ARCHIVO_RUN, "r") as file:
                    c_run = [line.strip() for line in file.readlines()]
                if not c in c_run:
                    print(f"el contenedor {c} ya esta parado")
                    
                else:
                    logging.info(f"Parando contenedor {c}...")
                    subprocess.Popen(["lxc", "stop", c])
                    c_run.remove(c)
                    with open(ARCHIVO_RUN, "w") as file:
                        file.write("\n".join(c_run))


        # PARA PARAR SOLO UN CONTENEDOR
        elif ans in contenedores:
            with open(ARCHIVO_RUN, "r") as file:
                c_run = [line.strip() for line in file.readlines()]
            
            if not ans in c_run:
                print(f"el contenedor {ans} ya esta parado")
            else:  
                logging.info(f"Parando contenedor {ans}...")
                subprocess.run(["lxc", "stop", ans])
                c_run.remove(ans)
                with open(ARCHIVO_RUN, "w") as file:
                    file.write("\n".join(c_run))


        elif ans == "s" or ans == "S":
            return

        else:
            print("Nombre no válido. Inténtelo de nuevo")