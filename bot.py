from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import requests
import json
import os

# آیدی عددی تلگرام ادمین‌ها
ADMIN_IDS = ["1478363268", "6325733331"]

# توکن ربات
BOT_TOKEN = "7990694940:AAFAftck3lNCMdt4ts7LWfJEmqAxLu1r2g4"

# کلید API Gemini
GEMINI_API_KEY = "AIzaSyCPUX41Xo_N611S5ToS3eI-766Z7oHt2B4"

# مشخصات حساب برای کارت به کارت
CARD_INFO = "محمد باقری\n6219-8619-6996-9723"

# مسیر فایل برای ذخیره کاربرها
USERS_FILE = "users.json"

# تنظیم کلاینت Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# تابع برای ذخیره کاربرها
def save_user(user_id, contact=None):
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    
    users[str(user_id)] = {
        "user_id": user_id,
        "phone": contact.phone_number if contact else None,
        "first_name": contact.first_name if contact else None
    }
    
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
    print(f"کاربر {user_id} ذخیره شد")

# تابع برای گرفتن لیست کاربرها
def get_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# کیبورد ثابت برای دسته‌بندی‌ها
def main_reply_keyboard():
    keyboard = [
        ["درمان بیماری گیاهان", "نحوه نگهداری گیاهان"],
        ["آموزش", "محصولات"],
        ["ویزیت حضوری", "ویزیت آنلاین"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# منوی اصلی (اینلاین)
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

# منوی دسته‌بندی گیاهان برای نگهداری
def care_category_menu():
    keyboard = [
        [InlineKeyboardButton("گیاهان آپارتمانی", callback_data="care_apartment")],
        [InlineKeyboardButton("گیاهان دارویی", callback_data="care_medicinal")],
        [InlineKeyboardButton("گیاهان کشاورزی", callback_data="care_agricultural")],
        [InlineKeyboardButton("درختان", callback_data="care_trees")],
        [InlineKeyboardButton("گل‌ها", callback_data="care_flowers")],
        [InlineKeyboardButton("برگشت به منوی اصلی", callback_data="back_to_main")],
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
        [InlineKeyboardButton("نور و فتوسنتز", callback_data="edu_8")],
        [InlineKeyboardButton("انتخاب بستر کاشت", callback_data="edu_9")],
        [InlineKeyboardButton("برگشت به منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# منوی بلاگ
def blog_menu():
    keyboard = [
        [InlineKeyboardButton("دریافت PDF جنگل خودتو بساز هیوا", callback_data="download_pdf")],
        [InlineKeyboardButton("بازگشت", callback_data="back_to_education")],
        [InlineKeyboardButton("برگشت به منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users = get_users()
    
    if str(user_id) not in users:
        keyboard = [[KeyboardButton("اطلاعات تماس", request_contact=True)]]
        await update.message.reply_text(
            "سلام رفیق! به دستیار گل و گیاهت هیوا خوش اومدی 💚\nاولین بارته اینجایی؟ اطلاعات تماستو بفرست تا باهم رفیق شیم!",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        )
    else:
        await update.message.reply_text(
            "سلام رفیق قدیمی! 💚 چطور می‌تونم بهت کمک کنم؟ یه گزینه انتخاب کن:",
            reply_markup=main_reply_keyboard()
        )

# برگشت به منوی اصلی
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "برگشتی به خونه اصلی 🌱 یه گزینه انتخاب کن رفیق!",
        reply_markup=main_reply_keyboard()
    )

# مدیریت دکمه‌ها (اینلاین)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    print(f"دکمه زده شده: {choice}")
    
    if choice == "treatment":
        await query.edit_message_text(
            "چیزی درباره گیاهت بگو یا مشکِلشو بگو، اگه عکس داری هم بفرست ببینم چی به چیه! 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif choice == "care":
        await query.edit_message_text("چه گیاهی داری رفیق؟ 🌱 یه دسته‌بندی انتخاب کن:", reply_markup=care_category_menu())
    elif choice.startswith("care_"):
        category_map = {
            "care_apartment": "گیاهان آپارتمانی",
            "care_medicinal": "گیاهان دارویی",
            "care_agricultural": "گیاهان کشاورزی",
            "care_trees": "درختان",
            "care_flowers": "گل‌ها"
        }
        context.user_data["care_category"] = category_map[choice]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"درباره {context.user_data['care_category']} بگو، چه کمکی از رفیقت می‌خوای؟ 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "care"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif choice == "education":
        await query.edit_message_text("بیا یه چیزی یاد بگیریم رفیق! یه موضوع انتخاب کن:", reply_markup=education_menu())
    elif choice.startswith("edu_"):
        education_content = {
            "edu_1": """**مبانی اولیه گیاه‌شناسی** 🌿✨  
گیاها موجودات باحالی‌ان که با نور خورشید غذا درست می‌کنن! ریشه‌هاشون آب و غذا می‌گیره، ساقه‌ها مثل جاده عمل می‌کنن و برگ‌ها هم آشپزخونه‌شونه. مثلاً گیاهای آپارتمانی مثل *Spathiphyllum* عاشق رطوبت و نور کمن. سوالی داری رفیق؟ بپرس! 🌱""",
            "edu_2": """**روش‌های آبیاری و تغذیه گیاهان** 💧🌱  
هر گیاهی یه جور آب می‌خواد؛ مثلاً کاکتوسا هر دو هفته یه بار کافیه، ولی *Calathea* هی باید خاکش مرطوب باشه. کود هم که غذاشونه، نیتروژن برای برگا و فسفر برای ریشه‌ها! چیزی می‌خوای بدونی؟ بگو! 🌱""",
            "edu_3": """**تکثیر و پرورش گیاهان** 🌿  
می‌خوای گیاهاتو زیاد کنی؟ یا بذر بکار یا قلمه بزن! مثلاً *Pothos* رو با قلمه راحت می‌شه تکثیر کرد. بذر بعضی گیاها مثل *Lavandula* هم باید یه مدت سرما بخوره تا سبز بشه. سوالی داری رفیق؟ 🌱""",
            "edu_4": """**کنترل آفات و بیماری‌ها** 🐞  
اگه شپشک یا کنه دیدی، با حشره‌کش سیستمیک بندازشون بیرون! قارچ هم که اومد، تهویه رو درست کن و قارچ‌کش بزن. علائم رو بگو تا بیشتر راهنمایی کنم رفیق! 🌱""",
            "edu_5": """**طراحی و نگهداری فضای سبز** 🌳  
فضای سبز می‌خوای بسازی؟ باید خاک و نور رو بشناسی. مثلاً *Ficus* برای سایه خوبه، *Rosa* آفتاب می‌خواد. هرس و کود هم یادت نره! چیزی می‌خوای بدونی؟ 🌱""",
            "edu_6": """**مشکلات رایج و راهکارها** ⚠️  
برگ زرد شد؟ شاید آب زیاد دادی یا غذاش کمه. پژمرد؟ ریشه رو چک کن! بگو چی شده تا باهم حلش کنیم رفیق 🌱""",
            "edu_7": """**روش‌های خاص نگهداری** 🌡️  
بعضی گیاها حساسن، مثلاً ارکیده (*Phalaenopsis*) رطوبت بالا می‌خواد. *Saintpaulia* هم زیرگلدونی آب بده. سوالی داری؟ بپرس! 🌱""",
            "edu_8": """**نور و فتوسنتز** ☀️  
نور برای گیاها مثل بنزینه! *Asplenium* نور کم می‌خواد، ولی *Hibiscus* آفتاب‌دوستِ. نور کم باشه، ساقه‌ها دراز و ضعیف می‌شن. چیزی می‌خوای بدونی؟ 🌱""",
            "edu_9": """**انتخاب بستر کاشت** 🏺  
خاک خوب زهکشی می‌خواد، مثلاً پرلیت و کوکوپیت قاطی کن. pH هم مهمه، اکثر گیاها 6-7 رو دوست دارن. سوالی داری رفیق؟ 🌱"""
        }
        photo_urls = {
            "edu_1": "https://www.mediafire.com/view/hbd3ibb19ggw9gz/image.png/file",
            "edu_2": "https://www.mediafire.com/view/8v893e6yvaj5aif/image%25282%2529.png/file",
            "edu_3": "https://www.mediafire.com/view/3duk4d4trc08iqf/image%25283%2529.png/file",
            "edu_4": "https://www.mediafire.com/view/spax06s4q543ok2/image%25284%2529.png/file",
            "edu_5": "https://www.mediafire.com/view/pfquugyy0lw3sve/image%25285%2529.png/file",
            "edu_6": "https://www.mediafire.com/file/59xvp7h08nelzue/image.png/file",
            "edu_7": "https://www.mediafire.com/view/mpf7dzi34qlfhhd/image%25287%2529.png/file",
            "edu_8": "https://www.mediafire.com/view/tlfhpj31d4m1ipd/image%25288%2529.png/file",
            "edu_9": "https://www.mediafire.com/file/4gssc3hndnpj0ix/image.png/file"
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
    elif choice == "download_pdf":
        pdf_url = "https://raw.githubusercontent.com/Mamdism/PlantBot/main/جنگل_خودتو_بساز_هیوا.pdf"
        response = requests.get(pdf_url)
        if response.status_code == 200:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=response.content,
                filename="جنگل_خودتو_بساز_هیوا.pdf",
                caption="اینم PDF جنگل خودتو بساز هیوا! امیدوارم به کارت بیاد رفیق 🌿"
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="اوپس! یه مشکلی پیش اومد، نمی‌تونم PDF رو بفرستم. بعداً دوباره امتحان کن!"
            )
    elif choice == "products":
        await query.edit_message_text(
            "محصولاتمون رو اینجا ببین رفیق! کلی چیز باحال و تخفیف منتظرته 🥰",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به کانال 🌱", url="https://t.me/hiwagarden")]
            ])
        )
    elif choice == "visit_home":
        await query.edit_message_text(
            "ویزیت حضوری 🌿:\n"
            "• هر چی گیاهت لازم داره می‌گیم، تا ۲۰ تا گلدون رو چک می‌کنیم.\n"
            "• کود مناسبشم پیدا می‌کنیم.\n"
            "• فعلاً فقط رشت هستیم، ولی قراره کل ایرانو بگیریم 🌍\n"
            "• رشت نیستی؟ ویزیت آنلاینم داریم 💻\n"
            "• اگه خودت متخصص گل و گیاهی و می‌تونی ویزیت کنی، به @Hiwa_garden پیام بده 🌱\n"
            "• برای رزرو، ۲۰۰ تومن بیعانه بده.\n\n"
            "تعداد گیاهات و توضیحات رو بگو، بعد مشخصات و آدرستو بنویس:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "آدرس:\n"
            "هر خط یه بخش رو پر کن و بفرست رفیق!",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_home"
        context.user_data["awaiting_visit_home_info"] = True
    elif choice == "pay_visit_home_gateway":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="درگاه پرداخت بزودی میاد رفیق! فعلاً کارت به کارت کن!",
            reply_markup=main_reply_keyboard()
        )
    elif choice == "pay_visit_home_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"قابلتو نداره رفیق! ۲۰۰ تومن بیعانه بده به این کارت و رسیدشو بفرست:\n{CARD_INFO}",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_home"
    elif choice == "visit_online":
        await query.edit_message_text(
            "ویزیت آنلاین 🌱:\n"
            "• هر چی گیاهت بخواد می‌گیم، تا ۲۰ تا گلدون رو چک می‌کنیم.\n"
            "• کودشم برات پیدا می‌کنیم.\n"
            "• ۲۵۰ تومن بده تا رزرو کنیم.\n\n"
            "تعداد گیاهات و توضیحات رو بگو، بعد مشخصاتتو بنویس:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "هر خط یه بخش رو پر کن و بفرست رفیق!",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_online"
        context.user_data["awaiting_visit_online_info"] = True
    elif choice == "pay_visit_online_gateway":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="درگاه پرداخت بزودی میاد رفیق! فعلاً کارت به کارت کن!",
            reply_markup=main_reply_keyboard()
        )
    elif choice == "pay_visit_online_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"قابلتو نداره رفیق! ۲۵۰ تومن بده به این کارت و رسیدشو بفرست:\n{CARD_INFO}",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_online"
    elif choice == "back_to_main":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="سلام دوباره رفیق! 💚 یه گزینه انتخاب کن:",
            reply_markup=main_reply_keyboard()
        )

# مدیریت متن‌ها
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    section = context.user_data.get("section", None)
    text = update.message.text
    print(f"متن دریافت‌شده: {text}")
    
    # پیام ادمین به آخرین کاربر
    if str(user_id) in ADMIN_IDS:
        last_user_id = context.bot_data.get("last_user_id")
        if last_user_id:
            await context.bot.send_message(
                chat_id=last_user_id,
                text=update.message.text
            )
            print(f"پیام ادمین به کاربر {last_user_id} ارسال شد")
        else:
            await update.message.reply_text("هنوز کسی چیزی نگفته که جواب بدم رفیق!")
        return
    
    # مدیریت انتخاب از کیبورد ثابت
    if text == "درمان بیماری گیاهان":
        await update.message.reply_text(
            "چیزی درباره گیاهت بگو یا بگو چی شده، عکس داری بفرست ببینم! 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
        return
    elif text == "نحوه نگهداری گیاهان":
        await update.message.reply_text(
            "چه گیاهی داری رفیق؟ 🌱 یه دسته‌بندی انتخاب کن:",
            reply_markup=care_category_menu()
        )
        return
    elif text == "آموزش":
        await update.message.reply_text(
            "بیا یه چیزی یاد بگیریم رفیق! یه موضوع انتخاب کن:",
            reply_markup=education_menu()
        )
        return
    elif text == "محصولات":
        await update.message.reply_text(
            "محصولاتمون رو اینجا ببین رفیق! کلی چیز باحال و تخفیف منتظرته 🥰",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به کانال 🌱", url="https://t.me/hiwagarden")]
            ])
        )
        return
    elif text == "ویزیت حضوری":
        await update.message.reply_text(
            "ویزیت حضوری 🌿:\n"
            "• هر چی گیاهت لازم داره می‌گیم، تا ۲۰ تا گلدون رو چک می‌کنیم.\n"
            "• کود مناسبشم پیدا می‌کنیم.\n"
            "• فعلاً فقط رشت هستیم، ولی قراره کل ایرانو بگیریم 🌍\n"
            "• رشت نیستی؟ ویزیت آنلاینم داریم 💻\n"
            "• اگه خودت متخصص گل و گیاهی و می‌تونی ویزیت کنی، به @Hiwa_garden پیام بده 🌱\n"
            "• برای رزرو، ۲۰۰ تومن بیعانه بده.\n\n"
            "تعداد گیاهات و توضیحات رو بگو، بعد مشخصات و آدرستو بنویس:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "آدرس:\n"
            "هر خط یه بخش رو پر کن و بفرست رفیق!",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_home"
        context.user_data["awaiting_visit_home_info"] = True
        return
    elif text == "ویزیت آنلاین":
        await update.message.reply_text(
            "ویزیت آنلاین 🌱:\n"
            "• هر چی گیاهت بخواد می‌گیم، تا ۲۰ تا گلدون رو چک می‌کنیم.\n"
            "• کودشم برات پیدا می‌کنیم.\n"
            "• ۲۵۰ تومن بده تا رزرو کنیم.\n\n"
            "تعداد گیاهات و توضیحات رو بگو، بعد مشخصاتتو بنویس:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "هر خط یه بخش رو پر کن و بفرست رفیق!",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_online"
        context.user_data["awaiting_visit_online_info"] = True
        return
    
    # بقیه منطق برای آدرس و ویزیت‌ها
    if section == "visit_home" and context.user_data.get("awaiting_visit_home_info", False):
        text_lines = text.split("\n")
        print(f"اطلاعات ویزیت حضوری دریافت‌شده: {text_lines}")
        if len(text_lines) >= 3:
            context.user_data["visit_home_info"] = {
                "plants": text_lines[0],
                "name": text_lines[1],
                "phone": text_lines[2],
                "address": "\n".join(text_lines[3:]) if len(text_lines) > 3 else ""
            }
            context.user_data["awaiting_visit_home_info"] = False
            await update.message.reply_text("مرسی رفیق! حالا لوکیشنتو بفرست 🌍", reply_markup=main_reply_keyboard())
        else:
            await update.message.reply_text("تعداد گیاها، اسم، شماره و آدرس رو توی حداقل ۳ خط بفرست رفیق!", reply_markup=main_reply_keyboard())
        return
    
    if section == "visit_online" and context.user_data.get("awaiting_visit_online_info", False):
        text_lines = text.split("\n")
        print(f"اطلاعات ویزیت آنلاین دریافت‌شده: {text_lines}")
        if len(text_lines) >= 2:
            context.user_data["visit_online_info"] = {
                "plants": text_lines[0],
                "name": text_lines[1],
                "phone": text_lines[2] if len(text_lines) > 2 else ""
            }
            context.user_data["awaiting_visit_online_info"] = False
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"درخواست ویزیت آنلاین از کاربر با آیدی: {user_id}\n"
                             f"تعداد گیاهان و توضیحات: {visit_info['plants']}\n"
                             f"نام: {visit_info['name']}\n"
                             f"شماره: {visit_info['phone']}"
                    )
                    print(f"اطلاعات ویزیت آنلاین به ادمین {admin_id} ارسال شد")
                except Exception as e:
                    print(f"خطا در ارسال اطلاعات ویزیت آنلاین به ادمین {admin_id}: {e}")
            await update.message.reply_text(
                "مرسی رفیق! حالا چطور می‌خوای پرداخت کنی؟",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("پرداخت از درگاه", callback_data="pay_visit_online_gateway")],
                    [InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_online_card")]
                ])
            )
        else:
            await update.message.reply_text("تعداد گیاها، اسم و شماره رو توی حداقل ۲ خط بفرست رفیق!", reply_markup=main_reply_keyboard())
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id  # ذخیره آخرین کاربر
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    if section in ["treatment", "care"]:
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
                print(f"متن به ادمین {admin_id} فوروارد شد (بخش: {section})")
            except Exception as e:
                print(f"خطا در فوروارد متن به ادمین {admin_id}: {e}")
        
        if context.user_data.get("first_message", True):
            loading_msg = await update.message.reply_text("یه لحظه صبر کن رفیق، دارم فکر می‌کنم... 🌱")
            context.user_data["first_message"] = False
        else:
            loading_msg = await update.message.reply_text("بذار ببینم چی می‌تونم بگم... 🌿")
        
        try:
            conversation = context.user_data.get("conversation", [])
            conversation.append({"role": "user", "content": text})
            
            prompt = f"""
            تو یه متخصص گیاه‌شناسی باحال و رفیق‌گونه هستی که همه‌چیز درباره گیاها می‌دونی: آپارتمانی، دارویی، کشاورزی، درختا، گل‌ها، همه‌شو! قراره به سوالای کاربر با دقت و حال خوب جواب بدی، انگار داری با رفیقت چت می‌کنی. دانشت عمیقه و جوابات همیشه درست و کاربردیه.

            اصول رفیقانه‌ات:
            - دقیق باش: همیشه درست و علمی بگو، ولی سخت نگیر!
            - همه‌چیزو بگو: هر چی به سوال ربط داره رو پوشش بده.
            - ساده حرف بزن: انگار داری برای رفیقت توضیح می‌دی، نه استاد دانشگاه!
            - راهکار عملی بده: چیزی بگو که بشه راحت انجامش داد.
            - به حرفای کاربر دقت کن: جزئیاتو از دست نده.
            - سوالای باحال بپرس: مثلاً "چند وقت یه بار آبش می‌دی رفیق؟" یا "نورش چطوره؟"
            - تشخیص دقیق نمی‌دی: بگو که بدون دیدن گیاه فقط حدس می‌زنم.
            - مثل رفیق باش: صمیمی، با حال، گاهی یه شوخی کوچیک بنداز!
            - اموجی باحال بزن: مثل 🌱، 💧، ☀️، 🐞 که چت زنده بشه.
            - کوتاه و شیرین: جوابات طولانی نباشه، سریع برو سر اصل مطلب.
            - عکس یا فایل بخواه: اگه هنوز نفرستاده بگو "یه عکس بنداز ببینم!"، اگه فرستاده دیگه نپرس.
            - چت رو ادامه بده: انگار داری مکالمه رو جلو می‌بری، نه فقط جواب می‌دی.
            - بخش درمان: درباره مشکل گیاه سوالای کوتاه و باحال بپرس.
            - بخش نگهداری: بگو اسمشو بگه و سوالای ساده درباره نگهداری بپرس.

            کاربر داره درباره {section} گیاهش حرف می‌زنه.
            {f"دسته‌بندی گیاه: {context.user_data.get('care_category', 'مشخص نشده')}" if section == "care" else ""}
            تاریخچه چت: {conversation}.
            آخرین پیامش: "{text}".
            عکس یا فایل فرستاده؟ {"بله" if context.user_data.get('has_photo', False) else "خیر"}.
            به فارسی، مثل یه رفیق باحال و صمیمی جواب بده!
            """
            response = model.generate_content(prompt)
            answer_fa = response.text
            
            conversation.append({"role": "assistant", "content": answer_fa})
            context.user_data["conversation"] = conversation
            
            await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
            await update.message.reply_text(answer_fa, reply_markup=main_reply_keyboard())
        except Exception as e:
            await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
            await update.message.reply_text(f"اوپس! یه خطا خوردم رفیق: {str(e)}. دوباره بگو ببینم! ⚠️", reply_markup=main_reply_keyboard())

# مدیریت عکس‌ها
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    section = context.user_data.get("section", None)
    if str(user_id) in ADMIN_IDS:
        print(f"عکس از ادمین ({user_id}) بود، نادیده گرفته شد")
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    if context.user_data.get("awaiting_receipt", False) and section in ["visit_home", "visit_online"]:
        pending_type = context.user_data.get("pending_type")
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"رسید پرداخت از کاربر با آیدی: {user_id} (نوع: {pending_type})"
                )
                print(f"رسید پرداخت به ادمین {admin_id} فوروارد شد (نوع: {pending_type})")
            except Exception as e:
                print(f"خطا در فوروارد رسید به ادمین {admin_id}: {e}")
        await update.message.reply_text(
            "رسیدتو گرفتم رفیق! ادمینا چک کنن باهات تماس می‌گیرن. مرسی که انتخابمون کردی 💚",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = False
        context.user_data.pop("pending_type", None)
    elif section in ["treatment", "care"]:
        context.user_data["has_photo"] = True
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
                print(f"عکس درمان/نگهداری به ادمین {admin_id} فوروارد شد (بخش: {section})")
            except Exception as e:
                print(f"خطا در فوروارد عکس به ادمین {admin_id}: {e}")
        await update.message.reply_text(
            "عکستو برای متخصصمون فرستادم رفیق! بزودی جوابتو می‌دم 🫰🏼",
            reply_markup=main_reply_keyboard()
        )
    else:
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
                print(f"عکس نامشخص به ادمین {admin_id} فوروارد شد")
            except Exception as e:
                print(f"خطا در فوروارد عکس به ادمین {admin_id}: {e}")
        await update.message.reply_text(
            "عکستو گرفتم رفیق، ولی نمی‌دونم باهاش چیکار کنم! یه توضیح بده ببینم 🌱",
            reply_markup=main_reply_keyboard()
        )

# مدیریت فایل‌ها (جدید)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    section = context.user_data.get("section", None)
    if str(user_id) in ADMIN_IDS:
        print(f"فایل از ادمین ({user_id}) بود، نادیده گرفته شد")
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    file = update.message.document
    file_type = file.mime_type
    
    if context.user_data.get("awaiting_receipt", False) and section in ["visit_home", "visit_online"]:
        pending_type = context.user_data.get("pending_type")
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"رسید پرداخت (فایل) از کاربر با آیدی: {user_id} (نوع: {pending_type})"
                )
                print(f"رسید پرداخت (فایل) به ادمین {admin_id} فوروارد شد (نوع: {pending_type})")
            except Exception as e:
                print(f"خطا در فوروارد فایل به ادمین {admin_id}: {e}")
        await update.message.reply_text(
            "فایل رسیدتو گرفتم رفیق! ادمینا چک کنن باهات تماس می‌گیرن. مرسی که باهامون هستی 💚",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = False
        context.user_data.pop("pending_type", None)
    elif section in ["treatment", "care"] and file_type.startswith("image/"):
        context.user_data["has_photo"] = True
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
                print(f"فایل عکس درمان/نگهداری به ادمین {admin_id} فوروارد شد (بخش: {section})")
            except Exception as e:
                print(f"خطا در فوروارد فایل عکس به ادمین {admin_id}: {e}")
        await update.message.reply_text(
            "عکسو به‌صورت فایل فرستادی رفیق! برای متخصصمون فرستادم، بزودی جواب می‌دم 🫰🏼",
            reply_markup=main_reply_keyboard()
        )
    else:
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
                print(f"فایل نامشخص به ادمین {admin_id} فوروارد شد")
            except Exception as e:
                print(f"خطا در فوروارد فایل به ادمین {admin_id}: {e}")
        await update.message.reply_text(
            "فایلتو گرفتم رفیق، ولی نمی‌دونم چیه! یه توضیح بده که بفهمم چیکارش کنم 🌱",
            reply_markup=main_reply_keyboard()
        )

# مدیریت لوکیشن
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) in ADMIN_IDS:
        print(f"لوکیشن از ادمین ({user_id}) بود، نادیده گرفته شد")
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    if context.user_data.get("section") == "visit_home" and "visit_home_info" in context.user_data:
        context.user_data["visit_home_info"]["location"] = update.message.location
        await update.message.reply_text(
            "مرسی رفیق! حالا چطور می‌خوای پرداخت کنی؟",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پرداخت از درگاه", callback_data="pay_visit_home_gateway")],
                [InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_home_card")]
            ])
        )
        visit_info = context.user_data["visit_home_info"]
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"درخواست ویزیت حضوری از کاربر با آیدی: {user_id}\n"
                         f"تعداد گیاهان و توضیحات: {visit_info['plants']}\n"
                         f"نام: {visit_info['name']}\n"
                         f"شماره: {visit_info['phone']}\n"
                         f"آدرس: {visit_info['address']}"
                )
                await context.bot.send_location(
                    chat_id=admin_id,
                    latitude=update.message.location.latitude,
                    longitude=update.message.location.longitude
                )
                print(f"اطلاعات و لوکیشن با موفقیت به ادمین {admin_id} ارسال شد")
            except Exception as e:
                print(f"خطا در ارسال اطلاعات و لوکیشن به ادمین {admin_id}: {e}")

# مدیریت تماس
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    contact = update.message.contact
    save_user(user_id, contact)
    await update.message.reply_text(
        "مرسی رفیق! حالا دیگه توی جمع مایی 🌱 یه گزینه انتخاب کن:",
        reply_markup=main_reply_keyboard()
    )

# اجرای ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.bot.delete_webhook()
    print("وب‌هوک با موفقیت حذف شد")
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", back_to_menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # اضافه کردن مدیریت فایل‌ها
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"یه خطا پیش اومد: {context.error}")
        if update and hasattr(update, "message") and update.message:
            await update.message.reply_text("اوپس! یه مشکلی پیش اومد رفیق، دوباره امتحان کن! ⚠️", reply_markup=main_reply_keyboard())
        elif update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.message.reply_text("اوپس! یه مشکلی پیش اومد رفیق، دوباره امتحان کن! ⚠️", reply_markup=main_reply_keyboard())
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
