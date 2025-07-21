import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

def advanced_account_check(url):
    try:
        # التحقق الأول: طلب HTTP الأساسي
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        content = response.text.lower()
        
        # التحليل باستخدام BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # 1. التحقق من التعليق الرسمي
        suspended_keywords = [
            'account suspended', 'حساب موقوف', 
            'تم تعليق الحساب', 'suspendedaccount',
            'account_status":"suspended', 'هذا الحساب مغلق'
        ]
        
        # 2. التحقق من العلامات الوصفية
        meta_tags = soup.find_all('meta')
        meta_check = any(
            'suspended' in str(tag).lower() or 'موقوف' in str(tag).lower() 
            for tag in meta_tags
        )
        
        # 3. التحقق من عنوان الصفحة
        title_check = any(
            kw in soup.title.string.lower() if soup.title else False
            for kw in ['suspended', 'موقوف']
        )
        
        # 4. التحقق من الصور التحذيرية
        img_check = any(
            'suspended' in img.get('src', '').lower() or
            'موقوف' in img.get('alt', '').lower()
            for img in soup.find_all('img')
        )
        
        # 5. التحقق من رأس الاستجابة
        header_check = any(
            'suspended' in str(response.headers).lower() or
            'موقوف' in str(response.headers).lower()
        )
        
        # 6. التحقق من الروابط الخاصة بالتعليق
        link_check = any(
            'suspended' in link.get('href', '').lower() or
            'موقوف' in link.get('href', '').lower()
            for link in soup.find_all('a')
        )
        
        # تحليل النتائج
        if any(kw in content for kw in suspended_keywords):
            return "⚠️ الحساب موقوف (تم الكشف عبر النص)"
        elif meta_check:
            return "⚠️ الحساب موقوف (تم الكشف عبر العلامات الوصفية)"
        elif title_check:
            return "⚠️ الحساب موقوف (تم الكشف عبر عنوان الصفحة)"
        elif img_check:
            return "⚠️ الحساب موقوف (تم الكشف عبر الصور التحذيرية)"
        elif header_check:
            return "⚠️ الحساب موقوف (تم الكشف عبر رأس الاستجابة)"
        elif link_check:
            return "⚠️ الحساب موقوف (تم الكشف عبر الروابط)"
        elif "هذا الحساب غير موجود" in content:
            return "❌ الحساب غير موجود"
        else:
            # فحص إضافي باستخدام واجهة الأرشفة
            archive_url = f"http://web.archive.org/web/{url}"
            archive_response = requests.get(archive_url)
            if "This URL has been excluded" in archive_response.text:
                return "⚠️ الحساب قديم أو محذوف (مستبعد من الأرشيف)"
            
            return "✅ الحساب نشط (تم التحقق بعدة طرق)"
            
    except Exception as e:
        return f"❌ خطأ في الفحص: {str(e)}"

# واجهة المستخدم
st.set_page_config(
    page_title="أداة الفحص المتقدم",
    layout="centered",
    initial_sidebar_state="expanded"
)

# تنسيق CSS مخصص
st.markdown("""
<style>
    .stTextInput input {
        padding: 12px !important;
        border: 2px solid #1DA1F2 !important;
        border-radius: 8px !important;
    }
    .stSelectbox select {
        padding: 12px !important;
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
    .stAlert {
        border-radius: 12px !important;
        padding: 20px !important;
    }
    .header {
        color: #1DA1F2;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# واجهة التطبيق
st.markdown('<h1 class="header">🔍 أداة الفحص المتقدم للحسابات</h1>', unsafe_allow_html=True)

with st.expander("🛠️ كيف يعمل الفحص المتقدم"):
    st.write("""
    تقوم الأداة بفحص الحساب بعدة طرق:
    1. تحليل محتوى الصفحة
    2. فحص العلامات الوصفية
    3. تحليل عنوان الصفحة
    4. البحث عن صور التحذير
    5. تحليل رأس الاستجابة
    6. فحص الروابط الخاصة
    7. التحقق من أرشيف الإنترنت
    """)

platform = st.selectbox("اختر المنصة:", ["تويتر/إكس"])
account_url = st.text_input("أدخل رابط الحساب", placeholder="https://x.com/اسم_المستخدم")

if st.button("فحص متقدم"):
    if account_url:
        with st.spinner("🔎 جاري الفحص المتعمق، قد يستغرق دقيقة..."):
            result = advanced_account_check(account_url)
            
            if "موقوف" in result:
                st.error(result)
                st.warning("💡 نصائح: يمكنك تقديم استئناف إذا كان الحساب مهمًا")
            elif "غير موجود" in result:
                st.warning(result)
            elif "نشط" in result:
                st.success(result)
                st.balloons()
            else:
                st.info(result)
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("🔄 آخر تحديث: ١٠ يونيو ٢٠٢٤ | الأداة توفر دقة عالية ولكنها ليست مضمونة ١٠٠٪")
