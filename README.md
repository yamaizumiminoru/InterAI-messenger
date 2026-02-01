# InterAI Messenger (v0.2)

A seamless "Messenger" layer that bridges your local work context (VS Code, Terminal, etc.) and AI Agents (Gemini, ChatGPT).

## Key Features (v0.2)

### 📸 Reliable Capture
- **Manual Capture Button**: No more flaky hotkeys. Click the button in the UI, swtich to your target window, and wait 3 seconds.
- **Auto-Focus**: Designed to capture the *target* app, not the Messenger itself.

### 🧠 Smart Handoff
- **Context Aware**: Automatically detects if you are Coding (VS Code) or browsing (Chrome) and formats the AI prompt accordingly.
- **Text Injection**: Embeds your copied clipboard content directly into the Handoff prompt. No file uploads required for text transfer.
- **One-Click Generation**: Use the "Handoff をコピー" button to generate and copy the perfect prompt instantly.

### 🛠 Stability
- **Auto-Startup**: Runs automatically on Windows login.
- **Robustness**: Core logic exposed via HTTP API (`/api/debug/*`) to bypass OS-level hook limitations.

## Usage

1. **Start**: The app runs on `http://127.0.0.1:8000`.
2. **Capture**:
    - Click **"📷 Capture"**.
    - Switch to the window you want to discuss (e.g., VS Code).
    - Wait for the "Wait 3s..." countdown to finish.
3. **Draft**:
    - If you have code or logs to share, copy them (Ctrl+C).
4. **Handoff**:
    - Click **"Handoff をコピー"**.
    - Paste (Ctrl+V) into Gemini/ChatGPT.
    - The prompt will include your context + your copied logs + formatted instructions.

---
*Developed by [Antigravity]*
