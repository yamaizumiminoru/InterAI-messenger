
import os
import json
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel

# Configuration Defaults
DEFAULT_CASE_ROOT = os.path.expanduser("~/MessengerCases")

class Case(BaseModel):
    path: str
    name: str
    created_at: str
    
    @property
    def input_dir(self): return os.path.join(self.path, "input")
    
    @property
    def output_dir(self): return os.path.join(self.path, "output")
    
    @property
    def handoff_path(self): return os.path.join(self.path, "handoff", "handoff.md")
    
    @property
    def clip_path(self): return os.path.join(self.input_dir, "clip.txt")

class CaseManager:
    def __init__(self, root_dir: str = DEFAULT_CASE_ROOT):
        self.root_dir = root_dir
        self.ensure_root()
        self._current_case: Optional[Case] = None

    def ensure_root(self):
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
            # Create a log directory
            os.makedirs(os.path.join(self.root_dir, "log"), exist_ok=True)

    def get_log_path(self):
        return os.path.join(self.root_dir, "log", "actions.jsonl")

    def log_action(self, action_type: str, details: Dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "details": details
        }
        with open(self.get_log_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def create_case(self, title: str = "auto") -> Case:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_name = f"{timestamp}_{title}"
        case_path = os.path.join(self.root_dir, case_name)
        
        # Create subdirectories
        os.makedirs(os.path.join(case_path, "input"), exist_ok=True)
        os.makedirs(os.path.join(case_path, "handoff"), exist_ok=True)
        os.makedirs(os.path.join(case_path, "output"), exist_ok=True)
        
        self._current_case = Case(path=case_path, name=case_name, created_at=timestamp)
        self.log_action("create_case", {"case_name": case_name})
        return self._current_case

    def get_current_case(self) -> Case:
        if not self._current_case:
            # If no current case, create one
            return self.create_case()
        return self._current_case
    
    def set_current_case(self, case_name: str):
         # Search key logic or just simplistic for now
         potential_path = os.path.join(self.root_dir, case_name)
         if os.path.exists(potential_path):
             self._current_case = Case(
                 path=potential_path, 
                 name=case_name, 
                 created_at=case_name.split("_")[0] # approximate
             )

    def list_cases(self, limit=20) -> List[Case]:
        # List directories in root_dir, sort by name desc (timestamp)
        dirs = [d for d in os.listdir(self.root_dir) if os.path.isdir(os.path.join(self.root_dir, d)) and d != "log"]
        dirs.sort(reverse=True)
        cases = []
        for d in dirs[:limit]:
            cases.append(Case(
                path=os.path.join(self.root_dir, d),
                name=d,
                created_at=d.split("_")[0] 
            ))
        return cases

# Singleton instance
case_manager = CaseManager()
