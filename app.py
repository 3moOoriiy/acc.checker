import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

def check_account_status(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
        }
        
        # تنظيف الرابط
        url = re.sub(r'https?://(www\.)?', 'https://', url.strip())
        if not url.startswith('https://'):
            url = f'https://{url}'
        
        response = requests.get(url, headers=headers, timeout=15)
        content = response.text
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # علامات التعليق الدقيقة (محدثة)
        suspension_indicators = [
            # الهيكل الرسمي لصفحة التعليق
            {'element': 'div', 'attrs': {'data-testid': 'empty_state_header_text'}, 'text': 'Account suspended'},
            {'element': 'div', 'attrs': {'data-testid': 'empty_state_body_text'}, 'text': 'X suspends accounts'},
            
            # العناصر الهيكلية للحسابات الموقوفة
            {'element': 'div', 'attrs': {'class': 'css-175oi2r r-1kihuf0 r-1xk7izq'}},
            {'element': 'div', 'attrs': {'class': 'css-175oi2r r-1kihuf0 r-1xk7izq r-f8sm7e r-jzhu7e'}},
            
            # النصوص العربية والإنجليزية للتعليق
            {'text': 'حساب موقوف'},
            {'text': 'تم تعليق الحساب'},
            {'text': 'This account is suspended'}
        ]
        
        # علامات النشاط الدقيقة (محدثة)
        activity_indicators = [
            # عناصر الملف الشخصي النشط
            {'element': 'div', 'attrs': {'data-testid': 'UserProfileHeader_Items'}},
            {'element': 'div', 'attrs': {'data-testid': 'UserDescription'}},
            {'element': 'img', 'attrs': {'alt': 'Profile image'}},
            
            # عناصر التغريدات
            {'element': 'div', 'attrs': {'data-testid': 'tweet'}},
            {'element': 'article', 'attrs': {'role': 'article'}},
            
            # عناصر المتابعة
            {'element': 'div', 'attrs': {'data-testid': 'placementTracking'}},
            {'element': 'button', 'attrs': {'data-testid': '1933527364975087616-follow'}}
        ]
        
        # التحقق من التعليق
        for indicator in suspension_indicators:
            if 'element' in indicator and 'attrs' in indicator:
                element = soup.find(indicator['element'], attrs=indicator['attrs'])
                if element:
                    if 'text' in indicator:
                        if re.search(indicator['text'], element.get_text(), re.IGNORECASE):
                            return {
                                "status": "موقوف",
                                "icon": "⛔",
                                "reason": "الحساب مخالف لشروط إكس",
                                "details": "تم اكتشاف علامات التعليق الرسمية",
                                "evidence": str(element)[:200] + "..."
                            }
                    else:
                        return {
                            "status": "موقوف",
                            "icon": "⛔",
                            "reason": "الحساب مخالف لشروط إكس",
                            "details": "تم اكتشاف هيكل الصفحة الموقوفة",
                            "evidence": str(element)[:200] + "..."
                        }
            elif 'text' in indicator:
                if re.search(indicator['text'], content, re.IGNORECASE):
                    return {
                        "status": "موقوف",
                        "icon": "⛔",
                        "reason": "الحساب مخالف لشروط إكس",
                        "details": "تم العثور على نص التعليق",
                        "evidence": re.search(indicator['text'], content, re.IGNORECASE).group(0)
                    }
        
        # التحقق من النشاط
        active_elements = []
        for indicator in activity_indicators:
            if soup.find(indicator['element'], attrs=indicator.get('attrs', {})):
                active_elements.append(indicator['element'])
        
        if active_elements:
            return {
                "status": "نشط",
                "icon": "✅",
                "reason": "الحساب يعمل بشكل طبيعي",
                "details": f"تم العثور على: {', '.join(active_elements)}",
                "evidence": "محتوى الملف الشخصي والتغريدات موجودة"
            }
        
        return {
            "status": "غير محدد",
            "icon": "❓",
            "reason": "لا يمكن تحديد الحالة بدقة",
            "details": "لم يتم العثور على بيانات كافية",
            "evidence": "لا يوجد محتوى واضح"
        }

    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return {
                "status": "غير موجود",
                "icon": "❌",
                "reason": "الحساب محذوف أو غير صحيح",
                "details": "الرمز 404: الصفحة غير موجودة",
                "evidence": "استجابة الخادم: 404"
            }
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": f"خطأ في الاتصال: {e.response.status_code}",
            "details": str(e),
            "evidence": "حدث خطأ أثناء محاولة الوصول للحساب"
        }
    except Exception as e:
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": "خطأ غير متوقع",
            "details": str(e),
            "evidence": "حدث خطأ غير متوقع"
        }

# واجهة المستخدم
st.set_page_config(
    page_title="أداة فحص حسابات تويتر/إكس الدقيقة",
    layout="centered"
)

# تنسيق عربي
st.markdown("""
<style>
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .suspended {
        color: #ff0000;
        font-weight: bold;
        border-right: 5px solid #ff0000;
        padding-right: 10px;
    }
    .active {
        color: #00aa00;
        font-weight: bold;
        border-right: 5px solid #00aa00;
        padding-right: 10px;
    }
    .unknown {
        color: #ffcc00;
        font-weight: bold;
    }
    .error {
        color: #666666;
        font-weight: bold;
    }
    .evidence {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        font-family: monospace;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 أداة فحص حسابات تويتر/إكس")

url = st.text_input("أدخل رابط الحساب", placeholder="https://x.com/اسم_المستخدم")

if st.button("فحص الحساب"):
    if url:
        with st.spinner("جاري التحقق بدقة..."):
            result = check_account_status(url)
            
            # عرض النتائج
            status_class = {
                "موقوف": "suspended",
                "نشط": "active",
                "غير محدد": "unknown",
                "خطأ": "error",
                "غير موجود": "error"
            }.get(result['status'], "")
            
            st.markdown(f"""
            <div class="rtl">
                <h3 class="{status_class}">{result['icon']} الحالة: {result['status']}</h3>
                <p><strong>السبب:</strong> {result['reason']}</p>
                <p><strong>التفاصيل:</strong> {result['details']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # عرض أدلة الإثبات
            with st.expander("أدلة الإثبات التقنية"):
                st.write("**الدليل:**")
                st.code(result['evidence'], language='html')
                
                if result['status'] == "موقوف":
                    st.warning("""
                    العلامات الدالة على التعليق:
                    1. وجود نص 'Account suspended' أو 'حساب موقوف'
                    2. وجود عنصر data-testid='empty_state_header_text'
                    3. ذكر 'X suspends accounts which violate'
                    """)
                elif result['status'] == "نشط":
                    st.info("""
                    العلامات الدالة على النشاط:
                    1. وجود وصف المستخدم (UserDescription)
                    2. وجود عناصر الملف الشخصي (UserProfileHeader_Items)
                    3. وجود زر المتابعة (Follow button)
                    """)
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("ℹ️ تم التحديث ليدعم أحدث تغييرات تويتر/إكس - يوليو 2024")
