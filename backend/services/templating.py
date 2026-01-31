
import os
from jinja2 import Template
from .case_mgr import case_manager

HANDOFF_TEMPLATE = """# 目的
{{ active_app }} の作業を再開する

# 状況
{{ active_app }} 実行中に、外部サービスの {{ issue_type_ja }} が表示され、作業が中断されている

# 添付
- {{ latest_screenshot }}
{% if has_clip %}- clip.txt（参考）{% endif %}

# 依頼
1. この画面が何を意味するか説明してください
2. ユーザーが取るべき操作を手順で示してください
3. 注意点や別パターンがあれば挙げてください
4. 追加で必要な情報があれば質問してください
"""

class TemplatingService:
    def generate_handoff(self, context: dict):
        case = case_manager.get_current_case()
        
        # Determine strict context
        active_app = context.get('active_app', 'Unknown App')
        latest_screenshot_path = context.get('latest_screenshot_path')
        latest_screenshot = os.path.basename(latest_screenshot_path) if latest_screenshot_path else "なし"
        
        has_clip = os.path.exists(case.clip_path)
        
        # Simple heuristic for issue type (Placeholder for logic)
        issue_type_ja = "不明な状態" 
        # In a real implementation, we'd check window title keywords here
        
        data = {
            "active_app": active_app,
            "issue_type_ja": issue_type_ja,
            "latest_screenshot": latest_screenshot,
            "has_clip": has_clip
        }
        
        template = Template(HANDOFF_TEMPLATE)
        content = template.render(data)
        
        # Write to file
        with open(case.handoff_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        case_manager.log_action("generate_handoff", data)
        return content

templating_service = TemplatingService()
