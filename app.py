import hmac
import os

import streamlit as st
import google.generativeai as genai

# --- 页面配置 ---
st.set_page_config(page_title="Walker Lingo", page_icon="🇺🇸", layout="wide")


def verify_login(username: str, password: str) -> bool:
    if not username or not password:
        return False
    default_user = os.getenv("WALKER_LINGO_USER", "admin")
    default_pass = os.getenv("WALKER_LINGO_PASS", "WalkerLingo2024!")
    return hmac.compare_digest(username, default_user) and hmac.compare_digest(
        password, default_pass
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 菜单")
        st.text_input("搜索模块", placeholder="搜索...")
        st.markdown("---")

        menu_sections = {
            "销售管理": [
                "导航看板",
                "任务管理",
                "提交新任务",
                "任务列表",
                "任务日程",
                "任务详情",
                "提醒提交任务",
                "定时任务",
                "周报",
            ],
            "产品中心": ["产品报表", "产品报价", "产品优化"],
            "Amazon管理": ["Amazon销售概要", "销售目标管理", "Listing优化", "Amazon订单管理"],
            "TikTok管理": [
                "TikTok销售统计",
                "TikTok推广后台",
                "视频群管理",
                "达人作品管理",
                "采集达人",
                "达人查询",
                "TikTok SKU映射",
                "旗舰产品推荐",
                "TikTok订单管理",
                "达人投顾后台",
                "淘搜任务板",
            ],
            "创作中心": ["AI图片工厂", "内容管理"],
            "产品管理": [
                "供应商管理",
                "采购需求单",
                "生成采购单",
                "采购管理",
                "入库审核",
                "入库管理",
                "出货管理",
                "货物管理",
                "库存查询",
                "库存盘点",
                "库存预警",
            ],
            "财务": ["提交报销凭证", "报销报表", "付款审核", "报销统计", "会计凭证"],
            "行政人事": ["职位申请表", "入职登记", "员工管理", "用户设置"],
        }

        for section, items in menu_sections.items():
            with st.expander(section, expanded=False):
                for item in items:
                    st.caption(f"• {item}")

        st.markdown("---")
        st.caption("系统")
        if st.button("退出登录"):
            st.session_state.authenticated = False
            st.rerun()


def render_login() -> None:
    st.markdown("## 欢迎使用 Walker Lingo 控制台")
    st.caption("请登录以继续访问系统。")
    with st.form("login_form"):
        username = st.text_input("用户名", placeholder="请输入账号")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        submit = st.form_submit_button("登录")
    if submit:
        if verify_login(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("登录成功，正在进入系统...")
            st.rerun()
        else:
            st.error("用户名或密码错误，请重试。")


def ensure_auth() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

# --- 侧边栏：设置区 ---
if not ensure_auth():
    render_login()
    st.stop()

render_sidebar()

st.sidebar.header("🔑 设置 (Settings)")
st.sidebar.info("请在下方输入你的 Google API Key")
api_key = st.sidebar.text_input(
    "Gemini API Key", type="password", help="去 aistudio.google.com 申请"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Denise's Profile")
st.sidebar.caption("Owner: Walkerfit & Hifiwalker")
st.sidebar.caption("Goal: US Expansion & IELTS 7.0")

# --- 主程序 ---
st.title("🇺🇸 Walker Lingo 控制台")
st.subheader(f"欢迎回来，{st.session_state.get('username', '用户')}")

st.markdown(
    """
    <div style="padding: 16px; border-radius: 12px; background: #F7F8FA; margin-bottom: 16px;">
        <strong>今日概览</strong>
        <ul style="margin: 8px 0 0 16px;">
            <li>待处理任务：8</li>
            <li>待提交内容：3</li>
            <li>待跟进客户：5</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

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
