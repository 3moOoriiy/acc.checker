import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

def advanced_x_account_check(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
        }
        
        url = re.sub(r'https?://(www\.)?', 'https://', url.strip())
        if not url.startswith('https://'):
            url = f'https://{url}'
        
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        def check_suspension():
            suspension_patterns = [
                {'element': 'div', 'attrs': {'data-testid': 'empty_state_header_text'}, 'text': 'Account suspended'},
                {'element': 'div', 'attrs': {'class': 'css-175oi2r r-1kihuf0 r-1xk7izq'}},
                {'element': 'div', 'attrs': {'data-testid': 'empty_state_header_text'}, 'text': 'حساب موقوف'},
                {'element': 'span', 'text': 'تم تعليق الحساب'},
                {'text': 'account_status":"suspended"'}
            ]
            
            for pattern in suspension_patterns:
                try:
                    if 'element' in pattern:
                        elements = soup.find_all(pattern['element'], attrs=pattern.get('attrs', {}))
                        for element in elements:
                            if 'text' in pattern:
                                if element and re.search(pattern['text'], element.get_text(), re.IGNORECASE):
                                    return True
                            else:
                                if element:
                                    return True
                    elif 'text' in pattern:
                        if soup.find(string=re.compile(pattern['text'], re.IGNORECASE)):
                            return True
                except Exception:
                    continue
            return False

        def check_activity():
            activity_indicators = [
                {'element': 'div', 'attrs': {'data-testid': 'UserProfileHeader_Items'}},
                {'element': 'div', 'attrs': {'data-testid': 'UserDescription'}},
                {'element': 'div', 'attrs': {'data-testid': 'UserName'}},
                {'element': 'div', 'attrs': {'data-testid': 'tweet'}},
                {'element': 'a', 'attrs': {'href': re.compile(r'/followers')}},
                {'element': 'img', 'attrs': {'alt': 'Profile image'}}
            ]
            
            for indicator in activity_indicators:
                try:
                    if soup.find(indicator['element'], attrs=indicator.get('attrs', {})):
                        return True
                except Exception:
                    continue
            return False

        if check_suspension():
            return {
                "status": "⛔ الحساب موقوف",
                "details": "تم تعليق هذا الحساب من قبل إدارة المنصة",
                "reason": "انتهاك شروط الخدمة أو القوانين",
                "confidence": "95%",
                "evidence": "تم العثور على علامات التعليق الرسمية"
            }
        
        if check_activity():
            return {
                "status": "✅ الحساب نشط",
                "details": "الحساب يعمل بشكل طبيعي ويظهر المحتوى",
                "reason": "جميع المؤشرات تدل على النشاط",
                "confidence": "98%",
                "evidence": "تم اكتشاف عناصر الملف الشخصي والتغريدات"
            }
        
        return {
            "status": "❓ حالة غير محددة",
            "details": "لم نتمكن من تحديد حالة الحساب بدقة",
            "reason": "بيانات غير كافية أو شكل غير معروف",
            "confidence": "40%",
            "evidence": "لا توجد أدلة كافية لتحديد الحالة"
        }

    except requests.HTTPError as e:
        error_status = {
            404: ("❌ الحساب غير موجود", "الرابط غير صحيح أو الحساب محذوف"),
            403: ("⛔ الدخول مرفوض", "الحساب خاص أو محمي"),
            401: ("🔒 يتطلب مصادقة", "الحساب يحتاج تسجيل دخول")
        }.get(e.response.status_code, (f"❗ خطأ {e.response.status_code}", "حدث خطأ غير متوقع"))
        
        return {
            "status": error_status[0],
            "details": error_status[1],
            "reason": f"استجابة الخادم: {e.response.status_code}",
            "confidence": "100%",
            "evidence": str(e)
        }
    except Exception as e:
        return {
            "status": "❗ خطأ فني",
            "details": "حدث خطأ أثناء التحليل",
            "reason": "مشكلة تقنية غير متوقعة",
            "confidence": "0%",
            "evidence": str(e)
        }

# إعداد واجهة المستخدم
st.set_page_config(
    page_title="🔍 أداة فحص حسابات إكس",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيقات CSS المعدلة
st.markdown("""
<style>
    body {
        background-color: #f5f5f5 !important;
    }
    .rtl {
        direction: rtl;
        text-align: right;
        font-family: 'Tahoma', 'Arial', sans-serif;
    }
    .header {
        background: #1DA1F2;
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .result-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .suspended-card {
        border-right: 4px solid #ff4b4b;
    }
    .active-card {
        border-right: 4px solid #2ecc71;
    }
    .unknown-card {
        border-right: 4px solid #ffcc00;
    }
    .error-card {
        border-right: 4px solid #95a5a6;
    }
    .stTextInput input {
        padding: 12px !important;
        font-size: 16px !important;
        text-align: right;
    }
    .stButton button {
        background: #1DA1F2 !important;
        color: white !important;
        font-size: 18px !important;
        height: 50px !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# واجهة التطبيق
st.markdown('<div class="header rtl"><h1>🔍 أداة فحص حسابات إكس</h1><p>تحقق من حالة أي حساب على منصة إكس (تويتر)</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    url = st.text_input("رابط الحساب", placeholder="https://x.com/اسم_المستخدم")
    
    if st.button("فحص الحساب"):
        if url:
            with st.spinner("جاري التحليل..."):
                result = advanced_x_account_check(url)
                
                card_class = {
                    "⛔ الحساب موقوف": "suspended-card",
                    "✅ الحساب نشط": "active-card",
                    "❓ حالة غير محددة": "unknown-card",
                    "❗ خطأ فني": "error-card",
                    "❌ الحساب غير موجود": "error-card",
                    "⛔ الدخول مرفوض": "error-card",
                    "🔒 يتطلب مصادقة": "error-card"
                }.get(result['status'], "")
                
                st.markdown(f"""
                <div class="result-card rtl {card_class}">
                    <h2>{result['status']}</h2>
                    <p><strong>التفاصيل:</strong> {result['details']}</p>
                    <p><strong>السبب:</strong> {result['reason']}</p>
                    <p><strong>مستوى الثقة:</strong> {result['confidence']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("التفاصيل الفنية"):
                    st.markdown(f"""
                    <div class="rtl">
                        <p><strong>أدلة الإثبات:</strong></p>
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">
                            {result['evidence']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("الرجاء إدخال رابط الحساب")

with col2:
    st.markdown("""
    <div class="rtl">
        <h3>🎯 دليل الاستخدام</h3>
        <p><strong>✅ الحسابات النشطة:</strong> تعمل بشكل طبيعي</p>
        <p><strong>⛔ الحسابات الموقوفة:</strong> تم تعليقها</p>
        <p><strong>🔒 الحسابات الخاصة:</strong> تحتاج متابعة</p>
        
        <h3>⚙️ كيفية الاستخدام</h3>
        <ol>
            <li>أدخل رابط الحساب</li>
            <li>انقر على "فحص الحساب"</li>
            <li>انتظر النتائج</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="rtl"><p>© 2024 أداة فحص حسابات إكس | الإصدار 1.0</p></div>', unsafe_allow_html=True)
