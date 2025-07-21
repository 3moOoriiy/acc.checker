import streamlit as st
import requests

def التحقق_من_حالة_الحساب(رابط, المنصة):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(رابط, headers=headers, timeout=10)
        status_code = response.status_code
        content = response.text.lower()

        if status_code == 404:
            return "❌ الحساب غير موجود"
        
        if المنصة == "ريديت":
            if "page not found" in content or "nobody on reddit goes by that name" in content:
                return "❌ الحساب غير موجود"
            return "✅ الحساب نشط"

        elif المنصة == "تويتر/إكس":
            if "account suspended" in content or "x suspends accounts" in content or "تم تعليق الحساب" in content:
                return "⚠️ الحساب موقوف"
            elif "this account doesn't exist" in content or "page doesn't exist" in content:
                return "❌ الحساب غير موجود"
            return "✅ الحساب نشط"

        elif المنصة == "تيك توك":
            if "couldn't find this account" in content or "user not found" in content:
                return "❌ الحساب غير موجود"
            elif "no content" in content:
                return "⚠️ الحساب قد يكون موقوفًا"
            return "✅ الحساب نشط"

        else:
            return "❓ المنصة غير مدعومة بعد"

    except requests.RequestException as e:
        return f"❌ خطأ في الاتصال: {e}"

# واجهة المستخدم
st.set_page_config(page_title="🔍 فحص حالة الحسابات", layout="centered")
st.title("🔍 فحص حالة الحسابات")
st.write("أدخل رابط الحساب واختر المنصة للتحقق من حالته (بدون استخدام Selenium).")

المنصة = st.selectbox("اختر المنصة:", ["تويتر/إكس", "ريديت", "تيك توك"])
رابط = st.text_input("رابط الحساب")

if st.button("فحص الحالة"):
    if رابط and المنصة:
        with st.spinner("جاري التحقق..."):
            النتيجة = التحقق_من_حالة_الحساب(رابط, المنصة)
            st.success(f"حالة الحساب: {النتيجة}")
    else:
        st.warning("الرجاء إدخال رابط الحساب واختيار المنصة أولاً")
