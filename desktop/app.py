"""Consent-focused MVT desktop preview with a packaged scan worker."""
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:
    from desktop.cases import create_case, list_cases
except ModuleNotFoundError:
    from cases import create_case, list_cases


def scan_command(executable, backup, output):
    """Run the bundled app in worker mode, not a non-existent -m entrypoint."""
    return [executable, "--mvt-scan-worker", "--output", output, backup]


def worker_main(args):
    """Invoke MVT's documented CLI entrypoint in the packaged process."""
    from mvt.ios import main as ios_main
    sys.argv = ["mvt-ios", "check-backup", *args]
    ios_main()


def main():
    root = tk.Tk()
    root.title("MVT Forensic Suite")
    root.geometry("960x680")
    root.configure(bg="#111827")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#111827")
    style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Helvetica", 12))
    style.configure("Header.TLabel", background="#111827", foreground="#f8fafc", font=("Helvetica", 24, "bold"))
    style.configure("TButton", padding=8)
    style.configure("TCheckbutton", background="#111827", foreground="#e5e7eb")
    backup, output = tk.StringVar(), tk.StringVar()
    consent = tk.BooleanVar(value=False)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="MVT FORENSIC SUITE", style="Header.TLabel").pack(anchor="w")
    ttk.Label(frame, text="Intel Mac forensic workspace · authorized investigations only").pack(anchor="w")
    tabs = ttk.Notebook(frame)
    tabs.pack(fill="both", expand=True, pady=(18, 0))
    scan_tab = ttk.Frame(tabs, padding=16)
    cases_tab = ttk.Frame(tabs, padding=16)
    tabs.add(scan_tab, text="iPhone Analysis")
    tabs.add(cases_tab, text="Investigations")
    case_name = tk.StringVar()
    ttk.Label(cases_tab, text="LOCAL INVESTIGATIONS").pack(anchor="w")
    ttk.Label(cases_tab, text="Case metadata stays on this Mac; no evidence files are copied.").pack(anchor="w", pady=(4, 12))
    ttk.Entry(cases_tab, textvariable=case_name).pack(fill="x")
    case_list = tk.Listbox(cases_tab, bg="#1f2937", fg="#f9fafb", selectbackground="#2563eb", relief="flat", height=12)
    case_list.pack(fill="both", expand=True, pady=12)

    def refresh_cases():
        case_list.delete(0, "end")
        try:
            for record in list_cases():
                case_list.insert("end", record["name"] + "  ·  " + record["created_at"][:10])
        except OSError as exc:
            messagebox.showerror("Cannot read cases", str(exc))

    def add_case():
        try:
            create_case(case_name.get())
        except (OSError, ValueError) as exc:
            messagebox.showerror("Cannot create case", str(exc))
            return
        case_name.set("")
        refresh_cases()

    ttk.Button(cases_tab, text="Create investigation", command=add_case).pack(anchor="w")
    ttk.Button(cases_tab, text="Refresh investigations", command=refresh_cases).pack(anchor="w", pady=8)
    refresh_cases()

    def choose(var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    for title, var in (("Choose iPhone backup", backup), ("Choose results directory", output)):
        ttk.Button(scan_tab, text=title, command=lambda v=var: choose(v)).pack(anchor="w", pady=(14, 2))
        ttk.Entry(scan_tab, textvariable=var.pack(fill="x")
    ttk.Checkbutton(scan_tab, text="I own this data or have explicit permission to analyze it", variable=consent).pack(anchor="w", pady=15)
    log = scrolledtext.ScrolledText(scan_tab, height=12)
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
                result = subprocess.run(scan_command(sys.executable, backup.get(), output.get()), capture_output=True, text=True, timeout=3600)
                message = result.stdout + "\n" + result.stderr + f"\nExit status: {result.returncode}\n"
            except Exception as exc:
                message = f"Analysis failed: {exc}\n"
            root.after(0, finish, message)

        threading.Thread(target=worker, daemon=True).start()

    run_button = ttk.Button(scan_tab, text="Analyze backup", command=run)
    run_button.pack(anchor="w", pady=10)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mvt-scan-worker":
        worker_main(sys.argv[2:])
    else:
        main()
