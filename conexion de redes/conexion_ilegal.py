import subprocess
import re
import os
import time

def listar_redes():
    print("Listando redes disponibles...\n")
    
    # Ejecuta el comando y captura la salida
    resultado = subprocess.run(["netsh", "wlan", "show", "networks", "mode=bssid"], capture_output=True, text=True, encoding='utf-8')

    # Busca los SSID en la salida
    redes = re.findall(r"SSID \d+ : (.+)", resultado.stdout)
    
    if not redes:
        print("No se encontraron redes disponibles.")
        return None
    
    # Muestra las redes numeradas
    for i, red in enumerate(redes, 1):
        print(f"{i}. {red.strip()}")
    
    return redes

def elegir_red(redes):
    while True:
        opcion = input(f"\nElige una red (1-{len(redes)} o '.' para volver a listar): ")
        if opcion == ".":
            return None
        if opcion.isdigit():
            opcion = int(opcion)
            if 1 <= opcion <= len(redes):
                return redes[opcion - 1].strip()
        print("Opción inválida, intenta nuevamente.")

def conectar_wifi(ssid, password):
    # Crear perfil XML
    xml_template = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <keyMaterial>{password}</keyMaterial>
            </authEncryption>
        </security>
    </MSM>
</WLANProfile>
"""
    # Guardar el archivo temporal
    with open("temp_profile.xml", "w", encoding="utf-8") as f:
        f.write(xml_template)

    # Agregar el perfil a Windows
    subprocess.run(["netsh", "wlan", "add", "profile", "filename=temp_profile.xml"], stdout=subprocess.DEVNULL)

    # Conectar a la red
    print(f"Intentando conectar a {ssid}...")
    subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], stdout=subprocess.DEVNULL)

    # Esperar 5 segundos
    time.sleep(5)

    # Verificar si está conectado
    resultado = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, encoding="utf-8")
    if "State" in resultado.stdout and "connected" in resultado.stdout:
        print(f"Conectado exitosamente a {ssid}.")
    else:
        print(f"No se pudo conectar a {ssid}.")

    # Eliminar el archivo XML temporal
    os.remove("temp_profile.xml")

def main():
    while True:
        redes = listar_redes()
        if not redes:
            break

        ssid = elegir_red(redes)
        if not ssid:
            continue

        password = input(f"Introduce la contraseña de {ssid}: ")
        conectar_wifi(ssid, password)
        break

if __name__ == "__main__":
    main()
