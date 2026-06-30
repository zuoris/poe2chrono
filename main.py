import tkinter as tk
import time
import json
import os

class CronometroOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE2 Sekhemas Tracker")
        
        # Ventana flotante siempre arriba y sin bordes
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        # Dimensiones: empezamos en modo COMPACTO (alto 115)
        self.ancho = 240
        self.alto_compacto = 115
        self.alto_expandido = 255
        self.root.geometry(f"{self.ancho}x{self.alto_compacto}+100+100")
        self.root.configure(bg="#1a1a1a")

        # Fichero y carga de récords
        self.records_file = "sekhemas_records.json"
        self.records = self.cargar_records()

        # Control del estado
        self.running = False
        self.panel_expandido = False
        self.tiempo_inicio = 0.0
        self.tiempo_acumulado = 0.0
        self.current_floor = 1
        self.tiempos_pisos = []

        # --- INTERFAZ VISUAL ---
        
        # Botón cerrar (X)
        self.btn_cerrar = tk.Button(root, text="X", command=root.destroy, bg="#1a1a1a", fg="#555555", relief="flat", font=("Arial", 8, "bold"))
        self.btn_cerrar.place(x=222, y=2)

        # Cronómetro Principal
        self.label_tiempo = tk.Label(root, text="00:00.00", font=("Consolas", 26, "bold"), fg="#e5c17b", bg="#1a1a1a")
        self.label_tiempo.pack(pady=(8, 0))

        # Indicador de Delta en tiempo real (Comparación con el récord del piso actual)
        self.label_delta_live = tk.Label(root, text="Floor 1 | Best: --:--.--", font=("Consolas", 10), fg="#888888", bg="#1a1a1a")
        self.label_delta_live.pack(pady=(0, 5))

        # Fila de Botones Principales
        frame_botones = tk.Frame(root, bg="#1a1a1a")
        frame_botones.pack(pady=2)

        self.btn_toggle = tk.Button(frame_botones, text="Start", command=self.toggle_cronometro, bg="#2a2a2a", fg="white", relief="flat", width=6)
        self.btn_toggle.pack(side=tk.LEFT, padx=2)

        self.btn_floor = tk.Button(frame_botones, text="Floor", command=self.registrar_piso, bg="#2a2a2a", fg="white", relief="flat", width=6, state=tk.DISABLED)
        self.btn_floor.pack(side=tk.LEFT, padx=2)

        self.btn_reset = tk.Button(frame_botones, text="Reset", command=self.reset, bg="#2a2a2a", fg="white", relief="flat", width=6)
        self.btn_reset.pack(side=tk.LEFT, padx=2)

        # Botón para Desplegar/Ocultar info extra
        self.btn_panel = tk.Button(frame_botones, text="+", command=self.toggle_panel, bg="#333333", fg="#e5c17b", relief="flat", width=2, font=("Arial", 9, "bold"))
        self.btn_panel.pack(side=tk.LEFT, padx=2)

        # --- PANEL DESPLEGABLE (Oculto por defecto) ---
        self.frame_floors = tk.Frame(root, bg="#111111") # Fondo un poco más oscuro para contrastar
        
        # Filas de los récords históricos de cada piso
        self.labels_pisos = []
        for i in range(4):
            f = tk.Frame(self.frame_floors, bg="#111111")
            f.pack(fill=tk.X, padx=15, pady=2)
            
            lbl_name = tk.Label(f, text=f"Floor {i+1} Best:", font=("Consolas", 10), fg="#777777", bg="#111111", anchor="w")
            lbl_name.pack(side=tk.LEFT)
            
            lbl_val = tk.Label(f, text="--:--.--", font=("Consolas", 10), fg="#bbbbbb", bg="#111111", anchor="e")
            lbl_val.pack(side=tk.RIGHT)
            self.labels_pisos.append(lbl_val)
            
        # Fila del récord Total histórico en el panel
        f_total = tk.Frame(self.frame_floors, bg="#111111")
        f_total.pack(fill=tk.X, padx=15, pady=(5, 2))
        lbl_t_name = tk.Label(f_total, text="PB Total Time:", font=("Consolas", 10, "bold"), fg="#888888", bg="#111111", anchor="w")
        lbl_t_name.pack(side=tk.LEFT)
        self.lbl_total_val = tk.Label(f_total, text="--:--.--", font=("Consolas", 10, "bold"), fg="#e5c17b", bg="#111111", anchor="e")
        self.lbl_total_val.pack(side=tk.RIGHT)

        # Cargar los datos guardados en la interfaz visual
        self.actualizar_interfaz_records()

        # Eventos de arrastre
        for widget in [root, self.label_tiempo, self.label_delta_live]:
            widget.bind("<ButtonPress-1>", self.iniciar_movimiento)
            widget.bind("<B1-Motion>", self.mover_ventana)
        root.bind("<Escape>", lambda e: root.destroy())

    # --- Lógica de Récords (JSON) ---
    def cargar_records(self):
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, "r") as f: return json.load(f)
            except: pass
        return {"floors": [None, None, None, None], "total": None}

    def guardar_records(self):
        with open(self.records_file, "w") as f: json.dump(self.records, f, indent=4)

    def actualizar_interfaz_records(self):
        for i in range(4):
            rec = self.records["floors"][i]
            texto = self.formatear_tiempo(rec) if rec else "--:--.--"
            self.labels_pisos[i].config(text=texto)
        
        tot = self.records["total"]
        self.lbl_total_val.config(text=self.formatear_tiempo(tot) if tot else "--:--.--")
        self.actualizar_label_live()

    def actualizar_label_live(self):
        if self.current_floor <= 4:
            rec = self.records["floors"][self.current_floor - 1]
            if rec:
                self.label_delta_live.config(text=f"Floor {self.current_floor} | Best: {self.formatear_tiempo(rec)}", fg="#888888")
            else:
                self.label_delta_live.config(text=f"Floor {self.current_floor} | First Run", fg="#888888")
        else:
            self.label_delta_live.config(text="Run Completed!", fg="#e5c17b")

    # --- Auxiliares ---
    def formatear_tiempo(self, segs):
        return f"{int(segs//60):02d}:{int(segs%60):02d}.{int((segs%1)*100):02d}"

    # --- Mostrar / Ocultar Panel ---
    def toggle_panel(self):
        if self.panel_expandido:
            self.frame_floors.pack_forget()
            self.root.geometry(f"{self.ancho}x{self.alto_compacto}")
            self.btn_panel.config(text="+")
            self.panel_expandido = False
        else:
            # Añadimos un pequeño margen abajo (pady=(5, 10)) para que no se corte
            self.frame_floors.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
            self.root.geometry(f"{self.ancho}x{self.alto_expandido}")
            self.btn_panel.config(text="-")
            self.panel_expandido = True

    # --- Lógica de Tiempos ---
    def actualizar_reloj(self):
        if self.running:
            actual = self.tiempo_acumulado + (time.time() - self.tiempo_inicio)
            self.label_tiempo.config(text=self.formatear_tiempo(actual))
            
            # Cálculo del Delta en tiempo real para el piso actual
            if self.current_floor <= 4:
                record_piso = self.records["floors"][self.current_floor - 1]
                if record_piso:
                    # Tiempo que llevamos consumido solo en el piso actual
                    tiempo_anterior = self.tiempos_pisos[self.current_floor - 2] if self.current_floor > 1 else 0
                    tiempo_piso_actual = actual - tiempo_anterior
                    delta = tiempo_piso_actual - record_piso
                    
                    signo = "-" if delta < 0 else "+"
                    color = "#4ade80" if delta < 0 else "#f87171"
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
        
        # Si es mejor tiempo o primera run, actualizamos memoria de récords
        if record_piso is None or tiempo_del_piso < record_piso:
            self.records["floors"][self.current_floor - 1] = tiempo_del_piso

        self.current_floor += 1
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
            self.label_tiempo.config(fg="#e5c17b")
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = CronometroOverlay(root)
    root.mainloop()