import subprocess
import logging
import time
import os

ARCHIVO_CONFIG = "servidores.txt"
ARCHIVO_RUN = "contenedores_running.txt"

def start():
    if not os.path.exists(ARCHIVO_RUN):
        with open(ARCHIVO_RUN, "w") as file:
            pass 
    
    with open(ARCHIVO_CONFIG, "r") as file:
        contenedores = [line.strip() for line in file.readlines()]

    while True:
        ans = input("Si desea arrancar todos los contenedores escriba TODOS.\n" 
                    "Si desea arancar un contenedor individual escriba el nombre: \n"
                    "Si desea salir escriba S \n").strip()
        if ans == "TODOS" or ans =="todos" or ans == "Todos":
            for c in contenedores: # recorremos los contenedores
                with open(ARCHIVO_RUN, "r") as file: # leemos el archivo contenedores_running.txt
                    c_run = [line.strip() for line in file.readlines()]    # lista de los que esten running 
                if c in c_run: # si el contenedor esta en el archivo contenedores_running.txt
                    print(f"El contenedor {c} ya esta arrancado")
                else:
                    logging.info(f"Iniciando contenedor {c}...")
                    print(f"Iniciando contenedor {c}...")
                    subprocess.Popen(["lxc", "start", c])
                    subprocess.Popen(["xterm", "-e", "lxc exec " + c + " bash"])
                    time.sleep(2)
                    with open(ARCHIVO_RUN, "a") as file:
                        file.write(f"{c}\n")
            modificar_yaml() # habría que añadir control de errores a esto IMPORTANTE IMPORTANTE IMPORTANTE IMPORTANTE IMPORTANTE IMPORTANTEEEEEEE  PUES NO SALE


       # para iniciar SOLO UNO 
        elif ans in contenedores:
            with open(ARCHIVO_RUN, "r") as file:
                c_run = [line.strip() for line in file.readlines()]
            
            if ans in c_run:
                print(f"el contenedor {ans} ya esta arrancado")
            else:    
                logging.info(f"Iniciando contenedor {ans}...")
                subprocess.run(["lxc", "start", ans])
                time.sleep(2)
                subprocess.Popen(["xterm", "-e", "lxc exec " + ans + " bash"])

                with open(ARCHIVO_RUN, "a") as file:
                    file.write(f"{ans}\n")

                if ans == "lb":
                    modificar_yaml()


        elif ans == "s" or ans == "S":
            return

        else:
            print("Nombre no válido. Inténtelo de nuevo")
        

