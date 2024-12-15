import firebase_admin
from firebase_admin import credentials, db
import time
from flask import Flask
import threading

# إعداد Firebase
cred = credentials.Certificate("firebase.json")  # تأكد من أنك قمت بتحميل ملف المفتاح الخاص
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://iraqi-gold-coin-default-rtdb.firebaseio.com"  # رابط قاعدة البيانات
})

# مرجع قاعدة البيانات
bot_add_ref = db.reference("bot_add")

# خريطة لتحديد المبلغ المضاف لكل قيمة VIP
VIP_amounts = {
    "VIP1": 125,
    "VIP2": 250,
    "VIP3": 500,
    "VIP4": 1000
}

# وظيفة التحقق من القيم وإضافة الأموال
def update_balances():
    while True:
        data = bot_add_ref.get()  # جلب البيانات من Firebase
        if data:
            for uid, user_data in data.items():
                updates = {}  # لتخزين التحديثات لهذا المستخدم
                for VIP_key, iq_key in zip(["VIP1", "VIP2", "VIP3", "VIP4"], ["IQD1", "IQD2", "IQD3", "IQD4"]):
                    VIP_value = int(user_data.get(VIP_key, 0))  # قيمة VIP
                    if VIP_value > 0:  # إذا كانت القيمة أكبر من 0
                        current_balance = int(user_data.get(iq_key, 0))  # الرصيد الحالي
                        added_amount = VIP_value * VIP_amounts[VIP_key]  # حساب المبلغ المضاف
                        new_balance = current_balance + added_amount  # تحديث الرصيد
                        updates[iq_key] = new_balance  # تخزين التحديث

                if updates:
                    # تحديث قاعدة البيانات للمستخدم
                    bot_add_ref.child(uid).update(updates)
                    print(f"تم تحديث الرصيد لـ UID: {uid} - {updates}")

        time.sleep(10)  # التحقق كل 10 ثوانٍ

# إعداد Flask Web Server
app = Flask(__name__)

@app.route('/')
def index():
    return "البوت يعمل 24/7!"

def run_bot():
    update_balances()  # استدعاء الدالة التي تقوم بتحديث الرصيد بشكل مستمر

if __name__ == "__main__":
    # تشغيل البوت في خلفية السيرفر
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=80)
