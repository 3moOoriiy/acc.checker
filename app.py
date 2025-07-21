import streamlit as st
import requests
import re

def check_twitter_account(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
        }
        
        # تنظيف الرابط
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text.lower()

        # قائمة بأنماط التعليق المحتملة (تم تحديثها)
        suspension_patterns = [
            r'account[\s_]*suspended',
            r'x[\s_]*suspends[\s_]*accounts',
            r'حساب[\s_]*موقوف',
            r'تم[\s_]*تعليق[\s_]*الحساب',
            r'account_status":"suspended',
            r'this[\s_]*account[\s_]*is[\s_]*suspended',
            r'<title>[^<]*suspended[^<]*</title>',
            r'<meta[^>]*suspended[^>]*>',
            r'content=["\']حساب موقوف["\']'
        ]

        # التحقق من وجود أي نمط من أنماط التعليق
        if any(re.search(pattern, content) for pattern in suspension_patterns):
            return "⚠️ الحساب موقوف (معلق رسمياً)"
        
        # التحقق من الحسابات المحذوفة
        if re.search(r'this[\s_]*account[\s_]*doesn[\'’]t[\s_]*exist|الحساب[\s_]*غير[\s_]*موجود', content):
            return "❌ الحساب غير موجود أو محذوف"
        
        # إذا مرت جميع الفحوصات
        return "✅ الحساب نشط وقابل للاستخدام"

    except requests.exceptions.RequestException as e:
        return f"❌ خطأ في الاتصال: {str(e)}"

# واجهة المستخدم العربية
st.set_page_config(
    page_title="أداة فحص الحسابات الدقيقة",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تنسيق عربي مع تصميم جذاب
st.markdown("""
<style>
    .reportview-container {
        direction: rtl;
        text-align: right;
    }
    .stTextInput input, .stSelectbox select {
        padding: 12px !important;
        border: 2px solid #1DA1F2 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    .stButton button {
        background-color: #1DA1F2 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 14px 24px !important;
        border-radius: 8px !important;
        width: 100% !important;
        font-size: 18px !important;
    }
    .success-msg {
        color: #28a745;
        font-size: 20px;
        font-weight: bold;
    }
    .error-msg {
        color: #dc3545;
        font-size: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# عنوان التطبيق
st.markdown("<h1 style='text-align: center; color: #1DA1F2;'>🔍 أداة فحص حسابات تويتر/إكس</h1>", unsafe_allow_html=True)

# إدخال البيانات
st.markdown("### ⚙️ إعدادات الفحص")
account_url = st.text_input("**رابط الحساب**", placeholder="https://x.com/اسم_المستخدم")

# زر الفحص
if st.button("**بدء الفحص الدقيق**", type="primary"):
    if account_url:
        with st.spinner("جاري التحقق بعمق، الرجاء الانتظار..."):
            result = check_twitter_account(account_url)
            
            if "موقوف" in result:
                st.markdown(f"<div class='error-msg'>{result}</div>", unsafe_allow_html=True)
                st.warning("💡 يمكنك تقديم استئناف إذا كان هذا خطأ")
            elif "غير موجود" in result:
                st.markdown(f"<div class='error-msg'>{result}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='success-msg'>{result}</div>", unsafe_allow_html=True)
                st.balloons()
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

# معلومات إضافية
st.markdown("---")
st.markdown("""
**ℹ️ ملاحظات مهمة:**
1. الأداة تعتمد على آخر تحديث لمنصة إكس (2024)
2. بعض الحسابات الموقوفة مؤقتاً قد لا تظهر مباشرة
3. للنتائج الأكثر دقة، تأكد من كتابة الرابط بشكل صحيح
""")

st.caption("آخر تحديث: ١٠ يونيو ٢٠٢٤ - إصدار 2.1.0")
