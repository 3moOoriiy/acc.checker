import streamlit as st
import requests
import re

def check_account_status(url, platform):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
    }

    try:
        # تنظيف الرابط
        url = re.sub(r'https?://(www\.)?', 'https://', url.strip())
        if not url.startswith('https://'):
            url = f'https://{url}'

        response = requests.get(url, headers=headers, timeout=15)
        content = response.text.lower()

        if platform == "تويتر/إكس":
            suspended_patterns = [
                r'account[\s_]*suspended',
                r'x[\s_]*suspends[\s_]*accounts',
                r'حساب[\s_]*موقوف',
                r'تم[\s_]*تعليق[\s_]*الحساب',
                r'account_status[":\s]+suspended',
                r'suspendedaccount',
                r'تعليق[\s_]*الحساب'
            ]

            if any(re.search(pattern, content) for pattern in suspended_patterns):
                return "⚠️ الحساب موقوف"
            
            if re.search(r'this[\s_]*account[\s_]*doesn[\'’]t[\s_]*exist', content):
                return "❌ الحساب غير موجود"
                
            return "✅ الحساب نشط"

    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# تطبيق واجهة Streamlit
st.set_page_config(
    page_title="أداة فحص الحسابات",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS مخصص
st.markdown("""
<style>
    .stTextInput input, .stSelectbox select {
        padding: 10px !important;
        border-radius: 5px !important;
    }
    .stButton button {
        width: 100%;
        padding: 12px;
        background-color: #1DA1F2;
        color: white;
        border: none;
        border-radius: 5px;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# واجهة المستخدم
st.title("🔍 فحص حالة الحسابات")
st.write("أدخل رابط الحساب للتحقق من حالته")

platform = st.selectbox("اختر المنصة:", ["تويتر/إكس"])
url = st.text_input("رابط الحساب", placeholder="https://x.com/اسم_المستخدم")

if st.button("فحص الحالة"):
    if url:
        with st.spinner("جاري التحقق..."):
            result = check_account_status(url, platform)
            
            if "موقوف" in result:
                st.error(result)
            elif "غير موجود" in result:
                st.warning(result)
            else:
                st.success(result)
    else:
        st.warning("الرجاء إدخال رابط الحساب")
