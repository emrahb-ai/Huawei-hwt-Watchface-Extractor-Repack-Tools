"""Windows graphical interface for Huawei HWT extractor / repacker."""
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from extract_huawei_watchface import extract_hwt
from repack import repack_folder


class WatchfaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Huawei HWT Watchface Tools")
        self.geometry("730x440")
        self.minsize(610, 350)
        self.target = tk.StringVar()
        self.operation = tk.StringVar(value="extract")
        self.events = queue.Queue()
        self.busy = False

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Huawei HWT Watchface Tools", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Extract and repack HWT watchfaces (offline)").pack(anchor="w", pady=(4, 16))
        modes = ttk.Frame(frame)
        modes.pack(anchor="w", pady=(0, 10))
        ttk.Radiobutton(modes, text="Extract HWT", variable=self.operation, value="extract").pack(side="left", padx=(0, 20))
        ttk.Radiobutton(modes, text="Repack folder", variable=self.operation, value="repack").pack(side="left")
        chooser = ttk.Frame(frame)
        chooser.pack(fill="x")
        ttk.Entry(chooser, textvariable=self.target).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(chooser, text="Choose HWT", command=self.choose_file).pack(side="left", padx=(0, 5))
        ttk.Button(chooser, text="Choose folder", command=self.choose_folder).pack(side="left")
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=14)
        self.run_button = ttk.Button(controls, text="Run Extract / Repack", command=self.start)
        self.run_button.pack(side="left")
        self.progress = ttk.Progressbar(controls, mode="indeterminate", length=200)
        self.progress.pack(side="left", padx=12)
        ttk.Label(frame, text="Activity log").pack(anchor="w")
        self.log = tk.Text(frame, height=10, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True, pady=(5, 5))
        ttk.Label(frame, text="You may also drag an .hwt or extracted folder onto the EXE icon.").pack(anchor="w")

        if len(sys.argv) > 1:
            dropped = Path(sys.argv[1])
            if dropped.exists():
                self.target.set(str(dropped.resolve()))
                self.operation.set("repack" if dropped.is_dir() else "extract")
                self.after(350, self.start)
        self.after(100, self.process_events)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("HWT files", "*.hwt"), ("All files", "*.*")])
        if path:
            self.target.set(path)
            self.operation.set("extract")

    def choose_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.target.set(path)
            self.operation.set("repack")

    def write_log(self, line):
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        if self.busy:
            return
        path = Path(self.target.get().strip().strip('"'))
        mode = self.operation.get()
        if not path.exists() or (mode == "extract" and not path.is_file()) or (mode == "repack" and not path.is_dir()):
            messagebox.showerror("Invalid selection", "Choose an HWT file to extract or an extracted folder to repack.")
            return
        self.busy = True
        self.run_button.configure(state="disabled")
        self.progress.start(10)
        self.write_log(f"{mode.upper()}: {path}")
        threading.Thread(target=self.worker, args=(mode, path), daemon=True).start()

    def worker(self, mode, path):
        try:
            result = extract_hwt(path) if mode == "extract" else repack_folder(path)
            self.events.put(("SUCCESS", str(result)))
        except Exception as exc:
            self.events.put(("ERROR", f"{type(exc).__name__}: {exc}"))

    def process_events(self):
        try:
            while True:
                status, detail = self.events.get_nowait()
                self.write_log(f"{status}: {detail}")
                self.busy = False
                self.progress.stop()
                self.run_button.configure(state="normal")
                if status == "ERROR":
                    messagebox.showerror("Operation failed", detail)
                else:
                    messagebox.showinfo("Completed", "Operation finished; see the source folder for results.")
        except queue.Empty:
            pass
        self.after(100, self.process_events)


if __name__ == "__main__":
    WatchfaceApp().mainloop()
