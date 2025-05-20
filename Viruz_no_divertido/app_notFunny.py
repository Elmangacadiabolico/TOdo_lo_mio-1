#!/usr/bin/env python3

import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import platform
import random
import threading
import time
import os
import sys
import webbrowser
import ctypes
import subprocess
from pynput import keyboard as pynput_keyboard

# ---------------- UTILIDAD PARA CARGAR RECURSOS ----------------
def recurso_path(relative_path):
    """Obtiene la ruta absoluta para recursos, compatible con PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- CONFIGURACIÓN ----------------
CUSTOM_WALLPAPER_PATH = recurso_path("fondo_pantalla.png")
IMAGE_PATH_1 = recurso_path("furry.png")
IMAGE_PATH_2 = recurso_path("furry2.png")
MAX_WINDOWS = float('inf')
VELOCITY = 5
URL_INICIAL = "https://www.youtube.com/watch?v=xSjmkeOoSqs&ab_channel=CjEditz"

# ---------------- CAMBIAR FONDO ----------------
def set_wallpaper(image_path):
    system = platform.system()
    abs_path = os.path.abspath(image_path)

    if system == "Windows":
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        except Exception as e:
            print(f"Error cambiando fondo en Windows: {e}")
    elif system == "Linux":
        desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "")
        try:
            if "GNOME" in desktop_env:
                subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{abs_path}"
                ], check=True)
            else:
                print("Entorno de escritorio no compatible para cambiar fondo.")
        except Exception as e:
            print(f"Error cambiando fondo en Linux: {e}")
    else:
        print("Sistema no soportado para fondo de pantalla.")

# Aplicar fondo y abrir link
set_wallpaper(CUSTOM_WALLPAPER_PATH)
webbrowser.open(URL_INICIAL)

# ---------------- INICIALIZAR ----------------
root = tk.Tk()
root.withdraw()

img1 = Image.open(IMAGE_PATH_1).resize((100, 100))
photo1 = ImageTk.PhotoImage(img1)

img2 = Image.open(IMAGE_PATH_2).resize((100, 100))
photo2 = ImageTk.PhotoImage(img2)

windows = []
image_selector = 0

# ---------------- FUNCIONES ----------------
def create_window(x=None, y=None):
    global windows, image_selector

    if len(windows) >= MAX_WINDOWS:
        return

    win = tk.Toplevel()
    win.overrideredirect(True)
    win.attributes("-topmost", True)

    label = tk.Label(win, image=photo1 if image_selector == 0 else photo2, bd=0)
    image_selector = 1 - image_selector
    label.pack()

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    pos_x = x if x is not None else random.randint(0, screen_width - 100)
    pos_y = y if y is not None else random.randint(0, screen_height - 100)

    win.geometry(f"+{pos_x}+{pos_y}")

    dx = random.choice([-VELOCITY, VELOCITY])
    dy = random.choice([-VELOCITY, VELOCITY])

    def move():
        nonlocal pos_x, pos_y, dx, dy
        while True:
            try:
                pos_x += dx
                pos_y += dy
                if pos_x <= 0 or pos_x >= screen_width - 100:
                    dx = -dx
                if pos_y <= 0 or pos_y >= screen_height - 100:
                    dy = -dy
                win.geometry(f"+{pos_x}+{pos_y}")

                mouse_x, mouse_y = pyautogui.position()
                if abs(mouse_x - pos_x) < 100 and abs(mouse_y - pos_y) < 100:
                    create_window(pos_x, pos_y)

                time.sleep(0.03)
            except Exception as e:
                print(f"Error al mover ventana: {e}")
                break

    threading.Thread(target=move, daemon=True).start()
    windows.append(win)

def listen_hotkey():
    COMBO = {pynput_keyboard.KeyCode.from_char('p'), pynput_keyboard.KeyCode.from_char('s')}
    current_keys = set()

    def on_press(key):
        current_keys.add(key)
        if COMBO.issubset(current_keys):
            print("Hotkey P+S detectada. Cerrando.")
            root.quit()

    def on_release(key):
        if key in current_keys:
            current_keys.remove(key)

    with pynput_keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# ---------------- INICIO ----------------
create_window()
threading.Thread(target=listen_hotkey, daemon=True).start()
root.mainloop()
