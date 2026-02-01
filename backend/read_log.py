
import os

log_file = "backend.log"
if os.path.exists(log_file):
    try:
        with open(log_file, "r", encoding="utf-16") as f:
            print(f.read())
    except Exception as e:
        print(f"UTF-16 failed: {e}")
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                print(f.read())
        except Exception as e2:
            print(f"UTF-8 failed: {e2}")
else:
    print("Log file not found.")
