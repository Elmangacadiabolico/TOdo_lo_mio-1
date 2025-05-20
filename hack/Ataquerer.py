import platform
import getpass
import socket
import subprocess
import time
import json
import requests
import threading

stop_flag = False

def get_wifi_ssid():
    try:
        output = subprocess.check_output(
            "netsh wlan show interfaces",
            shell=True,
            encoding="cp850",
            errors="ignore"
        )
        ssid = "Desconocido"
        signal = "Desconocido"
        for line in output.split("\n"):
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":", 1)[1].strip()
            if "Señal" in line or "Signal" in line:
                signal = line.split(":", 1)[1].strip()
        return ssid, signal
    except Exception as e:
        return f"Error al obtener SSID: {e}", "N/A"

def get_wifi_bssid():
    try:
        output = subprocess.check_output(
            "netsh wlan show interfaces",
            shell=True,
            encoding="cp850",
            errors="ignore"
        )
        for line in output.split("\n"):
            if "BSSID" in line:
                return line.split(":", 1)[1].strip()
        return "No detectado"
    except Exception as e:
        return f"Error: {e}"

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No detectada"

def get_location_from_mozilla(bssid):
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {
            "wifiAccessPoints": [
                {"macAddress": bssid}
            ]
        }
        response = requests.post(
            "https://location.services.mozilla.com/v1/geolocate?key=test",
            headers=headers,
            json=payload,
            timeout=5
        )
        
        # Verificar si la respuesta es válida
        if response.status_code == 200 and response.json():
            data = response.json()
            lat = data.get("location", {}).get("lat", "No disponible")
            lng = data.get("location", {}).get("lng", "No disponible")
            accuracy = data.get("accuracy", "N/A")
            
            return {
                "coordenadas": f"{lat},{lng}",
                "precision_metros": accuracy
            }
        else:
            return {
                "coordenadas": "No disponibles",
                "error": "No se pudo obtener ubicación precisa del BSSID"
            }
    except Exception as e:
        return {
            "coordenadas": "No disponibles",
            "error": str(e)
        }



def get_public_ip_and_location():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        return {
            "ip_publica": data.get("query", "No detectada"),
            "ciudad": data.get("city", "Desconocida"),
            "region": data.get("regionName", "Desconocida"),
            "pais": data.get("country", "Desconocido"),
            "org": data.get("isp", "Desconocida"),
            "loc": f"{data.get('lat', 'N/A')},{data.get('lon', 'N/A')}"
        }
    except Exception as e:
        return {
            "ip_publica": "Error",
            "error": str(e)
        }

def get_system_info():
    ssid, signal = get_wifi_ssid()
    bssid = get_wifi_bssid()
    ubicacion_precisa = get_location_from_mozilla(bssid)
    ubicacion_ip = get_public_ip_and_location()
    info = {
        "timestamp": time.ctime(),
        "username": getpass.getuser(),
        "os": platform.system() + " " + platform.release(),
        "hostname": socket.gethostname(),
        "ip_privada": get_private_ip(),
        "wifi_ssid": ssid,
        "wifi_bssid": bssid,
        "wifi_signal": signal,
        "ip_publica": ubicacion_ip.get("ip_publica"),
        "ubicacion_aproximada_por_ip": {
            "ciudad": ubicacion_ip.get("ciudad"),
            "region": ubicacion_ip.get("region"),
            "pais": ubicacion_ip.get("pais"),
            "coordenadas": ubicacion_ip.get("loc"),
            "proveedor": ubicacion_ip.get("org")
        },
        "ubicacion_precisa_por_bssid": ubicacion_precisa
    }
    return info

def save_info_loop():
    while not stop_flag:
        info = get_system_info()
        with open("system_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
        print(f"[{time.ctime()}] Datos actualizados.")
        time.sleep(20)

def start_monitoring():
    global stop_flag
    stop_flag = False
    thread = threading.Thread(target=save_info_loop)
    thread.start()
    return thread

# Interfaz de control simple
if __name__ == "__main__":
    print("📡 Monitor de información del sistema y red")
    thread = start_monitoring()
    while True:
        print("\n--- Menú ---")
        print("[1] Mostrar contenido actual del JSON")
        print("[2] Salir")
        choice = input("Elige una opción: ").strip()
        if choice == "1":
            try:
                with open("system_info.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(json.dumps(data, indent=4, ensure_ascii=False))
            except Exception as e:
                print(f"Error al leer el archivo: {e}")
        elif choice == "2":
            print("Deteniendo monitoreo...")
            stop_flag = True
            thread.join()
            print("Proceso finalizado.")
            break
        else:
            print("Opción inválida.")
