import ctypes
import json
import os
import sys
import threading
import time
import winreg

import tkinter as tk
from tkinter import filedialog

# ==============================================================================
# CONFIGURACIÓN DE LOGS Y LOGICA DE RUTAS
# ==============================================================================
LOG_CONFIG = {
    "TRIGGERS": {
        "START":   'area "Sanctum_1_Foyer',
        "FLOOR_2": 'area "Sanctum_2_Foyer',
        "FLOOR_3": 'area "Sanctum_3_Foyer',
        "FLOOR_4": 'area "Sanctum_4_Foyer',
        "END":     'Zarokh, the Temporal: Ugh...'
    }
}

CONFIG_FILE = "zarokh_config.json"

def cargar_config_app():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def guardar_config_app(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

def obtener_ruta_log():
    config = cargar_config_app()

    # Capa 1: Ver si ya está guardada en la configuración propia
    if "client_txt_path" in config and os.path.exists(config["client_txt_path"]):
        return config["client_txt_path"]

    # Capa 2: Rutas por defecto comunes
    rutas_defecto = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile 2\logs\Client.txt",
        r"C:\Program Files (x86)\Grinding Gear Games\Path of Exile 2\logs\Client.txt"
    ]
    for ruta in rutas_defecto:
        if os.path.exists(ruta):
            config["client_txt_path"] = ruta
            guardar_config_app(config)
            return ruta

    # Capa 3: Registro de Windows (Standalone)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Grinding Gear Games\Path of Exile 2") as key:
            install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
            ruta_registro = os.path.join(install_path, "logs", "Client.txt")
            if os.path.exists(ruta_registro):
                config["client_txt_path"] = ruta_registro
                guardar_config_app(config)
                return ruta_registro
    except:
        pass

    return None


class CronometroOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Zarokh - PoE2 Tracker")

        # Set executable icon
        if getattr(sys, 'frozen', False):
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("zarokh.tracker.v2")
                icon_img = tk.PhotoImage(file=sys.executable)
                self.root.iconphoto(True, icon_img)
            except:
                pass

        # Ventana flotante siempre arriba y sin bordes
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        # Dimensiones de la interfaz
        self.ancho = 240
        self.alto_compacto = 135
        self.alto_expandido = 305
        self.root.geometry(f"{self.ancho}x{self.alto_compacto}+100+100")
        self.root.configure(bg="#1a1a1a")

        self.forzar_icono_barra_tareas()

        # Fichero independiente para guardar récords de tiempo
        self.records_file = "zarokh_records.json"
        self.records = self.cargar_records()

        # Intentar obtener la ruta del Client.txt mediante configuración o auto-detección
        self.client_txt_path = obtener_ruta_log()

        # Control del estado del cronómetro
        self.running = False
        self.panel_expandido = False
        self.tiempo_inicio = 0.0
        self.tiempo_acumulado = 0.0
        self.current_floor = 1
        self.tiempos_pisos = []

        # --- INTERFAZ VISUAL ---
        self.btn_cerrar = tk.Button(root, text="X", command=root.destroy, bg="#1a1a1a", fg="#555555", relief="flat", font=("Arial", 8, "bold"))
        self.btn_cerrar.place(x=222, y=2)

        self.label_tiempo = tk.Label(root, text="00:00.00", font=("Consolas", 26, "bold"), fg="#e5c17b", bg="#1a1a1a")
        self.label_tiempo.pack(pady=(8, 0))

        self.label_delta_live = tk.Label(root, text="Waiting for Sekhemas...", font=("Consolas", 10), fg="#888888", bg="#1a1a1a")
        self.label_delta_live.pack(pady=(0, 2))

        # Indicador de Modo en la pantalla principal (Pasa a verde si está en auto, interactivo si es manual)
        self.btn_modo_status = tk.Button(
            root, text="", command=self.activar_modo_auto_manual,
            relief="flat", font=("Arial", 7, "bold"), bd=0, cursor="hand2"
        )
        self.btn_modo_status.pack(pady=(0, 5))

        frame_botones = tk.Frame(root, bg="#1a1a1a")
        frame_botones.pack(pady=2)

        self.btn_toggle = tk.Button(frame_botones, text="Start", command=self.toggle_cronometro, bg="#2a2a2a", fg="white", relief="flat", width=6)
        self.btn_toggle.pack(side=tk.LEFT, padx=2)

        self.btn_floor = tk.Button(frame_botones, text="Floor", command=self.registrar_piso, bg="#2a2a2a", fg="white", relief="flat", width=6, state=tk.DISABLED)
        self.btn_floor.pack(side=tk.LEFT, padx=2)

        self.btn_reset = tk.Button(frame_botones, text="Reset", command=self.reset, bg="#2a2a2a", fg="white", relief="flat", width=6)
        self.btn_reset.pack(side=tk.LEFT, padx=2)

        self.btn_panel = tk.Button(frame_botones, text="+", command=self.toggle_panel, bg="#333333", fg="#e5c17b", relief="flat", width=2, font=("Arial", 9, "bold"))
        self.btn_panel.pack(side=tk.LEFT, padx=2)

        # --- PANEL DESPLEGABLE (RÉCORDS) ---
        self.frame_floors = tk.Frame(root, bg="#111111")
        
        self.labels_pisos = []
        for i in range(4):
            f = tk.Frame(self.frame_floors, bg="#111111")
            f.pack(fill=tk.X, padx=15, pady=2)
            lbl_name = tk.Label(f, text=f"Floor {i+1} Best:", font=("Consolas", 10), fg="#777777", bg="#111111", anchor="w")
            lbl_name.pack(side=tk.LEFT)
            lbl_val = tk.Label(f, text="--:--.--", font=("Consolas", 10), fg="#bbbbbb", bg="#111111", anchor="e")
            lbl_val.pack(side=tk.RIGHT)
            self.labels_pisos.append(lbl_val)
            
        f_total = tk.Frame(self.frame_floors, bg="#111111")
        f_total.pack(fill=tk.X, padx=15, pady=(5, 2))
        lbl_t_name = tk.Label(f_total, text="PB Total Time:", font=("Consolas", 10, "bold"), fg="#888888", bg="#111111", anchor="w")
        lbl_t_name.pack(side=tk.LEFT)
        self.lbl_total_val = tk.Label(f_total, text="--:--.--", font=("Consolas", 10, "bold"), fg="#e5c17b", bg="#111111", anchor="e")
        self.lbl_total_val.pack(side=tk.RIGHT)

        self.btn_clear_records = tk.Button(self.frame_floors, text="Clear Records", command=self.borrar_records, bg="#3a1a1a", fg="#f87171", relief="flat", font=("Arial", 9, "bold"), activebackground="#5a2a2a", activeforeground="white")
        self.btn_clear_records.pack(fill=tk.X, padx=15, pady=(10, 5))

        self.actualizar_interfaz_records()
        self.actualizar_indicador_pantalla_principal()

        # Eventos para poder arrastrar la ventana sin bordes
        for widget in [root, self.label_tiempo, self.label_delta_live]:
            widget.bind("<ButtonPress-1>", self.iniciar_movimiento)
            widget.bind("<B1-Motion>", self.mover_ventana)
        root.bind("<Escape>", lambda e: root.destroy())

        # --- INICIALIZACIÓN DEL HILO (Solo si existe el fichero) ---
        self.stop_log_trigger = threading.Event()
        if self.client_txt_path:
            self.iniciar_hilo_lectura()

    def iniciar_hilo_lectura(self):
        self.log_thread = threading.Thread(target=self.escuchar_client_log, daemon=True)
        self.log_thread.start()

    def escuchar_client_log(self):
        ruta_log = self.client_txt_path
        
        with open(ruta_log, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)
            
            while not self.stop_log_trigger.is_set():
                linea = f.readline()
                if not linea:
                    time.sleep(0.1)
                    continue
                
                triggers = LOG_CONFIG["TRIGGERS"]
                if triggers["START"] in linea:
                    self.root.after(0, self.auto_start)
                elif triggers["FLOOR_2"] in linea and self.current_floor == 1:
                    self.root.after(0, self.registrar_piso)
                elif triggers["FLOOR_3"] in linea and self.current_floor == 2:
                    self.root.after(0, self.registrar_piso)
                elif triggers["FLOOR_4"] in linea and self.current_floor == 3:
                    self.root.after(0, self.registrar_piso)
                elif triggers["END"] in linea and self.current_floor == 4:
                    self.root.after(0, self.registrar_piso)

    def auto_start(self):
        if not self.running:
            self.reset()
            self.tiempo_inicio = time.time()
            self.running = True
            self.btn_toggle.config(text="Pause")
            self.btn_floor.config(state=tk.NORMAL)
            self.actualizar_reloj()

    def actualizar_indicador_pantalla_principal(self):
        if self.client_txt_path:
            self.btn_modo_status.config(
                text="● AUTO MODE", fg="#4ade80", bg="#1a1a1a", 
                activebackground="#1a1a1a", activeforeground="#4ade80", state=tk.DISABLED
            )
        else:
            self.btn_modo_status.config(
                text="○ MANUAL MODE (Click to link PoE2)", fg="#a3a3a3", bg="#1a1a1a",
                activebackground="#1a1a1a", activeforeground="white", state=tk.NORMAL
            )

    def activar_modo_auto_manual(self):
        archivo_seleccionado = filedialog.askopenfilename(
            title="Zarokh: Select your Client.txt to enable Auto Mode",
            filetypes=[("Text Files", "Client.txt"), ("All Files", "*.*")]
        )
        if archivo_seleccionado and os.path.exists(archivo_seleccionado):
            self.client_txt_path = archivo_seleccionado
            
            config = cargar_config_app()
            config["client_txt_path"] = archivo_seleccionado
            guardar_config_app(config)
            
            self.actualizar_indicador_pantalla_principal()
            self.iniciar_hilo_lectura()

    def cargar_records(self):
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, "r") as f: return json.load(f)
            except: pass
        return {"floors": [None, None, None, None], "total": None}

    def guardar_records(self):
        with open(self.records_file, "w") as f: json.dump(self.records, f, indent=4)

    def borrar_records(self):
        self.records = {"floors": [None, None, None, None], "total": None}
        self.guardar_records()
        self.reset()

    def actualizar_interfaz_records(self):
        for i in range(4):
            rec = self.records["floors"][i]
            self.labels_pisos[i].config(text=self.formatear_tiempo(rec) if rec else "--:--.--")
        tot = self.records["total"]
        self.lbl_total_val.config(text=self.formatear_tiempo(tot) if tot else "--:--.--")
        self.actualizar_label_live()

    def actualizar_label_live(self):
        if self.current_floor <= 4:
            rec = self.records["floors"][self.current_floor - 1]
            best_txt = self.formatear_tiempo(rec) if rec else "First Run"
            self.label_delta_live.config(text=f"Floor {self.current_floor} | Best: {best_txt}", fg="#888888")
        else:
            self.label_delta_live.config(text="Run Completed!", fg="#e5c17b")

    def formatear_tiempo(self, segs):
        return f"{int(segs//60):02d}:{int(segs%60):02d}.{int((segs%1)*100):02d}"

    def toggle_panel(self):
        if self.panel_expandido:
            self.frame_floors.pack_forget()
            self.root.geometry(f"{self.ancho}x{self.alto_compacto}")
            self.btn_panel.config(text="+")
            self.panel_expandido = False
        else:
            self.frame_floors.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
            self.root.geometry(f"{self.ancho}x{self.alto_expandido}")
            self.btn_panel.config(text="-")
            self.panel_expandido = True

    def actualizar_reloj(self):
        if self.running:
            actual = self.tiempo_acumulado + (time.time() - self.tiempo_inicio)
            self.label_tiempo.config(text=self.formatear_tiempo(actual))
            
            if self.current_floor <= 4:
                record_piso = self.records["floors"][self.current_floor - 1]
                if record_piso:
                    tiempo_anterior = self.tiempos_pisos[self.current_floor - 2] if self.current_floor > 1 else 0
                    delta = (actual - tiempo_anterior) - record_piso
                    signo = "-" if delta < 0 else "+"
                    color = "#4ade80" if delta < 0 else "#f87171"
                    self.label_tiempo.config(fg=color)
                    self.label_delta_live.config(text=f"Floor {self.current_floor} | {signo}{abs(delta):.1f}s", fg=color)
            self.root.after(50, self.actualizar_reloj)

    def toggle_cronometro(self):
        if self.running:
            self.running = False
            self.tiempo_acumulado += time.time() - self.tiempo_inicio
            self.btn_toggle.config(text="Start")
            self.btn_floor.config(state=tk.DISABLED)
        else:
            self.tiempo_inicio = time.time()
            self.running = True
            self.btn_toggle.config(text="Pause")
            if self.current_floor <= 4: self.btn_floor.config(state=tk.NORMAL)
            self.actualizar_reloj()

    def registrar_piso(self):
        if not self.running or self.current_floor > 4: return

        tiempo_actual = self.tiempo_acumulado + (time.time() - self.tiempo_inicio)
        self.tiempos_pisos.append(tiempo_actual)
        
        tiempo_anterior = self.tiempos_pisos[self.current_floor - 2] if self.current_floor > 1 else 0
        tiempo_del_piso = tiempo_actual - tiempo_anterior
        record_piso = self.records["floors"][self.current_floor - 1]
        
        if record_piso is None or tiempo_del_piso < record_piso:
            self.records["floors"][self.current_floor - 1] = tiempo_del_piso

        self.current_floor += 1
        self.label_tiempo.config(fg="#e5c17b")
        self.actualizar_label_live()
        self.actualizar_interfaz_records()

        if self.current_floor > 4:
            self.btn_floor.config(state=tk.DISABLED)
            self.finalizar_run(tiempo_actual)

    def finalizar_run(self, tiempo_total):
        self.running = False
        self.btn_toggle.config(text="Start")
        record_total = self.records["total"]
        if record_total is None or tiempo_total < record_total:
            self.records["total"] = tiempo_total
        self.guardar_records()
        self.actualizar_interfaz_records()

    def reset(self):
        if self.current_floor > 4: self.guardar_records()
        self.running = False
        self.tiempo_acumulado = 0.0
        self.current_floor = 1
        self.tiempos_pisos = []
        self.label_tiempo.config(text="00:00.00", fg="#e5c17b")
        self.btn_toggle.config(text="Start")
        self.btn_floor.config(state=tk.DISABLED)
        self.actualizar_interfaz_records()

    def iniciar_movimiento(self, event):
        self.x = event.x
        self.y = event.y

    def mover_ventana(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def forzar_icono_barra_tareas(self):
        """Aplica estilos nativos de Windows para mostrar la ventana en la barra de tareas."""
        self.root.update_idletasks()
        
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20) # -20 es GWL_EXSTYLE
        
        # Modificamos los estilos de bits nativos
        style = style & ~0x00000080  # Quita WS_EX_TOOLWINDOW
        style = style | 0x00000040   # Añade WS_EX_APPWINDOW
        
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        
        # Refrescar la ventana para que Windows entienda el cambio de estilo
        self.root.wm_withdraw()
        self.root.after(10, self.root.wm_deiconify)


if __name__ == "__main__":
    root = tk.Tk()
    app = CronometroOverlay(root)
    root.mainloop()