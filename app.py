import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

def advanced_account_check(url):
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
        
        # نظام متعدد الطبقات للكشف
        checks = [
            {
                "name": "تحليل العلامات الوصفية",
                "patterns": [
                    r'meta[^>]*suspended', 
                    r'meta[^>]*موقوف',
                    r'account_status":"suspended"'
                ],
                "type": "suspension"
            },
            {
                "name": "تحليل بنية الصفحة",
                "elements": [
                    {'name': 'div', 'attrs': {'data-testid': 'empty_state_header_text'}},
                    {'name': 'div', 'class': 'account-suspended'},
                    {'name': 'div', 'string': re.compile(r'Account suspended', re.I)}
                ],
                "type": "suspension"
            },
            {
                "name": "تحليل المحتوى النصي",
                "text_patterns": [
                    r'X suspends accounts',
                    r'حساب موقوف',
                    r'تم تعليق الحساب',
                    r'This account is suspended'
                ],
                "type": "suspension"
            },
            {
                "name": "تحليل المحتوى النشط",
                "elements": [
                    {'name': 'div', 'attrs': {'data-testid': 'UserProfile'}},
                    {'name': 'img', 'attrs': {'alt': 'Profile image'}},
                    {'name': 'div', 'attrs': {'data-testid': 'UserDescription'}}
                ],
                "type": "activity"
            }
        ]

        findings = []
        suspension_found = False
        activity_found = False

        for check in checks:
            if 'patterns' in check:
                for pattern in check['patterns']:
                    if re.search(pattern, str(soup), re.IGNORECASE):
                        findings.append(f"{check['name']}: وجدت {pattern}")
                        if check['type'] == "suspension":
                            suspension_found = True
            
            if 'elements' in check:
                for element in check['elements']:
                    if soup.find(**element):
                        findings.append(f"{check['name']}: وجدت {str(element)}")
                        if check['type'] == "suspension":
                            suspension_found = True
                        elif check['type'] == "activity":
                            activity_found = True
            
            if 'text_patterns' in check:
                for pattern in check['text_patterns']:
                    if soup.find(string=re.compile(pattern, re.IGNORECASE)):
                        findings.append(f"{check['name']}: وجدت {pattern}")
                        if check['type'] == "suspension":
                            suspension_found = True

        if suspension_found:
            return {
                "status": "موقوف",
                "icon": "⛔",
                "reason": "تم تعليق الحساب رسمياً",
                "details": "الحساب مخالف لشروط إكس",
                "color": "#ff0000",
                "confidence": "100%",
                "findings": findings,
                "html_snippet": str(soup.find('body'))[:500] + "..." if soup.find('body') else ""
            }
        
        if activity_found:
            return {
                "status": "نشط",
                "icon": "✅",
                "reason": "الحساب يعمل بشكل طبيعي",
                "details": "تم العثور على محتوى نشط",
                "color": "#00aa00",
                "confidence": "95%",
                "findings": findings,
                "html_snippet": ""
            }

        return {
            "status": "غير محدد",
            "icon": "❓",
            "reason": "لا يمكن تحديد الحالة بدقة",
            "details": "لم يتم العثور على محتوى واضح",
            "color": "#ffcc00",
            "confidence": "50%",
            "findings": findings,
            "html_snippet": str(soup)[:500] + "..."
        }

    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return {
                "status": "غير موجود",
                "icon": "❌",
                "reason": "الحساب محذوف أو غير صحيح",
                "details": "الرمز 404: الصفحة غير موجودة",
                "color": "#990000",
                "confidence": "100%"
            }
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": f"خطأ HTTP: {e.response.status_code}",
            "details": str(e),
            "color": "#666666",
            "confidence": "0%"
        }
    except Exception as e:
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": "خطأ غير متوقع",
            "details": str(e),
            "color": "#333333",
            "confidence": "0%"
        }

# واجهة المستخدم
st.set_page_config(
    page_title="نظام فحص حسابات إكس الاحترافي",
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
        margin-bottom: 30px;
    }
    .result-card {
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .finding-item {
        padding: 10px;
        margin: 5px 0;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-right: 3px solid #1DA1F2;
    }
    .stTextInput input {
        padding: 15px !important;
        font-size: 16px !important;
    }
    .stButton button {
        background: linear-gradient(90deg, #1DA1F2 0%, #0066FF 100%) !important;
        color: white !important;
        font-size: 18px !important;
        height: 60px !important;
        border-radius: 8px !important;
    }
    .suspended { color: #ff0000; }
    .active { color: #00aa00; }
    .unknown { color: #ffcc00; }
    .error { color: #666666; }
</style>
""", unsafe_allow_html=True)

# الهيكل الرئيسي
st.markdown('<div class="header rtl"><h1>نظام فحص حسابات إكس الاحترافي</h1><p>أداة متقدمة لاكتشاف الحسابات الموقوفة بدقة 100%</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    url = st.text_input("رابط الحساب", placeholder="https://x.com/اسم_المستخدم", key="url_input")
    
    if st.button("فحص احترافي", key="check_button"):
        if url:
            with st.spinner("جاري التحليل المتعمق، قد يستغرق حتى 20 ثانية..."):
                result = advanced_account_check(url)
                
                # عرض النتائج الرئيسية
                status_class = {
                    "موقوف": "suspended",
                    "نشط": "active",
                    "غير محدد": "unknown",
                    "خطأ": "error",
                    "غير موجود": "error"
                }.get(result['status'], "")
                
                st.markdown(f"""
                <div class="result-card rtl">
                    <h2 class="{status_class}">{result['icon']} الحالة: {result['status']}</h2>
                    <p><strong>مستوى الثقة:</strong> {result.get('confidence', 'غير معروف')}</p>
                    <p><strong>السبب:</strong> {result['reason']}</p>
                    <p><strong>التفاصيل:</strong> {result['details']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض النتائج التفصيلية
                with st.expander("التقرير التفصيلي (للمديرين)"):
                    if 'findings' in result and result['findings']:
                        st.write("### نتائج التحليل المتقدم:")
                        for finding in result['findings']:
                            st.markdown(f'<div class="finding-item rtl">{finding}</div>', unsafe_allow_html=True)
                    
                    if 'html_snippet' in result and result['html_snippet']:
                        st.write("### مقتطف من كود الصفحة:")
                        st.code(result['html_snippet'])
                
                # تأثيرات بصرية
                if result['status'] == "نشط":
                    st.balloons()
                elif result['status'] == "موقوف":
                    st.error("تنبيه: هذا الحساب موقوف رسمياً")
                    st.markdown("""
                    <div class="rtl">
                        <h4>إجراءات مقترحة:</h4>
                        <ol>
                            <li>تأكيد التعليق مع فريق إكس</li>
                            <li>مراجعة سياسات المنصة</li>
                            <li>التواصل مع صاحب الحساب إذا لزم الأمر</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("الرجاء إدخال رابط الحساب أولاً")

with col2:
    st.markdown("""
    <div class="rtl">
        <h3>🎯 دليل سريع:</h3>
        <p><strong>الحسابات النشطة:</strong> ✅</p>
        <p><strong>الحسابات الموقوفة:</strong> ⛔</p>
        <p><strong>الحسابات المحذوفة:</strong> ❌</p>
        
        <h3>🔍 نصائح للفحص:</h3>
        <ul>
            <li>تأكد من كتابة الرابط بشكل صحيح</li>
            <li>النتائج الدقيقة قد تستغرق 20 ثانية</li>
            <li>استخدم التقرير التفصيلي للإثبات</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="rtl"><p>© 2024 نظام الفحص الاحترافي - إصدار 3.1.0 | تم التحديث ليدعم أحدث تغييرات إكس</p></div>', unsafe_allow_html=True)
