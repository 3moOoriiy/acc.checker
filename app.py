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
            # علامات التعليق الأكثر دقة
            علامات_التعليق = [
                r'account suspended',
                r'x suspends accounts',
                r'حساب موقوف',
                r'تم تعليق الحساب',
                r'account_status[":\s]+suspended',
                r'this account is suspended',
                r'suspendedaccount',
                r'تعليق_الحساب',
                r'<title>حساب موقوف</title>'
            ]

            if any(re.search(pattern, content) for pattern in علامات_التعليق):
                return "⚠️ الحساب موقوف (معلق)"
            
            # تحسين اكتشاف الحسابات المحذوفة
            if re.search(r'this account doesn[\'’]t exist|page doesn[\'’]t exist|الحساب غير موجود', content):
                return "❌ الحساب غير موجود أو محذوف"
            
            # إذا لم يكن هناك محتوى للمستخدم (علامة على تعليق الحساب)
            if re.search(r'no tweets yet|لا يوجد محتوى', content):
                return "⚠️ الحساب قد يكون موقوفًا أو جديدًا"
            
            return "✅ الحساب نشط"

        # باقي المنصات...
        
    except requests.RequestException as e:
        return f"❌ خطأ في الاتصال: {str(e)}"

# واجهة المستخدم
st.set_page_config(page_title="🔍 فحص حالة الحسابات - الإصدار المحسن", layout="centered")
st.title("🔍 فحص حالة الحسابات (الإصدار المحسن)")

with st.expander("تعليمات مهمة"):
    st.write("""
    - تأكد من كتابة رابط الحساب بشكل صحيح
    - للحسابات المعلقة، قد تحتاج إلى تحديث الصفحة عدة مرات
    - بعض الحسابات قد تظهر كنشطة رغم تعليقها مؤقتًا
    """)

المنصة = st.selectbox("اختر المنصة:", ["تويتر/إكس", "ريديت", "تيك توك"])
رابط = st.text_input("رابط الحساب", placeholder="https://x.com/username")

if st.button("فحص دقيق", type="primary"):
    if رابط:
        with st.spinner("جاري الفحص بعمق..."):
            النتيجة = التحقق_من_حالة_الحساب(رابط, المنصة)
            
            if "موقوف" in النتيجة:
                st.error(النتيجة)
            elif "غير موجود" in النتيجة:
                st.warning(النتيجة)
            else:
                st.success(النتيجة)
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("ملاحظة: هذه الأداة لا تضمن دقة 100%، خاصة للحسابات المعلقة مؤقتًا")
