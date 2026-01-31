
import mss
import mss.tools
import pyperclip
import os
import time
from datetime import datetime
from .case_mgr import case_manager

class CaptureService:
    def capture_screenshot(self):
        # Using MSS for fast capture
        # TODO: Implement "region selection" (darken screen etc) later.
        # MVP: Capture Active Monitor or Full Screen for now to keep it simple and robust, 
        # or just primary monitor.
        # Requirement says: "Hotkey A: Range Screenshot (Snipping Tool equivalent)". 
        # Implementing actual custom Snipping Tool UI in Python is complex.
        # ALTERNATIVE MVP: Trigger authorized OS Snipping Tool and watch filesystem? 
        # OR: Just take full screen for MVP and user crops?
        # OR: Use `pygetwindow` to screenshot ACTIVE WINDOW. This is very useful.
        
        # Let's do ACTIVE WINDOW capture for MVP v0.1 as it's cleaner than building a selector UI.
        
        import pygetwindow as gw
        
        case = case_manager.get_current_case()
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"screen_{timestamp}.png"
        filepath = os.path.join(case.input_dir, filename)
        
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                # MSS doesn't easily capture by handle, but can capture by hierarchy.
                # Actually, simple PIL ImageGrab might be easier for regions if we knew them.
                # Let's stick to MSS full screen for reliability first, or create a simple logic.
                
                with mss.mss() as sct:
                     # Capture the region of the active window
                    monitor = {
                        "top": active_window.top, 
                        "left": active_window.left, 
                        "width": active_window.width, 
                        "height": active_window.height
                    }
                    output = sct.grab(monitor)
                    mss.tools.to_png(output.rgb, output.size, output=filepath)
                    
                case_manager.log_action("capture_screenshot", {"file": filename, "window": active_window.title})
                return filepath, active_window.title
        except Exception as e:
            print(f"Screenshot failed: {e}")
            # Fallback to full screen
            with mss.mss() as sct:
                filename = f"screen_{timestamp}_full.png"
                filepath = os.path.join(case.input_dir, filename)
                sct.shot(mon=-1, output=filepath)
                case_manager.log_action("capture_screenshot_fallback", {"file": filename})
                return filepath, "Unknown"

    def save_clipboard(self):
        content = pyperclip.paste()
        if not content or not isinstance(content, str) or not content.strip():
            return None # Skip empty
        
        case = case_manager.get_current_case()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        header = f"\n--- {timestamp} ---\n"
        
        with open(case.clip_path, "a", encoding="utf-8") as f:
            f.write(header + content + "\n")
            
        case_manager.log_action("save_clipboard", {"length": len(content)})
        return content

capture_service = CaptureService()
