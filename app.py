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
                # أنماط HTML الدقيقة للإيقاف
                {'element': 'div', 'attrs': {'data-testid': 'empty_state_header_text'}, 'text': 'Account suspended'},
                {'element': 'div', 'attrs': {'data-testid': 'empty_state_body_text'}, 'text': 'X suspends accounts'},
                {'element': 'div', 'attrs': {'class': 'css-175oi2r r-1kihuf0 r-1xk7izq'}},
                
                # أنماط النصوص العربية
                {'text': 'حساب موقوف'},
                {'text': 'تم تعليق الحساب'},
                {'text': 'الحساب غير متاح'},
                {'text': 'account_status":"suspended"'},
                
                # الأنماط الجديدة للايقاف
                {'element': 'div', 'attrs': {'class': 'r-1kihuf0 r-1xk7izq'}},
                {'element': 'div', 'attrs': {'data-testid': 'emptyState'}},
                {'element': 'span', 'attrs': {'class': 'css-1jxf684'}, 'text': 'Account suspended'}
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
                {'element': 'div', 'attrs': {'data-testid': 'UserProfileHeader_Items'}},
                {'element': 'div', 'attrs': {'data-testid': 'primaryColumn'}},
                {'element': 'div', 'attrs': {'data-testid': 'tweet'}},
                {'element': 'div', 'attrs': {'data-testid': 'UserName'}}
            ]
            
            return any(soup.find(e['element'], attrs=e.get('attrs', {})) for e in activity_elements)

        # التحقق الدقيق
        if check_suspension():
            return {
                "status": "مقفول (موقوف)",
                "icon": "⛔",
                "reason": "تم تعليق الحساب رسمياً",
                "details": "الحساب مخالف لشروط إكس أو تم إيقافه",
                "confidence": "100%",
                "evidence": "تم العثور على علامات التعليق الرسمية"
            }
        
        if check_activity():
            return {
                "status": "مفتوح (نشط)",
                "icon": "✅",
                "reason": "الحساب يعمل بشكل طبيعي",
                "details": "تم التحقق من المحتوى النشط والتفاعلات",
                "confidence": "99%",
                "evidence": "وجود عناصر الملف الشخصي والنشاط والتغريدات"
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
