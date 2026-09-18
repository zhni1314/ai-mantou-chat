# AI智能馒头 - AI 伴侣聊天应用

基于 Streamlit + DeepSeek 的聊天应用，支持角色设定（昵称/性格）、流式回复、会话保存与历史管理。

## 运行

```bash
pip install -r requirements.txt

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY = "你的DeepSeek API Key"
streamlit run mantou_chat.py

# macOS / Linux
export DEEPSEEK_API_KEY="你的DeepSeek API Key"
streamlit run mantou_chat.py