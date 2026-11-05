# MVT Forensic Suite — experimental Intel macOS preview

The desktop preview includes a dark GUI for iPhone backup analysis and local investigations. The `integrity.py` utility provides read-only SHA-256 hashing and digest verification for individual evidence files, with tests. **It is not yet wired into the GUI**, and does not replace a documented chain-of-custody procedure.

The `history.py` module now adds private metadata-only scan history (timestamp, status, optional case ID). This module is not yet connected to the GUI or scanner and stores no evidence paths or scan contents.\n\nThe app remains unsigned and unnotarized; Android workflows, scan history integration, findings, timelines, and reports remain pending. A successful CI build does not establish real Intel Mac launch or forensic scan reliability. Only investigate authorized data. No findings does not establish a clean device. Preserve upstream MVT licensing and attribution.
