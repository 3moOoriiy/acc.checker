import streamlit as st
import requests
import re

def check_account_status(url):
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
        content = response.text

        # تحليل محتوى الصفحة للكشف عن التعليق
        suspension_patterns = [
            r'<div[^>]*class="[^"]*css-175oi2r[^"]*"[^>]*>.*?<div[^>]*dir="ltr"[^>]*class="[^"]*css-146c3p1[^"]*"[^>]*>.*?Account suspended.*?</div>',
            r'X suspends accounts which violate',
            r'<div[^>]*data-testid="empty_state_header_text"[^>]*>.*?Account suspended.*?</div>',
            r'account_status":"suspended',
            r'حساب موقوف',
            r'تم تعليق الحساب'
        ]

        for pattern in suspension_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return {
                    "status": "موقوف",
                    "reason": "الحساب مخالف لشروط استخدام تويتر/إكس",
                    "details": "تم تعليق الحساب بواسطة المنصة بسبب انتهاك القواعد",
                    "html_snippet": re.search(pattern, content, re.IGNORECASE | re.DOTALL).group(0)[:200] + "..."
                }

        # التحقق من الحسابات المحذوفة
        if re.search(r'this account doesn[\'’]t exist|الحساب غير موجود', content, re.IGNORECASE):
            return {
                "status": "غير موجود",
                "reason": "الحساب محذوف أو غير موجود",
                "details": "لم يتم العثور على الحساب المطلوب"
            }

        # إذا كان الحساب نشطاً
        return {
            "status": "نشط",
            "reason": "الحساب يعمل بشكل طبيعي",
            "details": "يمكن الوصول إلى الحساب ومشاهدة المحتوى"
        }

    except Exception as e:
        return {
            "status": "خطأ",
            "reason": str(e),
            "details": "حدث خطأ أثناء محاولة التحقق من الحساب"
        }

# واجهة المستخدم
st.set_page_config(
    page_title="أداة فحص حسابات تويتر/إكس",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تنسيق عربي
st.markdown("""
<style>
    .reportview-container {
        direction: rtl;
        text-align: right;
    }
    .stTextInput input {
        padding: 12px !important;
        border: 2px solid #1DA1F2 !important;
        border-radius: 8px !important;
    }
    .stButton button {
        background-color: #1DA1F2 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 14px !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    .suspended { color: #dc3545; font-weight: bold; }
    .active { color: #28a745; font-weight: bold; }
    .not-found { color: #ffc107; font-weight: bold; }
    .error { color: #6c757d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🔍 أداة فحص حسابات تويتر/إكس")

url = st.text_input("أدخل رابط الحساب", placeholder="https://x.com/اسم_المستخدم")

if st.button("فحص الحساب"):
    if url:
        with st.spinner("جاري التحقق من حالة الحساب..."):
            result = check_account_status(url)
            
            if result["status"] == "موقوف":
                st.markdown(f"<p class='suspended'>الحالة: ⚠️ {result['status']}</p>", unsafe_allow_html=True)
                st.write(f"السبب: {result['reason']}")
                st.write(f"التفاصيل: {result['details']}")
                with st.expander("مقتطف من كود الصفحة"):
                    st.code(result['html_snippet'])
                
            elif result["status"] == "غير موجود":
                st.markdown(f"<p class='not-found'>الحالة: ❌ {result['status']}</p>", unsafe_allow_html=True)
                st.write(f"السبب: {result['reason']}")
                
            elif result["status"] == "نشط":
                st.markdown(f"<p class='active'>الحالة: ✅ {result['status']}</p>", unsafe_allow_html=True)
                st.write(f"التفاصيل: {result['details']}")
                
            else:
                st.markdown(f"<p class='error'>الحالة: ❗ {result['status']}</p>", unsafe_allow_html=True)
                st.write(f"الخطأ: {result['reason']}")
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("ℹ️ هذه الأداة تفحص الحسابات بناءً على هيكل صفحة تويتر/إكس. آخر تحديث: يوليو 2024")
