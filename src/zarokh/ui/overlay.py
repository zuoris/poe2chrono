"""
Tkinter UI for the Zarokh Sanctum timer overlay. This module only
handles widgets and rendering — all state and business logic lives
in AppController, RunTimer, and RecordsManager.
"""
import sys
from pathlib import Path
from typing import Callable

import tkinter as tk
from tkinter import filedialog

from zarokh.app_controller import AppController
from zarokh.windows_utils import (
    force_taskbar_icon,
    get_window_handle,
    resolve_icon_path,
    set_app_user_model_id,
)

TOTAL_FLOORS = 4


def format_time(seconds: float) -> str:
    """Formats a duration in seconds as MM:SS.CC."""
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}.{int((seconds % 1) * 100):02d}"


class CronometroOverlay:
    def __init__(
        self,
        root: tk.Tk,
        controller: AppController,
        auto_mode: bool,
        on_manual_path_selected: Callable[[str], None] | None = None,
    ):
        self.root = root
        self.controller = controller
        self.auto_mode = auto_mode
        self.on_manual_path_selected = on_manual_path_selected

        self.root.title("Zarokh - PoE2 Tracker")
        self._setup_window_icon()

        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.ancho = 240
        self.alto_compacto = 135
        self.alto_expandido = 305
        self.root.geometry(f"{self.ancho}x{self.alto_compacto}+100+100")
        self.root.configure(bg="#1a1a1a")

        self._force_taskbar_icon()

        self.panel_expandido = False
        self._build_widgets()
        self._bind_drag_events()

        self.refresh_all()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_window_icon(self) -> None:
        if not getattr(sys, "frozen", False):
            return

        set_app_user_model_id("zarokh.tracker.v3")
        base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3])
        icon_path = resolve_icon_path(base_path)
        try:
            icon_img = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, icon_img)
        except tk.TclError:
            pass

    def _force_taskbar_icon(self) -> None:
        self.root.update_idletasks()
        hwnd = get_window_handle(self.root.winfo_id())
        force_taskbar_icon(hwnd)
        self.root.wm_withdraw()
        self.root.after(10, self.root.wm_deiconify)

    def _build_widgets(self) -> None:
        self.btn_cerrar = tk.Button(
            self.root, text="X", command=self.root.destroy,
            bg="#1a1a1a", fg="#555555", relief="flat", font=("Arial", 8, "bold"),
        )
        self.btn_cerrar.place(x=222, y=2)

        self.label_tiempo = tk.Label(
            self.root, text="00:00.00", font=("Consolas", 26, "bold"),
            fg="#e5c17b", bg="#1a1a1a",
        )
        self.label_tiempo.pack(pady=(8, 0))

        self.label_delta_live = tk.Label(
            self.root, text="Waiting for Sekhemas...", font=("Consolas", 10),
            fg="#888888", bg="#1a1a1a",
        )
        self.label_delta_live.pack(pady=(0, 2))

        self.btn_modo_status = tk.Button(
            self.root, text="", command=self._on_click_modo_status,
            relief="flat", font=("Arial", 7, "bold"), bd=0, cursor="hand2",
        )
        self.btn_modo_status.pack(pady=(0, 5))

        frame_botones = tk.Frame(self.root, bg="#1a1a1a")
        frame_botones.pack(pady=2)

        self.btn_toggle = tk.Button(
            frame_botones, text="Start", command=self._on_click_toggle,
            bg="#2a2a2a", fg="white", relief="flat", width=6,
        )
        self.btn_toggle.pack(side=tk.LEFT, padx=2)

        self.btn_floor = tk.Button(
            frame_botones, text="Floor", command=self._on_click_floor,
            bg="#2a2a2a", fg="white", relief="flat", width=6, state=tk.DISABLED,
        )
        self.btn_floor.pack(side=tk.LEFT, padx=2)

        self.btn_reset = tk.Button(
            frame_botones, text="Reset", command=self._on_click_reset,
            bg="#2a2a2a", fg="white", relief="flat", width=6,
        )
        self.btn_reset.pack(side=tk.LEFT, padx=2)

        self.btn_panel = tk.Button(
            frame_botones, text="+", command=self._on_click_toggle_panel,
            bg="#333333", fg="#e5c17b", relief="flat", width=2, font=("Arial", 9, "bold"),
        )
        self.btn_panel.pack(side=tk.LEFT, padx=2)

        self.frame_floors = tk.Frame(self.root, bg="#111111")
        self.labels_pisos = []
        for i in range(TOTAL_FLOORS):
            f = tk.Frame(self.frame_floors, bg="#111111")
            f.pack(fill=tk.X, padx=15, pady=2)
            lbl_name = tk.Label(
                f, text=f"Floor {i + 1} Best:", font=("Consolas", 10),
                fg="#777777", bg="#111111", anchor="w",
            )
            lbl_name.pack(side=tk.LEFT)
            lbl_val = tk.Label(
                f, text="--:--.--", font=("Consolas", 10),
                fg="#bbbbbb", bg="#111111", anchor="e",
            )
            lbl_val.pack(side=tk.RIGHT)
            self.labels_pisos.append(lbl_val)

        f_total = tk.Frame(self.frame_floors, bg="#111111")
        f_total.pack(fill=tk.X, padx=15, pady=(5, 2))
        lbl_t_name = tk.Label(
            f_total, text="PB Total Time:", font=("Consolas", 10, "bold"),
            fg="#888888", bg="#111111", anchor="w",
        )
        lbl_t_name.pack(side=tk.LEFT)
        self.lbl_total_val = tk.Label(
            f_total, text="--:--.--", font=("Consolas", 10, "bold"),
            fg="#e5c17b", bg="#111111", anchor="e",
        )
        self.lbl_total_val.pack(side=tk.RIGHT)

        self.btn_clear_records = tk.Button(
            self.frame_floors, text="Clear Records", command=self._on_click_clear_records,
            bg="#3a1a1a", fg="#f87171", relief="flat", font=("Arial", 9, "bold"),
            activebackground="#5a2a2a", activeforeground="white",
        )
        self.btn_clear_records.pack(fill=tk.X, padx=15, pady=(10, 5))

    def _bind_drag_events(self) -> None:
        for widget in [self.root, self.label_tiempo, self.label_delta_live]:
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    # ------------------------------------------------------------------
    # Button callbacks — all delegate to AppController, never compute
    # ------------------------------------------------------------------

    def _on_click_toggle(self) -> None:
        self.controller.toggle()
        self.refresh_all()
        if self.controller.timer.running:
            self._tick()

    def _on_click_floor(self) -> None:
        self.controller.register_floor()
        self.refresh_all()

    def _on_click_reset(self) -> None:
        self.controller.reset()
        self.refresh_all()

    def _on_click_clear_records(self) -> None:
        self.controller.records.clear()
        self.controller.reset()
        self.refresh_all()

    def _on_click_toggle_panel(self) -> None:
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

    def _on_click_modo_status(self) -> None:
        if self.auto_mode or self.on_manual_path_selected is None:
            return

        selected_file = filedialog.askopenfilename(
            title="Zarokh: Select your Client.txt to enable Auto Mode",
            filetypes=[("Text Files", "Client.txt"), ("All Files", "*.*")],
        )
        if selected_file:
            self.on_manual_path_selected(selected_file)
            self.set_auto_mode(True)

    # ------------------------------------------------------------------
    # Called from LogWatcher, via root.after (see __main__.py)
    # ------------------------------------------------------------------

    def handle_log_event(self, event_name: str) -> None:
        was_running = self.controller.timer.running
        self.controller.handle_log_event(event_name)
        self.refresh_all()
        if self.controller.timer.running and not was_running:
            self._tick()

    # ------------------------------------------------------------------
    # Rendering — reads state, never mutates it
    # ------------------------------------------------------------------

    def set_auto_mode(self, enabled: bool) -> None:
        self.auto_mode = enabled
        self._refresh_mode_indicator()

    def _refresh_mode_indicator(self) -> None:
        if self.auto_mode:
            self.btn_modo_status.config(
                text="● AUTO MODE", fg="#4ade80", bg="#1a1a1a",
                activebackground="#1a1a1a", activeforeground="#4ade80", state=tk.DISABLED,
            )
        else:
            self.btn_modo_status.config(
                text="○ MANUAL MODE (Click to link PoE2)", fg="#a3a3a3", bg="#1a1a1a",
                activebackground="#1a1a1a", activeforeground="white", state=tk.NORMAL,
            )

    def refresh_all(self) -> None:
        timer = self.controller.timer

        self.btn_toggle.config(text="Pause" if timer.running else "Start")
        self.btn_floor.config(state=tk.NORMAL if timer.running and not timer.is_finished else tk.DISABLED)

        self.label_tiempo.config(text=format_time(timer.elapsed_time()), fg="#e5c17b")
        self._refresh_delta_label()
        self._refresh_records_panel()
        self._refresh_mode_indicator()

    def _refresh_delta_label(self) -> None:
        timer = self.controller.timer
        if timer.is_finished:
            self.label_delta_live.config(text="Run Completed!", fg="#e5c17b")
            return

        best_time = self.controller.best_time_for_current_floor()
        if best_time is None:
            self.label_delta_live.config(
                text=f"Floor {timer.current_floor} | Best: First Run", fg="#888888",
            )
            return

        if not timer.running:
            self.label_delta_live.config(
                text=f"Floor {timer.current_floor} | Best: {format_time(best_time)}", fg="#888888",
            )
            self.label_tiempo.config(fg="#e5c17b")
            return

        delta = self.controller.current_delta()
        sign = "-" if delta < 0 else "+"
        color = "#4ade80" if delta < 0 else "#f87171"
        self.label_delta_live.config(
            text=f"Floor {timer.current_floor} | {sign}{abs(delta):.1f}s", fg=color,
        )
        self.label_tiempo.config(fg=color)

    def _refresh_records_panel(self) -> None:
        records = self.controller.records
        for i in range(TOTAL_FLOORS):
            best = records.best_floor_time(i + 1)
            self.labels_pisos[i].config(text=format_time(best) if best else "--:--.--")
        total = records.best_total_time()
        self.lbl_total_val.config(text=format_time(total) if total else "--:--.--")

    def _tick(self) -> None:
        if not self.controller.timer.running:
            return
        self.label_tiempo.config(text=format_time(self.controller.timer.elapsed_time()))
        self._refresh_delta_label()
        self.root.after(50, self._tick)

    # ------------------------------------------------------------------
    # Window dragging
    # ------------------------------------------------------------------

    def _start_drag(self, event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event) -> None:
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")