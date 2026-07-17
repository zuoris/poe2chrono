"""
Tkinter UI for the Zarokh Sanctum timer overlay. This module only
handles widgets and rendering — all state and business logic lives
in AppController, Run, and RecordsManager.
"""
import logging
from pathlib import Path
import sys
import tkinter as tk
import webbrowser

from zarokh.app_controller import AppController
from zarokh.run import TOTAL_FLOORS, RunState
from zarokh.windows_utils import (
    force_taskbar_icon,
    get_window_handle,
    resolve_icon_path,
    set_app_user_model_id,
)

logger = logging.getLogger(__name__)


def format_time(seconds: float) -> str:
    """Formats a duration in seconds as MM:SS.CC."""
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}.{int((seconds % 1) * 100):02d}"


class _Tooltip:
    """Minimal hover tooltip — Tkinter has no built-in equivalent."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self._tipwindow: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def update_text(self, text: str) -> None:
        self.text = text

    def _show(self, event: tk.Event | None = None) -> None:
        if self._tipwindow is not None:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self._tipwindow = tk.Toplevel(self.widget)
        self._tipwindow.wm_overrideredirect(True)
        self._tipwindow.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._tipwindow, text=self.text, background="#222222", foreground="white",
            relief="solid", borderwidth=1, font=("Arial", 8), padx=4, pady=2,
        ).pack()

    def _hide(self, event: tk.Event | None = None) -> None:
        if self._tipwindow is not None:
            self._tipwindow.destroy()
            self._tipwindow = None


class CronometroOverlay:
    def __init__(self, root: tk.Tk, controller: AppController) -> None:
        self.root = root
        self.controller = controller
        self._ticking = False

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
        except tk.TclError as e:
            logger.warning("Could not load app icon from %s: %s", icon_path, e)

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

        frame_total = tk.Frame(self.root, bg="#1a1a1a")
        frame_total.pack(pady=(8, 0))

        self.label_tiempo = tk.Label(
            frame_total, text="00:00.00", font=("Consolas", 26, "bold"),
            fg="#e5c17b", bg="#1a1a1a",
        )
        self.label_tiempo.pack(side=tk.LEFT)

        self.label_total_delta = tk.Label(
            frame_total, text="--", font=("Consolas", 10, "bold"),
            fg="#888888", bg="#1a1a1a",
        )
        self.label_total_delta.pack(side=tk.LEFT, padx=(6, 0), pady=(10, 0), anchor="n")

        frame_floor = tk.Frame(self.root, bg="#1a1a1a")
        frame_floor.pack(pady=(0, 5))

        self.label_floor_indicator = tk.Label(
            frame_floor, text="Floor 1", font=("Consolas", 9, "bold"),
            fg="#777777", bg="#1a1a1a",
        )
        self.label_floor_indicator.pack(side=tk.LEFT, padx=(0, 4))

        self.label_floor_tiempo = tk.Label(
            frame_floor, text="00:00.00", font=("Consolas", 14, "bold"),
            fg="#e5c17b", bg="#1a1a1a",
        )
        self.label_floor_tiempo.pack(side=tk.LEFT)

        self.label_floor_delta = tk.Label(
            frame_floor, text="--", font=("Consolas", 10, "bold"),
            fg="#888888", bg="#1a1a1a",
        )
        self.label_floor_delta.pack(side=tk.LEFT, padx=(6, 0))

        frame_botones = tk.Frame(self.root, bg="#1a1a1a")
        frame_botones.pack(pady=2)

        self.btn_pause_restart = tk.Button(
            frame_botones, text="⏸", command=self._on_click_pause_restart,
            bg="#2a2a2a", fg="white", relief="flat", width=3,
            font=("Arial", 11), state=tk.DISABLED,
        )
        self.btn_pause_restart.pack(side=tk.LEFT, padx=4)
        self._pause_tooltip = _Tooltip(self.btn_pause_restart, "Pause")

        self.btn_cancel = tk.Button(
            frame_botones, text="✕", command=self._on_click_cancel,
            bg="#2a2a2a", fg="#f87171", relief="flat", width=3,
            font=("Arial", 11), state=tk.DISABLED,
        )
        self.btn_cancel.pack(side=tk.LEFT, padx=4)
        _Tooltip(self.btn_cancel, "Cancel")

        self.btn_panel = tk.Button(
            frame_botones, text="+", command=self._on_click_toggle_panel,
            bg="#333333", fg="#e5c17b", relief="flat", width=2, font=("Arial", 9, "bold"),
        )
        self.btn_panel.pack(side=tk.LEFT, padx=4)

        self.frame_floors = tk.Frame(self.root, bg="#111111")
        self.labels_pisos: list[tk.Label] = []
        for i in range(TOTAL_FLOORS):
            f = tk.Frame(self.frame_floors, bg="#111111")
            f.pack(fill=tk.X, padx=15, pady=2)
            tk.Label(
                f, text=f"Floor {i + 1} Best:", font=("Consolas", 10),
                fg="#777777", bg="#111111", anchor="w",
            ).pack(side=tk.LEFT)
            lbl_val = tk.Label(
                f, text="--:--.--", font=("Consolas", 10),
                fg="#bbbbbb", bg="#111111", anchor="e",
            )
            lbl_val.pack(side=tk.RIGHT)
            self.labels_pisos.append(lbl_val)

        f_total = tk.Frame(self.frame_floors, bg="#111111")
        f_total.pack(fill=tk.X, padx=15, pady=(5, 2))
        tk.Label(
            f_total, text="PB Total Time:", font=("Consolas", 10, "bold"),
            fg="#888888", bg="#111111", anchor="w",
        ).pack(side=tk.LEFT)
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

        self.btn_cerrar.lift()

        self.label_credit = tk.Label(
            self.root, text="by Zuo", font=("Arial", 7), fg="#555555", bg="#1a1a1a",
            cursor="hand2",
        )
        self.label_credit.pack(pady=(2, 4))
        self.label_credit.bind("<Button-1>", self._on_click_credit)

    def _bind_drag_events(self) -> None:
        for widget in [self.root, self.label_tiempo, self.label_floor_tiempo]:
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    # ------------------------------------------------------------------
    # Button callbacks — all delegate to AppController, never compute
    # ------------------------------------------------------------------

    def _on_click_pause_restart(self) -> None:
        self.controller.toggle_pause()
        self.refresh_all()
        self._ensure_ticking()

    def _on_click_cancel(self) -> None:
        self.controller.cancel()
        self.refresh_all()

    def _on_click_clear_records(self) -> None:
        self.controller.records.clear()
        self.controller.cancel()
        self.refresh_all()

    def _on_click_toggle_panel(self) -> None:
        if self.panel_expandido:
            self.frame_floors.pack_forget()
            self.root.geometry(f"{self.ancho}x{self.alto_compacto}")
            self.btn_panel.config(text="+")
            self.panel_expandido = False
        else:
            self.frame_floors.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            self.root.geometry(f"{self.ancho}x{self.alto_expandido}")
            self.btn_panel.config(text="-")
            self.panel_expandido = True

    def _on_click_credit(self, event: tk.Event) -> None:
        webbrowser.open("https://github.com/zuoris/poe2chrono")

    # ------------------------------------------------------------------
    # Called from LogWatcher, via root.after (see __main__.py)
    # ------------------------------------------------------------------

    def handle_log_event(self, event_name: str) -> None:
        self.controller.handle_log_event(event_name)
        self.refresh_all()
        self._ensure_ticking()

    # ------------------------------------------------------------------
    # Rendering — reads state, never mutates it
    # ------------------------------------------------------------------

    def refresh_all(self) -> None:
        run = self.controller.run

        controls_enabled = run.state == RunState.RUNNING
        self.btn_pause_restart.config(state=tk.NORMAL if controls_enabled else tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL if controls_enabled else tk.DISABLED)

        if run.is_paused:
            self.btn_pause_restart.config(text="▶")
            self._pause_tooltip.update_text("Restart")
        else:
            self.btn_pause_restart.config(text="⏸")
            self._pause_tooltip.update_text("Pause")

        self._refresh_time_display()
        self._refresh_records_panel()

    def _refresh_time_display(self) -> None:
        run = self.controller.run

        self.label_tiempo.config(text=format_time(run.total_timer.elapsed_time()))
        self._render_delta(self.label_total_delta, self.controller.total_delta())

        self.label_floor_indicator.config(text=f"Floor {self.controller.display_floor_number()}")
        self.label_floor_tiempo.config(text=format_time(run.floor_timer.elapsed_time()))
        self._render_delta(self.label_floor_delta, self.controller.floor_delta())

    def _render_delta(self, label: tk.Label, delta: float | None) -> None:
        if delta is None:
            label.config(text="--", fg="#888888")
            return
        sign = "-" if delta < 0 else "+"
        color = "#4ade80" if delta < 0 else "#f87171"
        label.config(text=f"{sign}{abs(delta):.1f}s", fg=color)

    def _refresh_records_panel(self) -> None:
        records = self.controller.records
        for i in range(TOTAL_FLOORS):
            best = records.best_floor_time(i + 1)
            self.labels_pisos[i].config(text=format_time(best) if best else "--:--.--")
        total = records.best_total_time()
        self.lbl_total_val.config(text=format_time(total) if total else "--:--.--")

    def _ensure_ticking(self) -> None:
        if self._ticking:
            return
        run = self.controller.run
        if run.state == RunState.RUNNING and not run.is_paused:
            self._ticking = True
            self._tick()

    def _tick(self) -> None:
        run = self.controller.run
        if run.state != RunState.RUNNING or run.is_paused:
            self._ticking = False
            return
        self._refresh_time_display()
        self.root.after(50, self._tick)

    # ------------------------------------------------------------------
    # Window dragging
    # ------------------------------------------------------------------

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event: tk.Event) -> None:
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")
