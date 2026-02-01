import keyboard
import pyperclip
import os
from .capture import capture_service
from .templating import templating_service
from .case_mgr import case_manager

class HotkeyManager:
    def __init__(self):
        self.is_running = False

    def on_screenshot(self):
        print("Hotkey: Screenshot triggered")
        # 1. Create NEW Case for every screenshot action (MVP behavior)
        case = case_manager.create_case() 
        # 2. Capture
        path, context_app = capture_service.capture_screenshot()
        print(f"Captured: {path} from {context_app}")
        
        # 3. Persist Metadata for Handoff
        try:
             meta_path = os.path.join(case.path, "meta.json")
             import json
             with open(meta_path, "w", encoding="utf-8") as f:
                 json.dump({"active_app": context_app}, f)
        except Exception as e:
            print(f"Failed to save metadata: {e}")

    def on_clip_save(self):
        print("Hotkey: Clip Save triggered")
        content = capture_service.save_clipboard()
        if content:
            print(f"Saved clip: {len(content)} chars")

    def on_handoff(self):
        print("Hotkey: Handoff triggered")
        
        # Get latest screenshot from case
        case = case_manager.get_current_case()
        
        # Determine Active App Context
        # Priority 1: Saved Metadata (from screenshot time)
        active_app = "Unknown"
        meta_path = os.path.join(case.path, "meta.json")
        if os.path.exists(meta_path):
            try:
                import json
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    active_app = data.get("active_app", "Unknown")
            except: pass
        else:
            # Fallback: Current Active Window (Legacy behavior)
            import pygetwindow as gw
            try:
                 w = gw.getActiveWindow()
                 if w: active_app = w.title
            except: pass

        # Find latest png in input
        files = [f for f in os.listdir(case.input_dir) if f.endswith(".png")]
        files.sort(reverse=True) # timestamp desc
        latest = os.path.join(case.input_dir, files[0]) if files else None

        context = {
            "active_app": active_app,
            "latest_screenshot_path": latest
        }
        
        content = templating_service.generate_handoff(context)
        pyperclip.copy(content)
        print("Handoff generated and copied to clipboard.")

    def start_listener(self):
        if self.is_running: return
        
        # Hotkeys
        # Hotkey A: Ctrl+Shift+1
        keyboard.add_hotkey('ctrl+shift+1', self.on_screenshot)
        
        # Hotkey B: Ctrl+Shift+2
        keyboard.add_hotkey('ctrl+shift+2', self.on_clip_save)
        
        # Hotkey C: Ctrl+Shift+3
        keyboard.add_hotkey('ctrl+shift+3', self.on_handoff)
        
        self.is_running = True
        print("Global Hotkey Listener Started: Ctrl+Shift+1/2/3")

hotkey_mgr = HotkeyManager()
