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
        
        response = requests.get(url, headers=headers, timeout=15)
        content = response.text

        # أنماط الكشف عن الحسابات الموقوفة (محدثة)
        suspension_patterns = [
            r'<div[^>]*class="[^"]*css-175oi2r[^"]*"[^>]*>.*?Account suspended.*?</div>',
            r'X suspends accounts which violate',
            r'data-testid="empty_state_header_text"[^>]*>.*?Account suspended',
            r'<div[^>]*class="css-146c3p1[^"]*"[^>]*>.*?Account suspended',
            r'حساب موقوف',
            r'تم تعليق الحساب',
            r'account_status":"suspended"'
        ]

        # التحقق من وجود أي نمط تعليق
        for pattern in suspension_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return {
                    "status": "موقوف",
                    "icon": "⚠️",
                    "reason": "الحساب مخالف لشروط إكس",
                    "details": "تم تعليق الحساب بواسطة المنصة",
                    "color": "#ff4b4b",
                    "snippet": re.search(pattern, content, re.IGNORECASE | re.DOTALL).group(0)[:200] + "..."
                }

        # التحقق من الحسابات المحذوفة
        if re.search(r'this account doesn[\'’]t exist|الحساب غير موجود', content, re.IGNORECASE):
            return {
                "status": "غير موجود",
                "icon": "❌",
                "reason": "الحساب محذوف أو غير صحيح",
                "details": "الرجاء التأكد من اسم المستخدم",
                "color": "#ffa500"
            }

        # إذا كان الحساب نشطاً
        return {
            "status": "نشط",
            "icon": "✅",
            "reason": "الحساب يعمل بشكل طبيعي",
            "details": "يمكن الوصول إلى المحتوى",
            "color": "#2ecc71"
        }

    except Exception as e:
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": str(e),
            "details": "حدث خطأ أثناء الفحص",
            "color": "#95a5a6"
        }

# واجهة المستخدم
st.set_page_config(
    page_title="أداة فحص حسابات إكس الدقيقة",
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
        margin-top: 10px !important;
    }
    .result-card {
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        border-left: 5px solid;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 أداة فحص حسابات إكس الدقيقة")

# إدخال البيانات
url = st.text_input("أدخل رابط الحساب", placeholder="https://x.com/اسم_المستخدم")

if st.button("فحص دقيق"):
    if url:
        with st.spinner("جاري التحقق بعمق..."):
            result = check_twitter_account(url)
            
            # عرض النتائج
            st.markdown(f"""
            <div class="result-card" style="border-color: {result['color']}; background-color: {result['color']}10;">
                <h3 style="color: {result['color']}; margin-top: 0;">{result['icon']} الحالة: {result['status']}</h3>
                <p><strong>السبب:</strong> {result['reason']}</p>
                <p><strong>التفاصيل:</strong> {result['details']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # عرض مقتطف HTML للحسابات الموقوفة
            if result['status'] == "موقوف":
                with st.expander("مقتطف من كود الصفحة (للتأكد)"):
                    st.code(result['snippet'])
                
            # تأثيرات بصرية
            if result['status'] == "نشط":
                st.balloons()
            elif result['status'] == "موقوف":
                st.error("للمساعدة: يمكنك تقديم استئناف عبر مركز مساعدة إكس")
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("🔄 تم التحديث ليدعم الهيكل الجديد لصفحات إكس - يوليو 2024")
