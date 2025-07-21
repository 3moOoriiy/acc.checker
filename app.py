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
        content = response.text

        # التحقق من التعليق
        suspension_pattern = re.compile(
            r'<div[^>]*class="[^"]*css-175oi2r[^"]*"[^>]*>.*?Account suspended.*?X suspends accounts',
            re.IGNORECASE | re.DOTALL
        )
        
        if suspension_pattern.search(content):
            return {
                "status": "موقوف",
                "icon": "⚠️",
                "reason": "الحساب مخالف لشروط استخدام المنصة",
                "details": "تم تعليق الحساب بواسطة إكس بسبب انتهاك القواعد",
                "color": "red"
            }

        # التحقق من الحسابات المحذوفة
        if re.search(r'this account doesn[\'’]t exist|الحساب غير موجود', content, re.IGNORECASE):
            return {
                "status": "غير موجود",
                "icon": "❌",
                "reason": "الحساب محذوف أو الرابط خاطئ",
                "details": "الرجاء التأكد من اسم المستخدم",
                "color": "orange"
            }

        # إذا كان الحساب نشطاً
        return {
            "status": "نشط",
            "icon": "✅",
            "reason": "الحساب يعمل بشكل طبيعي",
            "details": "يمكن الوصول إلى الحساب ومشاهدة المحتوى",
            "color": "green"
        }

    except Exception as e:
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": str(e),
            "details": "حدث خطأ أثناء محاولة التحقق",
            "color": "gray"
        }

# واجهة المستخدم
st.set_page_config(
    page_title="أداة فحص حسابات تويتر/إكس الدقيقة",
    layout="centered"
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
</style>
""", unsafe_allow_html=True)

st.title("🔍 أداة فحص حسابات تويتر/إكس")

# إدخال البيانات
url = st.text_input("أدخل رابط الحساب", placeholder="https://x.com/اسم_المستخدم")

if st.button("فحص الحساب"):
    if url:
        with st.spinner("جاري التحقق من حالة الحساب..."):
            result = check_twitter_account(url)
            
            # عرض النتائج في بطاقة منظمة
            st.markdown(f"""
            <div style="
                border: 2px solid {result['color']};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
            ">
                <h3>{result['icon']} الحالة: {result['status']}</h3>
                <p><strong>السبب:</strong> {result['reason']}</p>
                <p><strong>التفاصيل:</strong> {result['details']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # تأثيرات بصرية للحالات المختلفة
            if result['status'] == "نشط":
                st.balloons()
            elif result['status'] == "موقوف":
                st.error("للمساعدة: يمكنك تقديم استئناف عبر مركز مساعدة إكس")
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("آخر تحديث: يوليو 2024 - إصدار 2.5.0")
