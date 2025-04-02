from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# آیدی عددی تلگرام خودت
ADMIN_ID = "1478363268"

# توکن رباتت
BOT_TOKEN = "7990694940:AAHYGyi1mm2TNl2ZPSK98G0q4dCDaWcRevk"

# کلید API Gemini
GEMINI_API_KEY = "AIzaSyCPUX41Xo_N611S5ToS3eI-766Z7oHt2B4"

# تنظیم کلاینت Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')  # فرض می‌کنیم این مدل کار می‌کنه

# لینک PDF مستقیم (فعلاً استفاده نمی‌شه، چون فایل محلی می‌فرستیم)
PDF_LINK = "https://biaupload.com/do.php?filename=org-b946e23e76b71.pdf"

# منوی اصلی
def main_menu():
    keyboard = [
        [InlineKeyboardButton("درمان بیماری گیاهان", callback_data="treatment")],
        [InlineKeyboardButton("نحوه نگهداری گیاهان", callback_data="care")],
        [InlineKeyboardButton("آموزش", callback_data="education")],
        [InlineKeyboardButton("محصولات", callback_data="products")],
        [InlineKeyboardButton("ویزیت حضوری", callback_data="visit_home")],
        [InlineKeyboardButton("ویزیت آنلاین", callback_data="visit_online")],
    ]
    return InlineKeyboardMarkup(keyboard)

# منوی آموزش
def education_menu():
    keyboard = [
        [InlineKeyboardButton("مبانی اولیه گیاه‌شناسی", callback_data="edu_1")],
        [InlineKeyboardButton("روش‌های آبیاری و تغذیه", callback_data="edu_2")],
        [InlineKeyboardButton("تکثیر و پرورش گیاهان", callback_data="edu_3")],
        [InlineKeyboardButton("کنترل آفات و بیماری‌ها", callback_data="edu_4")],
        [InlineKeyboardButton("طراحی و نگهداری فضای سبز", callback_data="edu_5")],
        [InlineKeyboardButton("مشکلات رایج و راهکارها", callback_data="edu_6")],
        [InlineKeyboardButton("روش‌های خاص نگهداری", callback_data="edu_7")],
        [InlineKeyboardButton("نور", callback_data="edu_8")],
        [InlineKeyboardButton("گلدان مناسب", callback_data="edu_9")],
        [InlineKeyboardButton("برگشت به منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# منوی دکمه‌های بلاگ (تغییر کرده)
def blog_menu():
    keyboard = [
        [InlineKeyboardButton("دریافت PDF جنگل خودتو بساز هیوا", callback_data="download_pdf")],
        [InlineKeyboardButton("بازگشت", callback_data="back_to_education")]
    ]
    return InlineKeyboardMarkup(keyboard)

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! به ربات هیوا خوش اومدی. یه گزینه رو انتخاب کن:", reply_markup=main_menu())

# مدیریت دکمه‌ها (تغییر کرده برای ارسال PDF)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "treatment":
        await query.edit_message_text("لطفاً نوع گیاهت یا مشکلی که داره رو توضیح بده و اگه می‌تونی یه عکس بفرست!")
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True  # برای پیام اولیه
        context.user_data["conversation"] = []  # شروع تاریخچه مکالمه
    elif choice == "care":
        await query.edit_message_text("لطفاً نوع گیاهت یا سوالی که در مورد نگهداریش داری رو بگو و اگه می‌تونی عکس بفرست!")
        context.user_data["section"] = "care"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
    elif choice == "education":
        await query.edit_message_text("یه موضوع آموزشی انتخاب کن:", reply_markup=education_menu())
    elif choice.startswith("edu_"):
        education_content = {
            "edu_1": """راهنمای جامع مبانی گیاه‌شناسی: هر آنچه برای نگهداری گیاهان باید بدانید! 🌿✨

مقدمه
گیاهان، علاوه بر زیبایی که به محیط می‌بخشند، هوای اطراف را تصفیه کرده و باعث ایجاد حس آرامش می‌شوند. برای داشتن گیاهانی سالم، باید نیازهای اساسی آن‌ها مثل نور، آب، خاک، دما و رطوبت رو بشناسید. این اصول پایه، شروع راه شماست برای تبدیل شدن به یه باغبون حرفه‌ای!""",
            "edu_2": """روش‌های آبیاری و تغذیه گیاهان 💧🌱

چرا آبیاری بیش از حد خطرناک است؟
یکی از دلایل اصلی مرگ گیاهان، آبیاری زیاد است. وقتی آب اضافی در خاک باقی بمونه، ریشه‌ها پوسیده می‌شن و گیاه از بین می‌ره.

چگونه بفهمیم گیاه به آب نیاز داره؟
✔️ انگشت خودتون رو ۲ تا ۳ سانتی‌متر توی خاک فرو ببرید. اگه خشک بود، وقت آبیاریه.
✔️ گلدان باید سوراخ زهکشی داشته باشه تا آب اضافی خارج بشه.

برنامه آبیاری:
- گیاهان آپارتمانی معمولی: هفته‌ای ۱ تا ۲ بار
- کاکتوس‌ها و ساکولنت‌ها: هر ۱۰ تا ۱۵ روز یه بار
- گیاهان رطوبت‌دوست (مثل سرخس): آبیاری بیشتر + اسپری آب

خاک و کود:
✔️ خاک آپارتمانی: خاک برگ + پرلیت + کوکوپیت
✔️ کوددهی: هر ۲ تا ۴ هفته با کود ۲۰-۲۰-۲۰ برای رشد بهتر.""",
            "edu_3": """تکثیر و پرورش گیاهان 🌿
تکثیر گیاهان یه راه عالی برای افزایش تعداد گیاهاتونه! دو روش اصلی وجود داره:

1. قلمه زدن:
✔️ یه ساقه سالم با ۲-۳ برگ انتخاب کنید.
✔️ اون رو توی آب یا خاک مرطوب بذارید تا ریشه بده.
✔️ بعد از ۲-۴ هفته، قلمه رو به گلدان منتقل کنید.

2. کاشت بذر:
✔️ بذرها رو توی خاک سبک بکارید و کمی آب بدید.
✔️ توی جای گرم و با نور غیرمستقیم نگه دارید تا جوانه بزنن.

نکته: صبر کلید موفقیته! بعضی گیاها مثل پتوس سریع ریشه می‌دن، ولی کاکتوس‌ها بیشتر طول می‌کشه.""",
            "edu_4": """کنترل آفات و بیماری‌ها 🐞
آفات و بیماری‌ها می‌تونن گیاهاتون رو نابود کنن، پس باید سریع عمل کنید!

آفات رایج:
✔️ شته‌ها: با آب و صابون ملایم بشوریدشون.
✔️ کنه تارعنکبوتی: برگ‌ها رو مرطوب نگه دارید و از سم کنه‌کش استفاده کنید.

بیماری‌ها:
✔️ پوسیدگی ریشه: آبیاری رو کم کنید و زهکشی رو چک کنید.
✔️ لکه‌های قارچی: برگ‌های بیمار رو جدا کنید و قارچ‌کش بزنید.

نکته: همیشه گیاهاتون رو منظم بررسی کنید تا مشکل زود پیدا بشه!""",
            "edu_5": """طراحی و نگهداری فضای سبز 🌳
برای داشتن یه فضای سبز قشنگ توی خونه یا باغچه:

✔️ گیاها رو بر اساس نیاز نورشون بچینید (آفتاب‌دوست‌ها کنار پنجره، سایه‌دوست‌ها توی گوشه).
✔️ از ترکیب گیاهان با ارتفاع و رنگ مختلف استفاده کنید.
✔️ هرس منظم کنید تا شکلشون حفظ بشه.

نکته: یه برنامه نگهداری هفتگی بذارید تا همیشه مرتب بمونن!""",
            "edu_6": """مشکلات رایج و راهکارها ⚠️
✔️ زرد شدن برگ‌ها: آبیاری زیاد یا کم، یا نور نامناسب.
✔️ رشد علفی (ساقه دراز و برگ‌های کوچک): نور کمه، گیاه رو به جای پرنور ببرید.
✔️ برگ‌های رنگ‌پریده: نور زیاد یا کمبود کود.

راه‌حل: نیاز گیاهتون رو بشناسید و شرایط رو تنظیم کنید!""",
            "edu_7": """روش‌های خاص نگهداری 🌡️
دما و رطوبت خیلی مهمه:
✔️ دمای ایده‌آل: ۱۸ تا ۲۵ درجه سانتی‌گراد
✔️ دمای بالا = پژمردگی
✔️ دمای پایین = سیاه شدن برگ‌ها

رطوبت برای گیاهان گرمسیری:
✔️ دستگاه بخور سرد
✔️ ظرف آب کنار گیاه
✔️ اسپری آب روی برگ‌ها""",
            "edu_8": """نور: مهم‌ترین فاکتور برای رشد گیاهان ☀️
گیاها بدون نور نمی‌تونن فتوسنتز کنن و رشدشون متوقف می‌شه.

چطور نور رو تنظیم کنیم؟
✔️ برگ‌ها به سمت نور کشیده شدن = نور کم
✔️ برگ‌ها زرد شدن = نور زیاد
✔️ رشد علفی = نور ناکافی

نیاز نوری گیاها:
✔️ آفتاب‌دوست (کاکتوس): ۴-۶ ساعت نور مستقیم
✔️ نیم‌سایه (پتوس): نور غیرمستقیم
✔️ سایه‌دوست (زامیفولیا): نور کم""",
            "edu_9": """گلدان مناسب 🏺
یه گلدان خوب باید:
✔️ سوراخ زهکشی داشته باشه.
✔️ اندازه‌ش درست باشه (خیلی بزرگ = پوسیدگی ریشه).
✔️ جنسش مناسب باشه:
- سفالی: زهکشی بالا
- پلاستیکی: حفظ رطوبت
- سرامیکی: قشنگ ولی زهکشی کمتر

نکته: هر بار گلدان رو فقط یه سایز بزرگ‌تر کنید."""
        }
        photo_urls = {
            "edu_1": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_2": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_3": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_4": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_5": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_6": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_7": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_8": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg",
            "edu_9": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg"
        }
        content = education_content.get(choice, "موضوع پیدا نشد!")
        photo_url = photo_urls.get(choice, None)
        
        if photo_url:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo_url,
                caption=content,
                reply_markup=blog_menu()
            )
    elif choice == "download_pdf":  # شرط جدید برای ارسال فایل
        pdf_path = "جنگل_خودتو_بساز_هیوا.pdf"  # مسیر فایل توی پوشه پروژه
        with open(pdf_path, 'rb') as pdf_file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=pdf_file,
                filename="جنگل_خودتو_بساز_هیوا.pdf",
                caption="اینم PDF جنگل خودتو بساز هیوا! امیدوارم به کارت بیاد 🌿"
            )
    elif choice == "back_to_main":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="سلام! به ربات هیوا خوش اومدی. یه گزینه رو انتخاب کن:",
            reply_markup=main_menu()
        )
        context.user_data.clear()  # پاک کردن تاریخچه موقع برگشت به منوی اصلی
    elif choice == "back_to_education":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="یه موضوع آموزشی انتخاب کن:",
            reply_markup=education_menu()
        )

# مدیریت متن‌ها
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    section = context.user_data.get("section", None)
    
    if user_id == int(ADMIN_ID):
        target_user_id = context.bot_data.get("last_user_id")
        if target_user_id:
            await context.bot.send_message(chat_id=target_user_id, text=update.message.text)
            await update.message.reply_text("جوابت برای کاربر فرستاده شد!")
        else:
            await update.message.reply_text("کاربری پیدا نشد! اول باید یه کاربر پیام بفرسته.")
    
    elif user_id != int(ADMIN_ID):
        context.bot_data["last_user_id"] = user_id
        print(f"آیدی کاربر ذخیره شد: {user_id}")
        
        if section in ["treatment", "care"]:
            # فقط بار اول پیام "صبر کن" رو نشون بده
            if context.user_data.get("first_message", True):
                loading_msg = await update.message.reply_text("یه لحظه صبر کن، دارم فکر می‌کنم!")
                context.user_data["first_message"] = False
            else:
                loading_msg = await update.message.reply_text("در حال فکر کردن...")
            
            try:
                # تاریخچه مکالمه رو بگیر یا بساز
                conversation = context.user_data.get("conversation", [])
                conversation.append({"role": "user", "content": update.message.text})
                
                # پرامپت با تاریخچه
                prompt = f"""
                تو یه متخصص گل و گیاه هستی. کاربر در مورد {section} گیاهش داره باهات حرف می‌زنه.
                این تاریخچه مکالمه‌ست: {conversation}.
                آخرین پیام کاربر: "{update.message.text}".
                به زبان فارسی، دوستانه و محترمانه جواب بده. اگه فکر می‌کنی برای جواب دقیق‌تر نیاز به اطلاعات بیشتر یا عکس داری، محترمانه بگو، وگرنه کامل جواب بده.
                """
                response = model.generate_content(prompt)
                answer_fa = response.text
                
                # اضافه کردن جواب به تاریخچه
                conversation.append({"role": "assistant", "content": answer_fa})
                context.user_data["conversation"] = conversation
                
                # پاک کردن پیام لودینگ و فرستادن جواب
                await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
                await update.message.reply_text(answer_fa)
            except Exception as e:
                await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
                await update.message.reply_text(f"خطا: {str(e)}. یه کم دیگه دوباره امتحان کن!")
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        else:
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
            await update.message.reply_text("پیامت رو برای ادمین فرستادم، لطفاً منتظر باش!")

# مدیریت عکس‌ها
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != int(ADMIN_ID):
        context.bot_data["last_user_id"] = user_id
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        await update.message.reply_text("عکس رو گرفتم! منتظر جواب متخصص باش.")
    else:
        target_user_id = context.bot_data.get("last_user_id")
        if target_user_id:
            await context.bot.send_photo(chat_id=target_user_id, photo=update.message.photo[-1].file_id, caption=update.message.caption or "")
            await update.message.reply_text("عکست برای کاربر فرستاده شد!")
        else:
            await update.message.reply_text("کاربری پیدا نشد!")

# اجرای ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
