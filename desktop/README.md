# MVT Forensic Suite — experimental Intel macOS preview

The GUI currently provides a dark workspace with iPhone Analysis and local Investigations. The `history.py` module adds minimal private scan metadata storage for status, timestamp, and optional case ID; **history is not yet wired to the GUI or scan worker**. It deliberately stores no evidence contents, backup paths, or scan logs.

The app is unsigned and unnotarized. Android analysis, case-linked scans, findings, timelines, and reports are not yet implemented. CI builds and smoke tests do not replace actual Intel Mac launch and forensic validation. Analyze only data you own or are authorized to investigate. A scan with no findings does not establish a device is clean. Upstream MVT licensing and attribution apply.
