"""
Minimal hover tooltip widget — Tkinter has no built-in equivalent.
Shared between CronometroOverlay and HistoryWindow.
"""
import tkinter as tk


class Tooltip:
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
