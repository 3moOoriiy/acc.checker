import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

def check_x_account(url):
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

        # علامات التعليق المؤكدة
        suspension_evidence = [
            {'type': 'html', 'pattern': r'<div[^>]*data-testid="empty_state_header_text"[^>]*>.*?Account suspended'},
            {'type': 'text', 'pattern': r'X suspends accounts which violate'},
            {'type': 'html', 'pattern': r'حساب موقوف'},
            {'type': 'html', 'pattern': r'تم تعليق الحساب'},
            {'type': 'element', 'name': 'div', 'attrs': {'data-testid': 'empty_state_header_text'}}
        ]

        # علامات النشاط المؤكدة
        activity_evidence = [
            {'type': 'element', 'name': 'div', 'attrs': {'data-testid': 'UserProfileHeader_Items'}},
            {'type': 'element', 'name': 'div', 'attrs': {'data-testid': 'UserDescription'}},
            {'type': 'element', 'name': 'img', 'attrs': {'alt': 'Profile image'}},
            {'type': 'element', 'name': 'button', 'attrs': {'data-testid': 'userFollowButton'}}
        ]

        # البحث عن أدلة التعليق
        suspension_found = []
        for evidence in suspension_evidence:
            if evidence['type'] == 'html' and re.search(evidence['pattern'], content, re.IGNORECASE):
                suspension_found.append(evidence['pattern'])
            elif evidence['type'] == 'text' and evidence['pattern'].lower() in content.lower():
                suspension_found.append(evidence['pattern'])
            elif evidence['type'] == 'element' and soup.find(evidence['name'], attrs=evidence.get('attrs', {})):
                suspension_found.append(f"{evidence['name']} {evidence.get('attrs', {})}")

        if suspension_found:
            return {
                "status": "موقوف",
                "icon": "⛔",
                "reason": "تم تعليق الحساب رسمياً",
                "details": "الحساب مخالف لشروط إكس",
                "evidence": suspension_found[:3]  # عرض أول 3 أدلة فقط
            }

        # البحث عن أدلة النشاط
        activity_found = []
        for evidence in activity_evidence:
            if evidence['type'] == 'element' and soup.find(evidence['name'], attrs=evidence.get('attrs', {})):
                activity_found.append(f"{evidence['name']} {evidence.get('attrs', {})}")

        if activity_found:
            return {
                "status": "نشط",
                "icon": "✅",
                "reason": "الحساب يعمل بشكل طبيعي",
                "details": "تم التحقق من المحتوى النشط",
                "evidence": activity_found[:3]  # عرض أول 3 أدلة فقط
            }

        # إذا لم يتم العثور على أي دليل واضح
        return {
            "status": "غير محدد",
            "icon": "❓",
            "reason": "لا يمكن تحديد الحالة بدقة",
            "details": "لم يتم العثور على بيانات كافية",
            "evidence": ["لا توجد أدلة كافية للتحديد"]
        }

    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return {
                "status": "غير موجود",
                "icon": "❌",
                "reason": "الحساب محذوف أو غير صحيح",
                "details": "الرمز 404: الصفحة غير موجودة",
                "evidence": [f"استجابة الخادم: {e.response.status_code}"]
            }
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": f"خطأ في الاتصال: {e.response.status_code}",
            "details": str(e),
            "evidence": ["حدث خطأ أثناء محاولة الوصول"]
        }
    except Exception as e:
        return {
            "status": "خطأ",
            "icon": "❗",
            "reason": "خطأ غير متوقع",
            "details": str(e),
            "evidence": ["حدث خطأ غير متوقع"]
        }

# واجهة المستخدم
st.set_page_config(
    page_title="أداة فحص حسابات إكس الدقيقة",
    layout="centered"
)

# تنسيق عربي
st.markdown("""
<style>
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .result-card {
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .suspended {
        border-right: 5px solid #ff4b4b;
    }
    .active {
        border-right: 5px solid #2ecc71;
    }
    .unknown {
        border-right: 5px solid #ffcc00;
    }
    .error {
        border-right: 5px solid #95a5a6;
    }
    .evidence-item {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 أداة فحص حسابات إكس")

url = st.text_input("أدخل رابط الحساب", placeholder="https://x.com/اسم_المستخدم")

if st.button("فحص الحساب"):
    if url:
        with st.spinner("جاري التحقق بدقة..."):
            result = check_x_account(url)
            
            # تحديد فئة النتيجة
            status_class = {
                "موقوف": "suspended",
                "نشط": "active",
                "غير محدد": "unknown",
                "خطأ": "error",
                "غير موجود": "error"
            }.get(result['status'], "")
            
            # عرض النتيجة
            st.markdown(f"""
            <div class="result-card rtl {status_class}">
                <h3>{result['icon']} الحالة: {result['status']}</h3>
                <p><strong>السبب:</strong> {result['reason']}</p>
                <p><strong>التفاصيل:</strong> {result['details']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # عرض أدلة الإثبات
            st.write("**أدلة الإثبات:**")
            for evidence in result['evidence']:
                st.markdown(f'<div class="evidence-item rtl">{evidence}</div>', unsafe_allow_html=True)
            
            # نصائح إضافية
            if result['status'] == "غير محدد":
                st.warning("""
                نصائح:
                1. تأكد من صحة رابط الحساب
                2. حاول مرة أخرى لاحقاً
                3. تحقق يدوياً من الحساب
                """)
    else:
        st.warning("الرجاء إدخال رابط الحساب أولاً")

st.markdown("---")
st.caption("تم التحديث في يوليو 2024 - إصدار 3.2.0")
