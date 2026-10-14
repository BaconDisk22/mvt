"""MVT desktop preview. Requires explicit authorization for each investigation."""
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

def main():
    root = tk.Tk()
    root.title("MVT Forensic Suite")
    root.geometry("800x540")
    backup, output = tk.StringVar(), tk.StringVar()
    consent = tk.BooleanVar(value=False)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="MVT FORENSIC SUITE", font=("Helvetica", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Experimental iPhone backup analysis — authorized use only").pack(anchor="w")
    def choose(var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
    for title, var in (("Choose iPhone backup", backup), ("Choose results directory", output)):
        ttk.Button(frame, text=title, command=lambda v=var: choose(v)).pack(anchor="w", pady=(14, 2))
        ttk.Entry(frame, textvariable=var).pack(fill="x")
    ttk.Checkbutton(frame, text="I own this data or have explicit permission to analyze it", variable=consent).pack(anchor="w", pady=15)
    log = scrolledtext.ScrolledText(frame, height=12)
    log.pack(fill="both", expand=True)
    log.insert("end", "No findings does not mean a device is clean.\n")
    def finish(message):
        log.insert("end", message)
        log.see("end")
        run_button.configure(state="normal")
    def run():
        if not consent.get() or not backup.get() or not output.get():
            messagebox.showwarning("Authorization and folders required", "Confirm authorization and select both folders.")
            return
        run_button.configure(state="disabled")
        def worker():
            try:
                result = subprocess.run([sys.executable, "-m", "mvt.ios", "check-backup", "--output", output.get(), backup.get()], capture_output=True, text=True, timeout=3600)
                message = result.stdout + "\n" + result.stderr + f"\nExit status: {result.returncode}\n"
            except Exception as exc:
                message = f"Analysis failed: {exc}\n"
            root.after(0, finish, message)
        threading.Thread(target=worker, daemon=True).start()
    run_button = ttk.Button(frame, text="Analyze backup", command=run)
    run_button.pack(anchor="w", pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
