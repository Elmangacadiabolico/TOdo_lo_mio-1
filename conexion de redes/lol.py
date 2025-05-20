import subprocess
import xml.etree.ElementTree as ET
import os

def escanear_redes():
    print("🔍 Escaneando redes WiFi...\n")
    resultado = subprocess.run(["netsh", "wlan", "show", "networks", "mode=bssid"], capture_output=True, text=True, encoding='utf-8')
    redes = []
    for linea in resultado.stdout.splitlines():
        if "SSID" in linea and "BSSID" not in linea:
            ssid = linea.split(":", 1)[1].strip()
            if ssid and ssid not in [r[0] for r in redes]:
                redes.append((ssid,))
    return redes

def mostrar_redes(redes):
    print("📶 Redes disponibles:\n")
    for i, (ssid,) in enumerate(redes):
        print(f"{i + 1}. {ssid}")
    print()

def crear_perfil_xml(ssid, password, filename="perfil.xml"):
    profile = f"""<?xml version="1.0"?>
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
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(profile)
    return filename

def conectar_a_red(ssid, password=None):
    if password:
        perfil = crear_perfil_xml(ssid, password)
        resultado_add = subprocess.run(["netsh", "wlan", "add", "profile", f"filename={perfil}", "user=all"], capture_output=True, text=True)
        print("DEBUG perfil agregado:", resultado_add.stdout)
        os.remove(perfil)
    resultado = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True, text=True)
    if resultado.returncode == 0:
        print(f"✅ Conectado exitosamente a '{ssid}'")
    else:
        print(f"❌ Error al conectar a '{ssid}':")
        print("STDOUT:", resultado.stdout)
        print("STDERR:", resultado.stderr)


def main():
    redes = escanear_redes()
    if not redes:
        print("❌ No se encontraron redes.")
        return

    mostrar_redes(redes)

    try:
        opcion = int(input("🔢 Elegí una red por número: "))
        if opcion < 1 or opcion > len(redes):
            print("Número inválido.")
            return
        ssid = redes[opcion - 1][0]
        password = input(f"🔐 Ingresá la contraseña para '{ssid}' (dejar vacío si está guardada): ")
        if password.strip() == "":
            conectar_a_red(ssid)
        else:
            conectar_a_red(ssid, password.strip())
    except ValueError:
        print("❌ Entrada no válida.")

if __name__ == "__main__":
    main()