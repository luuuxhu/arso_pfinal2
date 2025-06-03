import subprocess
import logging
import sys


def modificar_yaml():
    """
    Configura las interfaces de red del balanceador lb
    """
    # Asegura que el contenedor esté iniciado
    subprocess.run(["lxc", "start", "lb"])

    # Modifica el archivo de configuración de red
    with open("50-cloud-init.yaml", "w") as f:
        f.write("""
# This file is generated from information provided by the datasource.  Changes
# to it will not persist across an instance reboot.  To disable cloud-init's
# network configuration capabilities, write a file
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# network: {config: disabled}
network:
    version: 2
    ethernets:
        eth0:
            dhcp4: true
        eth1:
            dhcp4: true
""")

    # sube el archivo y aplica la configuración
    subprocess.run(["lxc", "file", "push", "50-cloud-init.yaml", "lb/etc/netplan/50-cloud-init.yaml"])
    subprocess.run(["lxc", "exec", "lb", "--", "netplan", "apply"])
    subprocess.run(["lxc", "stop", "lb"])

    print("Red del balanceador configurada.")
