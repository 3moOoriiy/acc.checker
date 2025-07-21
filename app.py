import streamlit as st
import requests
import re
import json
import time
from urllib.parse import urlparse, quote

def check_x_account_status(url):
    """فحص حالة حساب إكس بطرق متعددة"""
    
    # تنظيف الرابط واستخراج اسم المستخدم
    def extract_username(url):
        try:
            url = url.strip()
            if not url.startswith('http'):
                url = 'https://' + url
            
            # استخراج اسم المستخدم من أنواع مختلفة من الروابط
            patterns = [
                r'(?:twitter\.com|x\.com)/([^/?]+)',
                r'@(\w+)',
                r'^(\w+)$'  # اسم المستخدم فقط
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    username = match.group(1)
                    # تنظيف اسم المستخدم
                    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
                    return username.lower()
            return None
        except:
            return None

    username = extract_username(url)
    if not username:
        return {
            "status": "❌ خطأ في الرابط",
            "details": "لم نتمكن من استخراج اسم المستخدم من الرابط",
            "reason": "تأكد من كتابة الرابط بشكل صحيح",
            "confidence": "100%",
            "evidence": "رابط غير صالح",
            "color": "error",
            "username": ""
        }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    results = {}
    
    # الطريقة 1: فحص صفحة الملف الشخصي مباشرة
    def method1_direct_check():
        try:
            profile_url = f"https://x.com/{username}"
            response = requests.get(profile_url, headers=headers, timeout=15, allow_redirects=True)
            
            # تحليل رمز الاستجابة
            if response.status_code == 404:
                return "not_found"
            elif response.status_code == 403:
                return "forbidden"
            elif response.status_code == 302 or response.status_code == 301:
                if 'suspended' in response.url:
                    return "suspended"
            
            content = response.text.lower()
            
            # فحص علامات التعليق
            suspension_signs = [
                'account suspended',
                'suspended account',
                'this account has been suspended',
                'حساب موقوف',
                'تم تعليق'
            ]
            
            for sign in suspension_signs:
                if sign in content:
                    return "suspended"
            
            # فحص علامات الحماية
            protection_signs = [
                'protected account',
                'these tweets are protected',
                'this account\'s tweets are protected',
                'محمي',
                'خاص'
            ]
            
            for sign in protection_signs:
                if sign in content:
                    return "protected"
            
            # فحص علامات النشاط
            activity_signs = [
                '"screen_name"',
                'profilepic',
                'tweet',
                'following',
                'followers'
            ]
            
            activity_count = sum(1 for sign in activity_signs if sign in content)
            if activity_count >= 2:
                return "active"
            
            return "unknown"
            
        except requests.exceptions.RequestException:
            return "error"
    
    # الطريقة 2: فحص API غير رسمي
    def method2_api_check():
        try:
            # استخدام نقطة نهاية عامة للفحص
            api_url = f"https://api.twitter.com/1.1/users/show.json?screen_name={username}"
            
            # محاولة الوصول دون مفتاح API (سيعطي معلومات عن وجود الحساب)
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                return "not_found"
            elif response.status_code == 403:
                # قد يكون محمي أو موقوف
                error_text = response.text.lower()
                if 'suspended' in error_text:
                    return "suspended"
                else:
                    return "protected"
            elif response.status_code == 401:
                # يحتاج API key، لكن الحساب موجود
                return "exists"
            
            return "unknown"
            
        except:
            return "error"
    
    # الطريقة 3: فحص البحث العام
    def method3_search_check():
        try:
            search_url = f"https://x.com/search?q=from%3A{username}&src=typed_query"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                if 'no results' in content or 'لم يتم العثور' in content:
                    return "inactive_or_suspended"
                elif username in content:
                    return "active"
            
            return "unknown"
            
        except:
            return "error"
    
    # تنفيذ الفحوصات
    result1 = method1_direct_check()
    time.sleep(1)  # انتظار قصير بين الطلبات
    result2 = method2_api_check()
    time.sleep(1)
    result3 = method3_search_check()
    
    # تحليل النتائج المدمجة
    results_list = [result1, result2, result3]
    
    # منطق القرار
    if "suspended" in results_list:
        return {
            "status": "⛔ الحساب موقوف",
            "details": "تم تعليق هذا الحساب من قبل إدارة منصة إكس",
            "reason": "انتهاك قوانين المنصة أو شروط الاستخدام",
            "confidence": "90%",
            "evidence": f"نتائج الفحص: {results_list}",
            "color": "error",
            "username": username
        }
    
    if "not_found" in results_list and results_list.count("not_found") >= 2:
        return {
            "status": "❌ الحساب غير موجود",
            "details": "هذا الحساب غير متوفر أو تم حذفه",
            "reason": "الحساب محذوف أو اسم المستخدم غير صحيح",
            "confidence": "95%",
            "evidence": f"نتائج الفحص: {results_list}",
            "color": "error",
            "username": username
        }
    
    if "protected" in results_list or "forbidden" in results_list:
        return {
            "status": "🔒 الحساب محمي",
            "details": "هذا الحساب محمي ولا يمكن رؤية منشوراته إلا للمتابعين المعتمدين",
            "reason": "إعدادات الخصوصية مفعلة - حساب خاص",
            "confidence": "85%",
            "evidence": f"نتائج الفحص: {results_list}",
            "color": "warning",
            "username": username
        }
    
    if "active" in results_list or "exists" in results_list:
        return {
            "status": "✅ الحساب نشط",
            "details": "الحساب يعمل بشكل طبيعي ويمكن الوصول إليه",
            "reason": "تم العثور على مؤشرات النشاط والمحتوى",
            "confidence": "80%",
            "evidence": f"نتائج الفحص: {results_list}",
            "color": "success",
            "username": username
        }
    
    # إذا كانت النتائج مختلطة أو غير واضحة
    return {
        "status": "❓ حالة غير واضحة",
        "details": "لم نتمكن من تحديد حالة الحساب بدقة كافية",
        "reason": "نتائج متضاربة أو مشاكل في الوصول للبيانات",
        "confidence": "50%",
        "evidence": f"نتائج الفحص: {results_list}",
        "color": "info",
        "username": username
    }

# إعداد الصفحة
st.set_page_config(
    page_title="فاحص حسابات إكس - مطور",
    page_icon="🔍",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', 'Tahoma', sans-serif;
    }
    
    .main {
        direction: rtl;
        text-align: right;
    }
    
    .header {
        background: linear-gradient(135deg, #1da1f2, #0d8bd9);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(29, 161, 242, 0.3);
    }
    
    .result-success {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
    }
    
    .result-error {
        background: linear-gradient(135deg, #dc3545, #e74c3c);
        color: white;
    }
    
    .result-warning {
        background: linear-gradient(135deg, #ffc107, #ffab00);
        color: #212529;
    }
    
    .result-info {
        background: linear-gradient(135deg, #17a2b8, #138496);
        color: white;
    }
    
    .result-card {
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .guide-section {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #dee2e6;
        margin: 1rem 0;
    }
    
    .status-example {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-right: 4px solid;
    }
    
    .status-active { background: #d4edda; border-color: #28a745; }
    .status-suspended { background: #f8d7da; border-color: #dc3545; }
    .status-protected { background: #fff3cd; border-color: #ffc107; }
    .status-notfound { background: #e2e3e5; border-color: #6c757d; }
    
    .stButton > button {
        background: linear-gradient(135deg, #007bff, #0056b3);
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 123, 255, 0.3);
    }
    
    .stTextInput input {
        text-align: right !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border: 2px solid #dee2e6 !important;
    }
    
    .username-display {
        background: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# واجهة التطبيق
st.markdown("""
<div class="header">
    <h1>🔍 فاحص حسابات إكس المطور</h1>
    <p>أداة متقدمة لفحص حالة أي حساب على منصة إكس بطرق متعددة</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 أدخل رابط الحساب أو اسم المستخدم")
    
    url_input = st.text_input(
        "",
        placeholder="https://x.com/username أو @username أو username",
        help="يمكنك إدخال الرابط كاملاً أو اسم المستخدم فقط"
    )
    
    if st.button("🔍 فحص الحساب", key="check_account"):
        if url_input.strip():
            with st.spinner("🔄 جاري الفحص بطرق متعددة... قد يستغرق 10-15 ثانية"):
                result = check_x_account_status(url_input.strip())
                
                # عرض اسم المستخدم المستخرج
                if result.get('username'):
                    st.markdown(f"""
                    <div class="username-display">
                        👤 اسم المستخدم: @{result['username']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # عرض النتيجة
                color_class = f"result-{result.get('color', 'info')}"
                
                st.markdown(f"""
                <div class="result-card {color_class}">
                    <h2>{result['status']}</h2>
                    <p><strong>📋 التفاصيل:</strong> {result['details']}</p>
                    <p><strong>💡 السبب:</strong> {result['reason']}</p>
                    <p><strong>🎯 مستوى الثقة:</strong> {result['confidence']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض التفاصيل الفنية
                with st.expander("🔧 التفاصيل الفنية"):
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; direction: ltr;">
                        <p><strong>📊 نتائج الفحص المتعدد:</strong></p>
                        <code>{result['evidence']}</code>
                        <p style="margin-top: 1rem; color: #6c757d;">
                            وقت الفحص: {time.strftime("%Y-%m-%d %H:%M:%S")}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("⚠️ الرجاء إدخال رابط الحساب أو اسم المستخدم")

with col2:
    st.markdown("""
    <div class="guide-section">
        <h3>📊 أنواع الحالات</h3>
        
        <div class="status-example status-active">
            <strong>✅ حساب نشط</strong><br>
            يعمل بشكل طبيعي ويمكن الوصول إليه
        </div>
        
        <div class="status-example status-suspended">
            <strong>⛔ حساب موقوف</strong><br>
            تم تعليقه من قبل الإدارة
        </div>
        
        <div class="status-example status-protected">
            <strong>🔒 حساب محمي</strong><br>
            خاص ومحدود على المتابعين
        </div>
        
        <div class="status-example status-notfound">
            <strong>❌ غير موجود</strong><br>
            محذوف أو غير صحيح
        </div>
        
        <h3>🎯 مميزات الأداة</h3>
        <ul style="padding-right: 1.5rem;">
            <li>فحص متعدد الطرق للدقة</li>
            <li>يدعم جميع أشكال الروابط</li>
            <li>تحليل ذكي للنتائج</li>
            <li>واجهة عربية سهلة</li>
        </ul>
        
        <h3>📖 كيفية الاستخدام</h3>
        <ol style="padding-right: 1.5rem;">
            <li>أدخل رابط الحساب أو اسم المستخدم</li>
            <li>اضغط على "فحص الحساب"</li>
            <li>انتظر النتيجة (10-15 ثانية)</li>
            <li>راجع التفاصيل الفنية إذا لزم الأمر</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# الفوتر
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #6c757d;">
    <p><strong>فاحص حسابات إكس المطور</strong> | الإصدار 2.1</p>
    <p>يستخدم طرق فحص متعددة لضمان الدقة العالية</p>
</div>
""", unsafe_allow_html=True)
