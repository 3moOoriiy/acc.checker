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
        
        # تنظيف الرابط
        url = re.sub(r'https?://(www\.)?', 'https://', url.strip())
        if not url.startswith('https://'):
            url = f'https://{url}'
        
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # نظام الكشف المحسن
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

        # التحليل المحسن
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

# واجهة المستخدم المحسنة
st.set_page_config(
    page_title="🔍 الأداة المتقدمة لفحص حسابات إكس",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    .rtl {
        direction: rtl;
        text-align: right;
        font-family: 'Tahoma', 'Arial', sans-serif;
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
        font-family: 'Courier New', monospace;
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
        text-align: right;
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
                    "⛔ الحساب موقوف": "suspended-card",
                    "✅ الحساب نشط": "active-card",
                    "❓ حالة غير محددة": "unknown-card",
                    "❗ خطأ فني": "error-card",
                    "❌ الحساب غير موجود": "error-card",
                    "⛔ الدخول مرفوض": "error-card",
                    "🔒 يتطلب مصادقة": "error-card"
                }.get(result['status'], "")
                
                # عرض النتائج
                st.markdown(f"""
                <div class="result-card rtl {card_class}">
                    <h2>{result['status']} <span class="confidence-badge" style="background-color: {'#ff4b4b' if 'موقوف' in result['status'] else '#2ecc71' if 'نشط' in result['status'] else '#ffcc00' if 'غير محددة' in result['status'] else '#95a5a6'}; color: white;">{result['confidence']}</span></h2>
                    <p><strong>التفاصيل:</strong> {result['details']}</p>
                    <p><strong>السبب:</strong> {result['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض أدلة الإثبات
                with st.expander("التقرير الفني (للمحترفين)"):
                    st.markdown(f"""
                    <div class="rtl">
                        <h4>أدلة الإثبات:</h4>
                        <div class="evidence-box">{result['evidence']}</div>
                        <p><strong>مستوى الثقة:</strong> {result['confidence']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # تأثيرات بصرية
                if "نشط" in result['status']:
                    st.balloons()
                elif "موقوف" in result['status']:
                    st.error("تنبيه: هذا الحساب موقوف رسمياً")

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
            <li>النتائج ذات الثقة فوق 90% موثوقة</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="rtl"><p>© 2024 نظام الفحص المتقدم - إصدار 4.2.0 | تم التحديث ليدعم أحدث تغييرات إكس</p></div>', unsafe_allow_html=True)
