import subprocess
import socket

def obtener_redes_guardadas():
    """Obtiene los nombres de las redes WiFi guardadas en la PC"""
    comando = "netsh wlan show profile"
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    
    redes = []
    for linea in resultado.stdout.split("\n"):
        if "Perfil de todos los usuarios" in linea or "All User Profile" in linea:  # Soporta español e inglés
            red = linea.split(":")[1].strip()
            redes.append(red)
    
    return redes

def obtener_ip_actual():
    """Obtiene la IP de la red actual"""
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    return ip_local

def obtener_contraseña_wifi(red):
    """Obtiene la contraseña de una red almacenada en la PC"""
    comando = f'netsh wlan show profile name="{red}" key=clear'
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    for linea in resultado.stdout.split("\n"):
        if "Contenido de la clave" in linea or "Key Content" in linea:  # Soporta español e inglés
            return linea.split(":")[1].strip()
    
    return "No se encontró la contraseña"

if __name__ == "__main__":
    print("Redes WiFi guardadas en la PC:")
    redes = obtener_redes_guardadas()

    if redes:
        for red in redes:
            contraseña = obtener_contraseña_wifi(red)
            print(f"Red: {red} | Contraseña: {contraseña}")
    else:
        print("No se encontraron redes guardadas.")
    
    print("\nIP de la red actual:", obtener_ip_actual())
