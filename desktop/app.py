"""Consent-focused MVT desktop preview with a packaged scan worker."""
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:
    from desktop.cases import create_case, list_cases
    from desktop.history import list_scans, save_scan
    from desktop.integrity import sha256_file
except ModuleNotFoundError:
    from cases import create_case, list_cases
    from history import list_scans, save_scan
    from integrity import sha256_file


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
    history_tab = ttk.Frame(tabs, padding=16)
    tabs.add(history_tab, text="Scan History")
    ttk.Label(history_tab, text="LOCAL SCAN OUTCOMES").pack(anchor="w")
    ttk.Label(history_tab, text="Execution status only; not a finding or clean-device verdict.").pack(anchor="w")
    history_list = tk.Listbox(history_tab, bg="#1f2937", fg="#f9fafb", height=15)
    history_list.pack(fill="both", expand=True, pady=12)

    def refresh_history():
        history_list.delete(0, "end")
        try:
            for record in list_scans():
                history_list.insert("end", record["created_at"][:19] + "  ·  " + record["status"])
        except OSError as exc:
            messagebox.showerror("Cannot load history", str(exc))

    ttk.Button(history_tab, text="Refresh history", command=refresh_history).pack(anchor="w")
    refresh_history()
    integrity_tab = ttk.Frame(tabs, padding=16)
    tabs.add(integrity_tab, text="Evidence Integrity")
    ttk.Label(integrity_tab, text="READ-ONLY EVIDENCE VERIFICATION").pack(anchor="w")
    ttk.Label(integrity_tab, text="SHA-256 fingerprints do not establish chain of custody.").pack(anchor="w", pady=(4, 12))
    evidence_path = tk.StringVar()
    expected_digest = tk.StringVar()
    actual_digest = tk.StringVar(value="Select a regular evidence file to calculate its SHA-256.")
    def select_evidence():
        selected = filedialog.askopenfilename(title="Select evidence file")
        if selected:
            evidence_path.set(selected)
    ttk.Button(integrity_tab, text="Choose evidence file", command=select_evidence).pack(anchor="w")
    ttk.Entry(integrity_tab, textvariable=evidence_path, state="readonly").pack(fill="x", pady=(4, 12))
    ttk.Label(integrity_tab, text="Expected SHA-256 (optional):").pack(anchor="w")
    ttk.Entry(integrity_tab, textvariable=expected_digest).pack(fill="x")
    ttk.Label(integrity_tab, textvariable=actual_digest, wraplength=780).pack(anchor="w", pady=12)
    def hash_evidence():
        if not evidence_path.get():
            messagebox.showwarning("File required", "Choose a regular evidence file.")
            return
        hash_button.configure(state="disabled")
        selected = evidence_path.get()
        expected = expected_digest.get().strip()
        def worker():
            try:
                actual = sha256_file(selected)
                if expected:
                    if len(expected) != 64 or any(c not in "0123456789abcdefABCDEF" for c in expected):
                        raise ValueError("Expected a 64-character SHA-256 hexadecimal digest")
                    matches = actual == expected.lower()
                    message = actual + ("  — MATCH" if matches else "  — MISMATCH")
                else:
                    message = actual
            except (OSError, ValueError) as exc:
                message = "Verification failed: " + str(exc)
            root.after(0, lambda: (actual_digest.set(message), hash_button.configure(state="normal")))
        threading.Thread(target=worker, daemon=True).start()
    hash_button = ttk.Button(integrity_tab, text="Calculate / Verify SHA-256", command=hash_evidence)
    hash_button.pack(anchor="w", pady=10)
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
        ttk.Entry(scan_tab, textvariable=var).pack(fill="x")
    ttk.Checkbutton(scan_tab, text="I own this data or have explicit permission to analyze it", variable=consent).pack(anchor="w", pady=15)
    log = scrolledtext.ScrolledText(scan_tab, height=12)
    log.pack(fill="both", expand=True)
    log.insert("end", "No findings does not mean a device is clean.\n")

    def finish(message, status):
        try:
            save_scan(status)
            refresh_history()
        except OSError as exc:
            message += f"\nWarning: scan history was not saved: {exc}\n"
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
                status = "completed" if result.returncode == 0 else "failed"
            except subprocess.TimeoutExpired:
                message = "Analysis timed out after one hour.\n"
                status = "timed_out"
            except Exception as exc:
                message = f"Analysis failed: {exc}\n"
                status = "failed"
            root.after(0, finish, message, status)

        threading.Thread(target=worker, daemon=True).start()

    run_button = ttk.Button(scan_tab, text="Analyze backup", command=run)
    run_button.pack(anchor="w", pady=10)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mvt-scan-worker":
        worker_main(sys.argv[2:])
    else:
        main()
