import streamlit as st
import requests

def check_account_status(url, platform):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        status_code = response.status_code
        content = response.text.lower()

        if status_code == 404:
            return "❌ غير موجود"
        
        if platform == "Reddit":
            if "page not found" in content or "nobody on reddit goes by that name" in content:
                return "❌ غير موجود"
            return "✅ نشط"

        elif platform == "Twitter":
            if "account suspended" in content:
                return "⚠️ موقوف"
            elif "this account doesn’t exist" in content or "page doesn’t exist" in content:
                return "❌ غير موجود"
            return "✅ نشط"

        elif platform == "TikTok":
            if "couldn’t find this account" in content or "user not found" in content:
                return "❌ غير موجود"
            elif "no content" in content:
                return "⚠️ قد يكون موقوف"
            return "✅ نشط"

        else:
            return "❓ غير مدعوم بعد"

    except requests.RequestException as e:
        return f"❌ خطأ في الاتصال: {e}"

# Streamlit UI
st.set_page_config(page_title="🔍 فحص حالة الحسابات", layout="centered")
st.title("🔍 فحص حالة الحسابات")
st.write("أدخل رابط الحساب واختر المنصة لمعرفة حالته (بدون استخدام Selenium).")

platform = st.selectbox("اختر المنصة:", ["Reddit", "Twitter", "TikTok"])
url = st.text_input("رابط الحساب")

if st.button("فحص الحالة"):
    if url and platform:
        with st.spinner("جاري الفحص..."):
            result = check_account_status(url, platform)
            st.success(f"حالة الحساب: {result}")
    else:
        st.warning("يرجى إدخال الرابط واختيار المنصة أولاً.")
