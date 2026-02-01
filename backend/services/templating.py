
import os
from jinja2 import Template
from .case_mgr import case_manager

HANDOFF_TEMPLATE_SUPPORT = """# 目的
{{ active_app }} の作業を再開する

# 状況
{{ active_app }} 実行中に、外部サービスの {{ issue_type_ja }} が表示され、作業が中断されている

{% if clip_content %}
# 参考情報（クリップボード）
```
{{ clip_content }}
```
{% endif %}

# 依頼
1. この画面が何を意味するか説明してください
2. ユーザーが取るべき操作を手順で示してください
3. 注意点や別パターンがあれば挙げてください
4. 追加で必要な情報があれば質問してください
"""

HANDOFF_TEMPLATE_CODING = """# 依頼
以下のタスクを実行してください。

# 状況
ユーザーは {{ active_app }} を使用中です。

{% if clip_content %}
# 詳細指示（クリップボード）
```
{{ clip_content }}
```
{% endif %}

# ユーザーの意図（推測）
クリップボードまたは画像の内容に基づいて、コーディングまたは作業の継続を求めています。
"""

class TemplatingService:
    def generate_handoff(self, context: dict):
        case = case_manager.get_current_case()
        
        # Determine strict context
        active_app = context.get('active_app', 'Unknown App')
        latest_screenshot_path = context.get('latest_screenshot_path')
        latest_screenshot = os.path.basename(latest_screenshot_path) if latest_screenshot_path else "なし"
        
        clip_content = ""
        if os.path.exists(case.clip_path):
            try:
                with open(case.clip_path, "r", encoding="utf-8") as f:
                    clip_content = f.read()
            except: pass
        
        # Heuristic for Template Selection
        # If app is likely a dev tool, use Coding Template
        dev_keywords = ["Code", "Cursor", "Terminal", "PowerShell", "Command", "Gemini", "ChatGPT", "Claude", "Python", "Node"]
        is_coding = any(k in active_app for k in dev_keywords)

        issue_type_ja = "不明な状態" 
        
        data = {
            "active_app": active_app,
            "issue_type_ja": issue_type_ja,
            "latest_screenshot": latest_screenshot,
            "clip_content": clip_content
        }
        
        selected_template_str = HANDOFF_TEMPLATE_CODING if is_coding else HANDOFF_TEMPLATE_SUPPORT
        
        template = Template(selected_template_str)
        content = template.render(data)
        
        # Write to file
        with open(case.handoff_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        case_manager.log_action("generate_handoff", {"template": "coding" if is_coding else "support", "app": active_app})
        return content

templating_service = TemplatingService()
