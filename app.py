import streamlit as st
import requests
import re

def التحقق_من_حالة_الحساب(رابط, المنصة):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
    }

    try:
        # تنظيف الرابط والتأكد من صحته
        رابط = re.sub(r'https?://(www\.)?', 'https://', رابط.strip())
        if not رابط.startswith('https://'):
            رابط = f'https://{رابط}'

        response = requests.get(رابط, headers=headers, timeout=15)
        content = response.text.lower()

        if المنصة == "تويتر/إكس":
            # علامات التعليق الأكثر دقة (تم تحديثها)
            علامات_التعليق = [
                r'account[\s_]*suspended',
                r'x[\s_]*suspends[\s_]*accounts',
                r'حساب[\s_]*موقوف',
                r'تم[\s_]*تعليق[\s_]*الحساب',
                r'account_status[":\s]+suspended',
                r'suspendedaccount',
                r'تعليق[\s_]*الحساب',
                r'<title>حساب موقوف</title>',
                r'content="حساب موقوف"',
                r'حسابك مغلق'
            ]

            if any(re.search(pattern, content) for pattern in علامات_التعليق):
                return "⚠️ الحساب موقوف (معلق)"
            
            # تحسين اكتشاف الحسابات المحذوفة
            if re.search(r'this[\s_]*account[\s_]*doesn[\'’]t[\s_]*exist|page[\s_]*doesn[\'’]t[\s_]*exist|الحساب[\s_]*غير[\s_]*موجود', content):
                return "❌ الحساب غير موجود أو محذوف"
            
            # إذا لم يكن هناك محتوى للمستخدم
            if re.search(r'no[\s_]*tweets[\s_]*yet|لا[\s_]*يوجد[\s_]*محتوى|هذا[\s_]*المستخدم[\s_]*ليس[\s_]*لديه[\s_]*تغريدات', content):
                return "⚠️ الحساب فارغ (قد يكون جديدًا أو موقوفًا)"
            
            return "✅ الحساب نشط (العمليات فقط)"

    except requests.RequestException as e:
        return f"❌ خطأ في الاتصال: {str(e)}"

# واجهة المستخدم المحسنة
st.set_page_config(page_title="🔍 فحص حالة الحسابات - النسخة النهائية", layout="centered")
st.title("🔍 فحص حالة الحسابات بدقة عالية")

with st.expander("تعليمات الاستخدام"):
    st.write("""
    1. اختر المنصة المطلوبة (تويتر/إكس)
    2. أدخل رابط الحساب بشكل صحيح
    3. اضغط على زر الفحص الدقيق
    4. انتظر حتى تظهر النتيجة
    """)

المنصة = st.selectbox("اختر المنصة:", ["تويتر/إكس"])
رابط = st.text_input("رابط الحساب", placeholder="https://x.com/اسم_المستخدم", help="أدخل الرابط كاملاً مثل: https://x.com/mohamed_ali")

if st.button("فحص دقيق", type="primary"):
    if رابط:
        with st.spinner("جاري الفحص بعمق، الرجاء الانتظار..."):
            النتيجة = التحقق_من_حالة_الحساب(رابط, المنصة)
            
            if "موقوف" in النتيجة:
                st.error(النتيجة)
                st.warning("ملاحظة: تم اكتشاف أن الحساب موقوف")
            elif "غير موجود" in النتيجة:
                st.warning(النتيجة)
            elif "فارغ" in النتيجة:
                st.info(النتيجة)
            else:
                st.success(النتيجة)
                st.info("العمليات فقط ✅")
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("ملاحظة: هذه الأداة توفر دقة عالية ولكنها لا تضمن 100% خاصة للحسابات المعلقة مؤقتًا")
