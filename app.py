import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time

def check_account_status(url, platform):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)

        if platform == "Reddit":
            if "page not found" in driver.page_source.lower():
                return "❌ غير موجود أو محذوف"
            elif "sorry, nobody on reddit goes by that name" in driver.page_source.lower():
                return "❌ غير موجود"
            else:
                return "✅ نشط"

        elif platform == "Twitter":
            if "account suspended" in driver.page_source.lower():
                return "⚠️ موقوف"
            elif "this account doesn’t exist" in driver.page_source.lower():
                return "❌ غير موجود"
            else:
                return "✅ نشط"

        elif platform == "TikTok":
            if "couldn’t find this account" in driver.page_source.lower():
                return "❌ غير موجود"
            elif "no content" in driver.page_source.lower():
                return "⚠️ قد يكون موقوف"
            else:
                return "✅ نشط"

        else:
            return "❓ غير مدعوم بعد"

    except WebDriverException as e:
        return f"❌ خطأ في الاتصال: {e}"
    finally:
        driver.quit()

# Streamlit واجهة
st.title("🔍 فحص حالة الحسابات")
st.write("أدخل رابط الحساب واختر المنصة لمعرفة حالته.")

platform = st.selectbox("اختر المنصة:", ["Reddit", "Twitter", "TikTok"])  # أضف لاحقًا: YouTube, Facebook, Instagram, Telegram
url = st.text_input("رابط الحساب")

if st.button("فحص الحالة"):
    if url and platform:
        with st.spinner("جاري الفحص..."):
            result = check_account_status(url, platform)
            st.success(f"حالة الحساب: {result}")
    else:
        st.warning("يرجى إدخال الرابط واختيار المنصة أولاً.")
