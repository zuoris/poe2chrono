"""
Full run history window: pinned relic-totals and best-times rows,
plus a scrollable list of past runs (most recent first), each with
per-relic +/- editing for completed runs. An independent Toplevel —
unlike the main overlay, it is NOT kept always-on-top, styled to
match it (borderless, draggable, same close button, forced into the
taskbar/Alt+Tab). Sizes itself to fit its actual content instead of
a hand-tuned fixed size.
"""
import tkinter as tk
from tkinter import ttk

from zarokh.records import RecordsManager
from zarokh.relics import RELICS
from zarokh.run import TOTAL_FLOORS
from zarokh.ui.tooltip import Tooltip
from zarokh.windows_utils import force_taskbar_icon, get_window_handle

VISIBLE_RUN_ROWS = 5
ROW_HEIGHT = 26

# (key, character width, header label)
COLUMNS = (
    [
        ("attempt", 5, "#"),
        ("floor_1", 9, "F1"),
        ("floor_2", 9, "F2"),
        ("floor_3", 9, "F3"),
        ("floor_4", 9, "F4"),
        ("total", 9, "Total"),
    ]
    + [(f"relic_{i}", 9, short) for i, (_, short) in enumerate(RELICS)]
)


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

        self._force_taskbar_icon()
        self._build_widgets()
        self._bind_drag_events()
        self.bind("<Escape>", lambda e: self.destroy())
        self.refresh()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _force_taskbar_icon(self) -> None:
        self.update_idletasks()
        hwnd = get_window_handle(self.winfo_id())
        force_taskbar_icon(hwnd)
        self.wm_withdraw()
        self.after(10, self.wm_deiconify)

    def _build_widgets(self) -> None:
        self.btn_cerrar = tk.Button(
            self, text="X", command=self.destroy,
            bg="#1a1a1a", fg="#555555", relief="flat", font=("Arial", 8, "bold"),
        )
        # relx-based placement so it stays in the top-right corner
        # regardless of the window's final computed width.
        self.btn_cerrar.place(relx=1.0, x=-20, y=2, anchor="ne")

        header_frame = tk.Frame(self, bg="#222222")
        header_frame.pack(fill=tk.X, padx=8, pady=(24, 0))
        self._build_header_row(header_frame)

        pinned_frame = tk.Frame(self, bg="#111111")
        pinned_frame.pack(fill=tk.X, padx=8)
        self.totals_row = tk.Frame(pinned_frame, bg="#111111")
        self.totals_row.pack(fill=tk.X)
        self.best_row = tk.Frame(pinned_frame, bg="#111111")
        self.best_row.pack(fill=tk.X)

        runs_container = tk.Frame(self, bg="#111111")
        runs_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        self.canvas = tk.Canvas(
            runs_container, bg="#111111", highlightthickness=0,
            height=VISIBLE_RUN_ROWS * ROW_HEIGHT,
        )
        scrollbar = ttk.Scrollbar(runs_container, orient="vertical", command=self.canvas.yview)
        self.runs_inner = tk.Frame(self.canvas, bg="#111111")

        self.runs_inner.bind("<Configure>", self._on_runs_inner_configure)
        self.canvas.create_window((0, 0), window=self.runs_inner, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"),
        )

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_cerrar.lift()

    def _on_runs_inner_configure(self, event: tk.Event) -> None:
        """Keeps the canvas exactly as wide as its actual content —
        a Canvas doesn't inherit its embedded frame's width on its
        own, unlike a normal Frame/Label."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=event.width)

    def _build_header_row(self, parent: tk.Frame) -> None:
        for key, width, label in COLUMNS:
            cell = tk.Label(
                parent, text=label, width=width, font=("Consolas", 9, "bold"),
                fg="#e5c17b", bg="#222222", anchor="center",
            )
            cell.pack(side=tk.LEFT, padx=1, pady=3)
            if key.startswith("relic_"):
                index = int(key.split("_")[1])
                Tooltip(cell, RELICS[index][0])

    def _resize_to_content(self) -> None:
        """Sizes the window to fit its actual content — same
        technique used by the main overlay's window, applied to both
        width and height here instead of just height."""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        for widget in self.totals_row.winfo_children():
            widget.destroy()
        for widget in self.best_row.winfo_children():
            widget.destroy()
        for widget in self.runs_inner.winfo_children():
            widget.destroy()

        self._render_totals_row()
        self._render_best_row()
        for run in self.records.list_runs():
            self._render_run_row(run)

        self._resize_to_content()

    def _render_totals_row(self) -> None:
        totals = self.records.relic_totals()
        values = [""] * 6  # attempt + 4 floor columns + total: not applicable
        values += [str(totals[name]) for name, _ in RELICS]
        self._render_static_row(self.totals_row, values, fg="#c084fc")

    def _render_best_row(self) -> None:
        values = [
            "PB",
            *[format_time(self.records.best_floor_time(i)) for i in range(1, TOTAL_FLOORS + 1)],
            format_time(self.records.best_total_time()),
        ]
        values += [""] * len(RELICS)  # not applicable to relics
        self._render_static_row(self.best_row, values, fg="#e5c17b")

    def _render_static_row(self, parent: tk.Frame, values: list[str], fg: str) -> None:
        for (_, width, _), value in zip(COLUMNS, values):
            cell = tk.Label(
                parent, text=value, width=width, font=("Consolas", 10, "bold"),
                fg=fg, bg="#111111", anchor="center",
            )
            cell.pack(side=tk.LEFT, padx=1, pady=2)

    def _render_run_row(self, run: dict) -> None:
        row = tk.Frame(self.runs_inner, bg="#111111")
        row.pack(fill=tk.X)

        floor_times = run["floor_times"]
        relics = run.get("relics")  # None for cancelled runs

        tk.Label(
            row, text=f"{run['attempt']:04d}", width=COLUMNS[0][1],
            font=("Consolas", 10), fg="#bbbbbb", bg="#111111", anchor="center",
        ).pack(side=tk.LEFT, padx=1, pady=1)

        for i in range(TOTAL_FLOORS):
            text = format_time(floor_times[i]) if i < len(floor_times) else ""
            tk.Label(
                row, text=text, width=COLUMNS[1 + i][1],
                font=("Consolas", 10), fg="#bbbbbb", bg="#111111", anchor="center",
            ).pack(side=tk.LEFT, padx=1, pady=1)

        tk.Label(
            row, text=format_time(run["total_time"]), width=COLUMNS[5][1],
            font=("Consolas", 10), fg="#bbbbbb", bg="#111111", anchor="center",
        ).pack(side=tk.LEFT, padx=1, pady=1)

        for relic_name, _ in RELICS:
            self._render_relic_cell(row, run["attempt"], relic_name, relics)

    def _render_relic_cell(
        self, row: tk.Frame, attempt: int, relic_name: str, relics: dict | None,
    ) -> None:
        cell = tk.Frame(row, bg="#111111")
        cell.pack(side=tk.LEFT, padx=1, pady=1)

        if relics is None:
            tk.Label(
                cell, text="--", width=9, font=("Consolas", 9),
                fg="#555555", bg="#111111", anchor="center",
            ).pack()
            return

        count = relics.get(relic_name, 0)

        tk.Button(
            cell, text="-", width=2, font=("Arial", 8), relief="flat",
            bg="#2a2a2a", fg="white",
            command=lambda: self._on_click_relic_delta(attempt, relic_name, -1),
        ).pack(side=tk.LEFT)

        tk.Label(
            cell, text=str(count), width=2, font=("Consolas", 9),
            fg="#bbbbbb", bg="#111111", anchor="center",
        ).pack(side=tk.LEFT)

        tk.Button(
            cell, text="+", width=2, font=("Arial", 8), relief="flat",
            bg="#2a2a2a", fg="white",
            command=lambda: self._on_click_relic_delta(attempt, relic_name, 1),
        ).pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_click_relic_delta(self, attempt: int, relic_name: str, delta: int) -> None:
        self.records.adjust_relic_count(attempt, relic_name, delta)
        self.refresh()

    # ------------------------------------------------------------------
    # Window dragging
    # ------------------------------------------------------------------

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
