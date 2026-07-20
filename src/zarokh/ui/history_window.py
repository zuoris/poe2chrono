"""
Full run history window: a pinned record row plus a scrollable list
of past runs (most recent first). An independent Toplevel — unlike
the main overlay, it is NOT kept always-on-top. Styled to match the
main overlay: no native title bar, dark theme, a discreet close
button.
"""
import tkinter as tk
from tkinter import ttk

from zarokh.windows_utils import force_taskbar_icon, get_window_handle
from zarokh.records import RecordsManager
from zarokh.run import TOTAL_FLOORS

COLUMNS = ["attempt"] + [f"floor_{i}" for i in range(1, TOTAL_FLOORS + 1)] + ["total"]
HEADERS = ["#"] + [f"Floor {i}" for i in range(1, TOTAL_FLOORS + 1)] + ["Total"]

WIDTH = 540
HEIGHT = 280


def format_time(seconds: float | None) -> str:
    if seconds is None:
        return "--:--.--"
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}.{int((seconds % 1) * 100):02d}"


class HistoryWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, records: RecordsManager):
        super().__init__(master)
        self.records = records

        self.title("Zarokh - Run History")
        self.overrideredirect(True)
        self.configure(bg="#1a1a1a")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WIDTH) // 2
        y = (screen_height - HEIGHT) // 2
        self.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        self._force_taskbar_icon()

        self._build_widgets()
        self._bind_drag_events()
        self.bind("<Escape>", lambda e: self.destroy())
        self.refresh()

    def _build_widgets(self) -> None:
        self.btn_cerrar = tk.Button(
            self, text="X", command=self.destroy,
            bg="#1a1a1a", fg="#555555", relief="flat", font=("Arial", 8, "bold"),
        )
        self.btn_cerrar.place(x=WIDTH - 20, y=2)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Zarokh.Treeview",
            background="#111111", fieldbackground="#111111", foreground="#bbbbbb",
            rowheight=24, borderwidth=0,
        )
        style.configure(
            "Zarokh.Treeview.Heading",
            background="#222222", foreground="#e5c17b", relief="flat",
        )
        style.map("Zarokh.Treeview", background=[("selected", "#333333")])

        record_frame = tk.Frame(self, bg="#111111")
        record_frame.pack(fill=tk.X, padx=8, pady=(24, 4))
        self.record_tree = ttk.Treeview(
            record_frame, columns=COLUMNS, show="headings", height=1, style="Zarokh.Treeview",
        )
        for col, header in zip(COLUMNS, HEADERS):
            self.record_tree.heading(col, text=header)
            self.record_tree.column(col, width=40 if col == "attempt" else 70, anchor="center")
        self.record_tree.pack(fill=tk.X)

        runs_frame = tk.Frame(self, bg="#111111")
        runs_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        self.runs_tree = ttk.Treeview(
            runs_frame, columns=COLUMNS, show="", height=5, style="Zarokh.Treeview",
        )
        for col in COLUMNS:
            self.runs_tree.column(col, width=40 if col == "attempt" else 70, anchor="center")
        self.runs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(runs_frame, orient="vertical", command=self.runs_tree.yview)
        self.runs_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_cerrar.lift()

    def _force_taskbar_icon(self) -> None:
        self.update_idletasks()
        hwnd = get_window_handle(self.winfo_id())
        force_taskbar_icon(hwnd)
        self.wm_withdraw()
        self.after(10, self.wm_deiconify)

    def _bind_drag_events(self) -> None:
        self.bind("<ButtonPress-1>", self._start_drag)
        self.bind("<B1-Motion>", self._on_drag)

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event: tk.Event) -> None:
        x = self.winfo_x() + (event.x - self._drag_x)
        y = self.winfo_y() + (event.y - self._drag_y)
        self.geometry(f"+{x}+{y}")

    def refresh(self) -> None:
        self.record_tree.delete(*self.record_tree.get_children())
        record_values = (
            "PB",
            *[format_time(self.records.best_floor_time(i)) for i in range(1, TOTAL_FLOORS + 1)],
            format_time(self.records.best_total_time()),
        )
        self.record_tree.insert("", "end", values=record_values)

        self.runs_tree.delete(*self.runs_tree.get_children())
        for run in self.records.list_runs():
            floor_times = run["floor_times"]
            values = [f"{run['attempt']:04d}"]
            for i in range(TOTAL_FLOORS):
                values.append(format_time(floor_times[i]) if i < len(floor_times) else "")
            values.append(format_time(run["total_time"]))
            self.runs_tree.insert("", "end", values=values)
