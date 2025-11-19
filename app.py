import streamlit as st
import google.generativeai as genai

# --- 页面配置 ---
st.set_page_config(page_title="Walker Lingo", page_icon="🇺🇸", layout="wide")

# --- 侧边栏：设置区 ---
with st.sidebar:
    st.header("🔑 设置 (Settings)")
    st.info("请在下方输入你的 Google API Key")
    api_key = st.text_input("Gemini API Key", type="password", help="去 aistudio.google.com 申请")
    
    st.markdown("---")
    st.markdown("### Denise's Profile")
    st.caption("Owner: Walkerfit & Hifiwalker")
    st.caption("Goal: US Expansion & IELTS 7.0")

# --- 主程序 ---
st.title("🇺🇸 Walker Lingo")
st.subheader("Your Pocket AI English Coach")

if not api_key:
    st.warning("⬅️ 请先在左侧侧边栏输入 API Key 才能开始使用。")
    st.markdown("""
    **如何获取 Key?**
    1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. 登录 Google 账号
    3. 点击 'Create API key'
    4. 复制那一长串字符粘贴到左边。
    """)
    st.stop()

# 配置模型 (增加自动重试机制)
try:
    genai.configure(api_key=api_key)
    # 优先尝试 Flash 模型 (快且免费)，如果不行会自动报错提示
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Key 配置出错: {e}")
    st.stop()

# --- 功能区 ---
tab1, tab2 = st.tabs(["📖 单词深度析 (Word Analysis)", "🗣️ 场景模拟 (Roleplay)"])

# === 功能 1: 查词 ===
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        word = st.text_input("输入你想查询的单词/短语 (Enter Word):", placeholder="e.g., profit margin, kick off, leverage")
    with col2:
        st.write("") # 占位
        analyze_btn = st.button("Analyze 🚀", use_container_width=True)

    if analyze_btn and word:
        with st.spinner(f"Thinking about '{word}'..."):
            try:
                prompt = f"""
                Role: Professional English Coach for a Business Owner (Denise).
                Target: IELTS Band 7.0 + US Business Context.
                Word: "{word}"
                
                Please generate a Markdown response with these sections:
                1. **Definition**: Simple English definition & Chinese meaning.
                2. **🔊 Pronunciation**: IPA & tip for Chinese speakers.
                3. **⚖️ Vibe Check**: Formal/Casual? Positive/Negative?
                4. **💼 Business Context (For Walkerfit/Hifiwalker)**:
                   - A sentence for **External Email** (to buyers/partners).
                   - A sentence for **Internal Management** (to staff).
                5. **🎓 IELTS Speaking (Band 7.0)**:
                   - A sophisticated sentence using this word.
                """
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"请求失败，请检查网络或 Key。错误信息: {e}")

# === 功能 2: 对话模拟 ===
with tab2:
    st.markdown("**Practice Real Situations**")
    topic = st.selectbox("选择当前练习场景:", 
        ["Business: Negotiating Price with Supplier", 
         "Business: Explaining Product Delay", 
         "IELTS: Speaking Part 2 (Describe a tech product)", 
         "Daily: Small Talk with US Neighbor"])

    # 聊天记录管理
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = topic
    
    # 切换场景清空历史
    if st.session_state.current_topic != topic:
        st.session_state.messages = []
        st.session_state.current_topic = topic
        st.rerun()

    # 清空按钮
    if st.button("Restart Conversation 🔄"):
        st.session_state.messages = []
        st.rerun()

    # 显示聊天历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    if user_input := st.chat_input("Type your reply here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Writing..."):
                try:
                    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                    prompt = f"""
                    Scene: {topic}.
                    User (Denise) said: "{user_input}"
                    Conversation History:
                    {history_text}
                    
                    Task:
                    1. Reply naturally as the other person in this scene. Keep it concise.
                    2. **CRITICAL**: At the very end, strictly check Denise's grammar.
                       If she made a mistake, add a specific section:
                       > **📝 Correction**: [Your correction here]
                       > **✨ Better Way (Native/Band 7)**: [Polished version]
                    """
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
