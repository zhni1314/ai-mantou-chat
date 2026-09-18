"""AI智能馒头 - 基于 Streamlit + DeepSeek 的 AI 伴侣聊天应用

运行方式:
    streamlit run mantou_chat.py

依赖环境变量:
    DEEPSEEK_API_KEY  DeepSeek 平台的 API Key
"""

import base64
import datetime
import json
import os
import traceback

import streamlit as st
from openai import OpenAI

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(APP_DIR, "session")


def save_session():
    """将当前会话保存到 session 目录"""
    if not st.session_state.current_session:
        return
    session_data = {
        "nick_name": st.session_state.nick_name,
        "nature": st.session_state.nature,
        "messages": st.session_state.messages,
        "current_session": st.session_state.current_session,
    }
    os.makedirs(SESSION_DIR, exist_ok=True)
    with open(os.path.join(SESSION_DIR, f"{st.session_state.current_session}.json"), "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)


def create_session():
    """新建对话：先保存旧会话，再重置状态"""
    if st.button("新建对话", width="stretch", icon="🔄"):
        if st.session_state.messages:
            save_session()
            st.session_state.messages = []
            st.session_state.current_session = datetime.datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
            st.rerun()


def load_sessions():
    """列出所有已保存的会话 ID"""
    session_list = []
    if os.path.exists(SESSION_DIR):
        for filename in os.listdir(SESSION_DIR):
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    return session_list


def load_session(session_id):
    """加载指定会话并恢复状态"""
    session_path = os.path.join(SESSION_DIR, f"{session_id}.json")
    if os.path.exists(session_path):
        with open(session_path, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        st.session_state.nick_name = session_data.get("nick_name", "小馒头")
        st.session_state.nature = session_data.get("nature", "活泼开朗的浙江姑娘")
        st.session_state.messages = session_data.get("messages", [])
        st.session_state.current_session = session_id
        st.rerun()


def delete_session(session_id):
    """删除指定会话文件"""
    session_path = os.path.join(SESSION_DIR, f"{session_id}.json")
    if os.path.exists(session_path):
        os.remove(session_path)
        if st.session_state.current_session == session_id:
            st.session_state.messages = []
            st.session_state.current_session = datetime.datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
        st.rerun()


def image_to_data_uri(image_path):
    """读取图片文件并返回 base64 数据 URI"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_data = f.read()
        base64_str = base64.b64encode(image_data).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_str}"
    return ""


st.set_page_config(
    page_title="AI智能馒头",
    page_icon=os.path.join(APP_DIR, "assets", "mantou.jpg"),
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# 注入自定义 CSS：背景图 + 黑白灰主题
bg_image_uri = image_to_data_uri(os.path.join(APP_DIR, "assets", "background.jpg"))

st.markdown(
    f"""
<style>
.stApp {{
    background-image: url("{bg_image_uri}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

/* 侧边栏 */
[data-testid="stSidebar"] {{
    background-color: #ffffff;
    border-right: 1px solid #e5e5e5;
}}

[data-testid="stSidebar"] .stSidebarContent {{
    padding: 1.5rem 1rem;
}}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: #000000 !important;
    font-weight: 600 !important;
}}

[data-testid="stSidebar"] .stText,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {{
    color: #333333 !important;
    font-size: 14px !important;
}}

[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {{
    background-color: #f5f5f5 !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
    color: #000000 !important;
    font-size: 14px !important;
    padding: 10px 12px !important;
}}

[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stTextArea textarea:focus {{
    border-color: #666666 !important;
    box-shadow: none !important;
    background-color: #ffffff !important;
}}

[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {{
    color: #aaaaaa !important;
}}

[data-testid="stSidebar"] hr {{
    border-color: #eeeeee !important;
    margin: 1.5rem 0 !important;
}}

/* 按钮 */
[data-testid="stSidebar"] .stButton button {{
    background-color: #000000 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: opacity 0.2s !important;
    width: 100% !important;
}}

[data-testid="stSidebar"] .stButton button:hover {{
    opacity: 0.8 !important;
}}

[data-testid="stSidebar"] .stButton button:active {{
    opacity: 0.7 !important;
}}

[data-testid="stSidebar"] .stButton button[kind="secondary"] {{
    background-color: #f5f5f5 !important;
    color: #333333 !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    padding: 6px 12px !important;
    text-align: left !important;
}}

[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {{
    background-color: #e8e8e8 !important;
    border-color: #cccccc !important;
}}

[data-testid="stSidebar"] .stButton button:has(span:only-child) {{
    background: none !important;
    border: none !important;
    color: #999999 !important;
    padding: 4px !important;
    min-width: unset !important;
    font-size: 14px !important;
}}

[data-testid="stSidebar"] .stButton button:has(span:only-child):hover {{
    color: #ff4444 !important;
}}

/* 聊天气泡 */
[data-testid="stChatMessage"] {{
    background-color: #ffffff;
    border-radius: 12px;
    padding: 4px 0;
}}

[data-testid="stChatMessage"][data-testid="stChatMessage"]:has([data-testid="user"]) {{
    background-color: transparent;
}}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {{
    color: #000000 !important;
}}

/* 底部输入框 */
[data-testid="stChatInput"] {{
    background-color: #ffffff !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    padding: 4px 4px 4px 16px !important;
}}

[data-testid="stChatInput"] textarea {{
    background-color: #ffffff !important;
    color: #000000 !important;
    font-size: 16px !important;
    caret-color: #000000 !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: #aaaaaa !important;
}}

[data-testid="stChatInput"]:focus-within {{
    border: none !important;
    box-shadow: none !important;
}}

[data-testid="stChatInput"] button {{
    background-color: #ffffff !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 4px 16px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}}

[data-testid="stChatInput"] button:hover {{
    background-color: #f5f5f5 !important;
}}

/* 全局文字 */
h1, h2, h3 {{
    color: #000000;
    font-weight: 600;
}}

p, span, div {{
    color: #333333;
}}
</style>
""",
    unsafe_allow_html=True,
)

st.title("AI智能馒头")
st.logo(os.path.join(APP_DIR, "assets", "mantou.jpg"))

# 会话状态初始化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小馒头"
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的浙江姑娘"
if "current_session" not in st.session_state:
    st.session_state.current_session = datetime.datetime.now().strftime("%Y_%m_%d_%H-%M-%S")

# 渲染历史消息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

SYSTEM_PROMPT = """
            你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。:
            规则:
            1.每次只回1条消息
            2.禁止任何场景或状态描述性文字
            3.匹配用户的语言
            4.回复简短，像微信聊天一样
            5.有需要的话可以用等emoji表情
            6.用符合伴侣性格的方式对话
            7.回复的内容，要充分体现伴侣的性格特征伴侣性格:
            - %s你必须严格遵守上述规则来回复用户。
            """

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    st.error("未检测到 DEEPSEEK_API_KEY，请在环境变量中配置后再运行。")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

# 侧边栏：控制面板与会话历史
with st.sidebar:
    st.subheader("ai控制面板")
    create_session()

    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

    st.divider()
    st.text("会话历史")
    for session in load_sessions():
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(session, width="stretch", icon="🔄", key=f"load_{session}"):
                load_session(session)
        with col2:
            if st.button("", width="stretch", icon="❌", key=f"delete_{session}"):
                delete_session(session)

# 聊天输入与流式响应
prompt = st.chat_input("请输入您要问的问题：")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # 已修正为官方模型名
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT % (st.session_state.nick_name, st.session_state.nature)},
                *st.session_state.messages,
            ],
            stream=True,
        )

        message_placeholder = st.chat_message("assistant").empty()
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.write(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"错误：{e}")
        st.code(traceback.format_exc())