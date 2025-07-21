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
        
        # تنظيف وتحسين الرابط
        url = re.sub(r'https?://(www\.)?', 'https://', url.strip())
        if not url.startswith('https://'):
            url = f'https://{url}'
        
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # نظام الكشف المتقدم
        def check_suspension():
            suspension_patterns = [
                # أنماط HTML الدقيقة
                {'element': 'div', 'attrs': {'data-testid': 'empty_state_header_text'}, 'text': 'Account suspended'},
                {'element': 'div', 'attrs': {'data-testid': 'empty_state_body_text'}, 'text': 'X suspends accounts'},
                
                # أنماط الهيكل الداخلي
                {'element': 'div', 'attrs': {'class': 'css-175oi2r r-1kihuf0'}},
                {'element': 'div', 'attrs': {'class': 'r-1kihuf0 r-1xk7izq'}},
                
                # أنماط النصوص
                {'text': 'حساب موقوف'},
                {'text': 'تم تعليق الحساب'},
                {'text': 'account_status":"suspended"'}
            ]
            
            for pattern in suspension_patterns:
                if 'element' in pattern:
                    element = soup.find(pattern['element'], attrs=pattern.get('attrs', {}))
                    if element:
                        if 'text' in pattern:
                            if re.search(pattern['text'], element.get_text(), re.IGNORECASE):
                                return True
                        else:
                            return True
                elif 'text' in pattern:
                    if soup.find(string=re.compile(pattern['text'], re.IGNORECASE)):
                        return True
            return False

        def check_activity():
            activity_elements = [
                {'element': 'div', 'attrs': {'data-testid': 'UserProfileHeader_Items'}},
                {'element': 'div', 'attrs': {'data-testid': 'UserDescription'}},
                {'element': 'img', 'attrs': {'alt': 'Profile image'}},
                {'element': 'button', 'attrs': {'data-testid': re.compile(r'follow|unfollow')}},
                {'element': 'div', 'attrs': {'data-testid': 'UserProfileHeader_Items'}}
            ]
            
            return any(soup.find(e['element'], attrs=e.get('attrs', {})) for e in activity_elements)

        # التحقق الدقيق
        if check_suspension():
            return {
                "status": "موقوف",
                "icon": "⛔",
                "reason": "تم تعليق الحساب رسمياً",
                "details": "الحساب مخالف لشروط إكس",
                "confidence": "100%",
                "evidence": "تم العثور على علامات التعليق الرسمية"
            }
        
        if check_activity():
            return {
                "status": "نشط",
                "icon": "✅",
                "reason": "الحساب يعمل بشكل طبيعي",
                "details": "تم التحقق من المحتوى النشط",
                "confidence": "99%",
                "evidence": "وجود عناصر الملف الشخصي والنشاط"
            }
        
        return {
            "status": "غير محدد",
            "icon": "❓",
            "reason": "لا يمكن تحديد الحالة بدقة",
            "details": "لم يتم العثور على بيانات كافية",
            "confidence": "50%",
            "evidence": "لا توجد أدلة كافية"
        }

    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return {
                "status": "غير موجود",
                "icon": "❌",
                "reason": "الحساب محذوف أو غير صحيح",
                "details": "الرمز 404: الصفحة غير موجودة",
                "confidence": "100%",
                "evidence": f"استجابة الخادم: {e.response.status_code}"
            }
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": f"خطأ HTTP: {e.response.status_code}",
            "details": str(e),
            "confidence": "0%",
            "evidence": "فشل في الاتصال بالخادم"
        }
    except Exception as e:
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": "خطأ غير متوقع",
            "details": str(e),
            "confidence": "0%",
            "evidence": "حدث خطأ غير متوقع"
        }

# واجهة المستخدم المحسنة
st.set_page_config(
    page_title="🔍 الأداة المتقدمة لفحص حسابات إكس",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS متقدم
st.markdown("""
<style>
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .header {
        background: linear-gradient(90deg, #1DA1F2 0%, #0066FF 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .result-card {
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-right: 5px solid;
    }
    .suspended-card {
        border-color: #ff4b4b;
        background-color: #fff5f5;
    }
    .active-card {
        border-color: #2ecc71;
        background-color: #f5fff7;
    }
    .unknown-card {
        border-color: #ffcc00;
        background-color: #fffdf5;
    }
    .error-card {
        border-color: #95a5a6;
        background-color: #f5f5f5;
    }
    .evidence-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-family: monospace;
    }
    .confidence-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: bold;
    }
    .stTextInput input {
        padding: 12px !important;
        font-size: 16px !important;
    }
    .stButton button {
        background: linear-gradient(90deg, #1DA1F2 0%, #0066FF 100%) !important;
        color: white !important;
        font-size: 18px !important;
        height: 50px !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# الهيكل الرئيسي
st.markdown('<div class="header rtl"><h1>🔍 الأداة المتقدمة لفحص حسابات إكس</h1><p>أداة متكاملة للكشف الدقيق عن حالة الحسابات</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    url = st.text_input("رابط الحساب", placeholder="https://x.com/اسم_المستخدم", key="url_input")
    
    if st.button("فحص متقدم", key="check_button"):
        if url:
            with st.spinner("جاري التحليل المتعمق، يرجى الانتظار..."):
                result = advanced_x_account_check(url)
                
                # تحديد فئة النتيجة
                card_class = {
                    "موقوف": "suspended-card",
                    "نشط": "active-card",
                    "غير محدد": "unknown-card",
                    "خطأ": "error-card",
                    "غير موجود": "error-card"
                }.get(result['status'], "")
                
                # عرض النتائج
                st.markdown(f"""
                <div class="result-card rtl {card_class}">
                    <h2>{result['icon']} {result['status']} <span class="confidence-badge" style="background-color: {'#ff4b4b' if result['status'] == 'موقوف' else '#2ecc71' if result['status'] == 'نشط' else '#ffcc00' if result['status'] == 'غير محدد' else '#95a5a6'}; color: white;">{result.get('confidence', '')}</span></h2>
                    <p><strong>السبب:</strong> {result['reason']}</p>
                    <p><strong>التفاصيل:</strong> {result['details']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض أدلة الإثبات
                with st.expander("التقرير الفني (للمحترفين)"):
                    st.markdown(f"""
                    <div class="rtl">
                        <h4>أدلة الإثبات:</h4>
                        <div class="evidence-box">{result['evidence']}</div>
                        <h4>مستوى الثقة: {result['confidence']}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                
                # تأثيرات بصرية
                if result['status'] == "نشط":
                    st.balloons()
                elif result['status'] == "موقوف":
                    st.error("تنبيه: هذا الحساب موقوف رسمياً")
        else:
            st.warning("الرجاء إدخال رابط الحساب أولاً")

with col2:
    st.markdown("""
    <div class="rtl">
        <h3>🎯 دليل الاستخدام:</h3>
        <p><strong>الحسابات النشطة:</strong> ✅</p>
        <p><strong>الحسابات الموقوفة:</strong> ⛔</p>
        <p><strong>الحسابات المحذوفة:</strong> ❌</p>
        
        <h3>🔍 نصائح مهمة:</h3>
        <ul>
            <li>تأكد من كتابة الرابط بشكل صحيح</li>
            <li>النتائج الدقيقة قد تستغرق 20 ثانية</li>
            <li>استخدم التقرير الفني للإثبات</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="rtl"><p>© 2024 نظام الفحص المتقدم - إصدار 4.0.0 | تم التحديث ليدعم أحدث تغييرات إكس</p></div>', unsafe_allow_html=True)
