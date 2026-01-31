# InterAI-messenger

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14777777.svg)](https://zenodo.org/) <!-- Replace with actual DOI badge URL from Zenodo if available, otherwise generic placeholder -->

**English** | [日本語](#interai-messenger-日本語)

A desktop utility designed to bridge the gap between human workflows and AI assistants (like Gemini/ChatGPT).  
It reduces the cognitive load of "describing the context" by capturing screenshots, logs, and generating structured prompts via global hotkeys.

## Features

- **Global Hotkeys**: Capture context instantly without leaving your active window.
- **Auto-Context**: Automatically saves the active window's screenshot.
- **Clipboard Logger**: Appends copied text (logs, error messages) to a running log file.
- **Handoff Generation**: Generates a structured markdown prompt (`handoff.md`) summarizing the situation for AI adjustment.
- **Local Database**: All data is stored locally in your home directory (`~/MessengerCases`).

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yamaizumiminoru/InterAI-messenger.git
   ```
2. Install dependencies:
   ```bash
   cd InterAI-messenger
   pip install -r backend/requirements.txt
   ```

## Usage

### 1. Start the App
Run the launcher script:
- **Windows**: Double-click `start_messenger.bat`

Or via terminal:
```bash
cd backend
python main.py
```
Access the UI at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### 2. Workflow (Hotkeys)

| Hotkey | Action | Use Case |
| :--- | :--- | :--- |
| **`Ctrl` + `Shift` + `1`** | **Capture** | Take a screenshot of the active window and create a new case. |
| **`Ctrl` + `Shift` + `2`** | **Log Clip** | Append current clipboard content (errors/code) to the case log. |
| **`Ctrl` + `Shift` + `3`** | **Handoff** | Generate a prompt (`handoff.md`) and **copy it to clipboard**. |

### 3. Ask AI
Paste (`Ctrl+V`) the generated handoff content into Gemini or ChatGPT to get immediate help with full context.

---

# InterAI-messenger (日本語)

人間の作業とAIアシスタント（Gemini/ChatGPT等）の間にある「状況説明のコスト」を埋めるためのデスクトップツールです。  
ホットキー一発でスクショ撮影・ログ収集を行い、AIに投げるための指示書（Handoff）を自動生成します。

## 特徴

- **グローバルホットキー**: 作業中のウィンドウから移動せずに、瞬時にコンテキストを保存できます。
- **自動スクショ**: アクティブウィンドウを自動でキャプチャし、案件フォルダを作成します。
- **クリップボードログ**: コピーしたテキスト（エラーログ等）を時系列で追記保存します。
- **Handoff生成**: AIに渡すための構造化されたプロンプト（`handoff.md`）を自動生成し、クリップボードにコピーします。
- **ローカル管理**: すべてのデータはローカル（`~/MessengerCases`）に保存され、外部に送信されません。

## インストール

1. リポジトリをダウンロード:
   ```bash
   git clone https://github.com/yamaizumiminoru/InterAI-messenger.git
   ```
2. 依存ライブラリをインストール:
   ```bash
   cd InterAI-messenger
   pip install -r backend/requirements.txt
   ```

## 使い方

### 1. 起動
以下のスクリプトを実行してください:
- **Windows**: `start_messenger.bat` をダブルクリック

またはターミナルから:
```bash
cd backend
python main.py
```
ブラウザで [http://127.0.0.1:8000](http://127.0.0.1:8000) を開きます。

### 2. 基本操作（ホットキー）

| ホットキー | 動作 | 用途 |
| :--- | :--- | :--- |
| **`Ctrl` + `Shift` + `1`** | **撮影・作成** | アクティブな画面を撮影し、新しい案件フォルダを作成します。 |
| **`Ctrl` + `Shift` + `2`** | **メモ保存** | クリップボードの内容（コードやエラー）をログに追記します。 |
| **`Ctrl` + `Shift` + `3`** | **生成・コピー** | スクショとログを統合した指示書を作成し、**クリップボードにコピー**します。 |

### 3. AIに相談
Gemini や ChatGPT の入力欄で貼り付け（`Ctrl+V`）を行うだけで、状況を説明するプロンプトが入力されます。

## License
MIT
