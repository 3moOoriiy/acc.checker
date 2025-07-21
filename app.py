<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أداة فحص حالة الحسابات</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1DA1F2;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        select, input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #1DA1F2;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #1991db;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .loading {
            text-align: center;
            margin: 20px 0;
            display: none;
        }
        .note {
            font-size: 14px;
            color: #666;
            margin-top: 30px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 أداة فحص حالة الحسابات</h1>
        
        <div class="form-group">
            <label for="platform">اختر المنصة:</label>
            <select id="platform">
                <option value="twitter">تويتر/إكس</option>
                <option value="tiktok">تيك توك</option>
                <option value="reddit">ريديت</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="url">رابط الحساب:</label>
            <input type="text" id="url" placeholder="https://x.com/اسم_المستخدم">
        </div>
        
        <button onclick="checkAccount()">فحص الحالة</button>
        
        <div id="loading" class="loading">
            <p>جاري التحقق من الحساب، الرجاء الانتظار...</p>
        </div>
        
        <div id="result" class="result"></div>
        
        <div class="note">
            ملاحظة: هذه الأداة لا تضمن دقة 100% خاصة للحسابات المعلقة مؤقتاً
        </div>
    </div>

    <script>
        async function checkAccount() {
            const platform = document.getElementById('platform').value;
            let url = document.getElementById('url').value.trim();
            
            if (!url) {
                alert('الرجاء إدخال رابط الحساب');
                return;
            }
            
            // إضافة https:// إذا لم يكن موجوداً
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                url = 'https://' + url;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            
            try {
                // استخدام CORS Anywhere للتحايل على قيود CORS (لأغراض الاختبار فقط)
                const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
                const response = await fetch(proxyUrl + url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const html = await response.text();
                const resultDiv = document.getElementById('result');
                
                if (platform === 'twitter') {
                    if (/account\s*suspended|حساب\s*موقوف|تم\s*تعليق\s*الحساب/i.test(html)) {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = '⚠️ الحساب موقوف (معلق)';
                    } else if (/this\s*account\s*doesn\'t\s*exist|الحساب\s*غير\s*موجود/i.test(html)) {
                        resultDiv.className = 'result warning';
                        resultDiv.innerHTML = '❌ الحساب غير موجود أو محذوف';
                    } else {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = '✅ الحساب نشط (العمليات فقط)';
                    }
                }
                // يمكن إضافة منصات أخرى هنا...
                
                resultDiv.style.display = 'block';
                
            } catch (error) {
                document.getElementById('result').className = 'result error';
                document.getElementById('result').innerHTML = '❌ حدث خطأ أثناء التحقق: ' + error.message;
                document.getElementById('result').style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
