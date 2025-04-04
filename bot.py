from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import requests
import json
import os

# آیدی عددی تلگرام ادمین
ADMIN_ID = "1478363268"

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
        keyboard = [[KeyboardButton("اشتراک تماس", request_contact=True)]]
        await update.message.reply_text(
            "به دستیار گل و گیاهتون هیوا خوش اومدین💚\nلطفاً برای ثبت‌نام، تماس خودت رو اشتراک کن:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        )
    else:
        await update.message.reply_text(
            "به دستیار گل و گیاهتون هیوا خوش اومدین💚\nیه گزینه رو انتخاب کن:",
            reply_markup=main_reply_keyboard()
        )

# برگشت به منوی اصلی
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "برگشتی به منوی اصلی 🌱 یه گزینه انتخاب کن:",
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
            "لطفاً نوع گیاهت یا مشکلی که داره رو توضیح بده و اگه می‌تونی یه عکس بفرست! 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif choice == "care":
        await query.edit_message_text("چه نوع گیاهی داری؟ 🌱 یه دسته‌بندی انتخاب کن:", reply_markup=care_category_menu())
    elif choice.startswith("care_"):
        category_map = {
            "care_apartment": "گیاهان آپارتمانی",
            "care_medicinal": "گیاهان دارویی",
            "care_agricultural": "گیاهان کشاورزی",
            "care_trees": "درختان",
            "care_flowers": "گل‌ها"
        }
        context.user_data["care_category"] = category_map[choice]
        await query.edit_message_text(
            f"درباره {context.user_data['care_category']} بگو، چه کمکی می‌خوای؟ 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "care"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif choice == "education":
        await query.edit_message_text("یه موضوع آموزشی انتخاب کن:", reply_markup=education_menu())
    elif choice.startswith("edu_"):
        education_content = {
            "edu_1": """**مبانی اولیه گیاه‌شناسی** 🌿✨  
گیاهان به عنوان موجودات فتوسنتزکننده، از ساختارهای تخصصی مثل ریشه، ساقه، برگ و بافت‌های آوندی (آوند چوبی و آبکشی) تشکیل شدن که هر کدوم وظایف مشخصی دارن. ریشه‌ها آب و مواد معدنی رو جذب می‌کنن، ساقه‌ها مواد رو منتقل می‌کنن و برگ‌ها با استفاده از کلروفیل و نور خورشید، گلوکز تولید می‌کنن. شناخت خانواده‌های گیاهی (مثل Liliaceae یا Asteraceae) و نیازهای اکولوژیک اون‌ها برای مدیریت بهتر ضروریه. مثلاً گیاهان آپارتمانی مثل *Spathiphyllum* به رطوبت بالا و نور غیرمستقیم نیاز دارن. سوالی داری؟ از هوش مصنوعی هیوا بپرس! 🌱""",
            "edu_2": """**روش‌های آبیاری و تغذیه گیاهان** 💧🌱  
آبیاری باید بر اساس نیاز هیدرولیکی گیاه تنظیم بشه؛ مثلاً گونه‌های خشکی‌پسند (*Succulents*) به فاصله آبیاری 10-14 روزه نیاز دارن، در حالی که گیاهان رطوبت‌دوست مثل *Calathea* به خاک مرطوب مداوم وابسته‌ان. تغذیه با کودهای ماکرو (N، P، K) و میکرو (Fe، Zn) باید بر اساس فاز رشد (رویشی یا زایشی) انجام بشه. مثلاً نیتروژن برای رشد برگ‌ها و فسفر برای ریشه‌زایی حیاتیه. از محلول‌پاشی هم می‌شه برای تأمین سریع عناصر استفاده کرد. سوالی داری؟ بپرس! 🌱""",
            "edu_3": """**تکثیر و پرورش گیاهان** 🌿  
تکثیر گیاهی شامل روش‌های جنسی (بذر) و غیرجنسی (قلمه، پیوند، خوابانیدن) می‌شه. قلمه‌زنی ساقه در گونه‌هایی مثل *Pothos* با هورمون ریشه‌زایی (مثل IAA) سریع‌تر ریشه می‌ده. برای بذر، جوانه‌زنی به دما، رطوبت و گاهی تیمارهایی مثل خیساندن یا سرمادهی نیاز داره. مثلاً بذر *Lavandula* قبل از کاشت باید 30 روز در 4 درجه سانتی‌گراد استراتیفیه بشه. تکثیر موفق به ژنتیک و شرایط محیطی بستگی داره. سوالی داری؟ بپرس! 🌱""",
            "edu_4": """**کنترل آفات و بیماری‌ها** 🐞  
آفاتی مثل شپشک آردی (*Pseudococcidae*) یا کنه تارتن (*Tetranychidae*) با حشره‌کش‌های سیستمیک (مثل ایمیداکلوپرید) کنترل می‌شن. بیماری‌های قارچی مثل *Botrytis cinerea* به تهویه و قارچ‌کش‌هایی مثل مانکوزب نیاز دارن. تشخیص اولیه با بررسی علائم (لکه‌های نکروزه، پودر سفید و ...) شروع می‌شه. مدیریت تلفیقی (IPM) شامل کنترل بیولوژیک (مثل کفشدوزک) و شیمیاییه. سوالی داری؟ بپرس! 🌱""",
            "edu_5": """**طراحی و نگهداری فضای سبز** 🌳  
طراحی فضای سبز به عواملی مثل اقلیم، توپوگرافی و نوع خاک بستگی داره. مثلاً در خاک رسی، زهکشی مصنوعی لازمه. انتخاب گونه‌ها (مثل *Ficus elastica* برای سایه یا *Rosa* برای آفتاب) باید با نور و آب منطقه سازگار باشه. نگهداری شامل هرس فرم‌دهی، کوددهی سالانه (مثل 10-10-10) و کنترل علف‌های هرزه. هدف، تعادل اکوسیستمی و زیباییه. سوالی داری؟ بپرس! 🌱""",
            "edu_6": """**مشکلات رایج و راهکارها** ⚠️  
زردی برگ‌ها (کلروز) می‌تونه از کمبود نیتروژن، آهن یا آبیاری بیش از حد باشه؛ تست pH خاک (ایده‌آل 6-7) و EC کمک‌کننده‌ست. پژمردگی ممکنه به کم‌آبی یا پوسیدگی ریشه (*Pythium*) برگرده. برگ‌ریزان هم گاهی به شوک دمایی یا آفات ریشه‌خوار ربط داره. با آزمایش خاک و مشاهده دقیق، راهکار پیدا می‌شه. سوالی داری؟ بپرس! 🌱""",
            "edu_7": """**روش‌های خاص نگهداری** 🌡️  
گونه‌هایی مثل *Phalaenopsis* (ارکیده) به رطوبت 60-80% و بستر کاشت خزه اسفاگنوم نیاز دارن. *Saintpaulia* (بنفشه آفریقایی) به آبیاری زیرگلدانی و دمای 20-25 درجه وابسته‌ست. تنظیم EC آب (زیر 1.5 dS/m) و دمای ریشه هم برای رشد بهینه مهمه. هر گیاه یه میکروکلیمات خاص می‌خواد. سوالی داری؟ بپرس! 🌱""",
            "edu_8": """**نور و فتوسنتز** ☀️  
فتوسنتز به شدت نور (PAR بین 400-700 نانومتر) و مدت تابش بستگی داره. گیاهان سایه‌پسند مثل *Asplenium* در 1000-2000 لوکس رشد می‌کنن، ولی گونه‌های آفتاب‌دوست (*Hibiscus*) به 5000 لوکس نیاز دارن. کمبود نور باعث اتیوله شدن (بلند و ضعیف شدن ساقه) می‌شه. از لامپ‌های LED رشد هم می‌شه استفاده کرد. سوالی داری؟ بپرس! 🌱""",
            "edu_9": """**انتخاب بستر کاشت** 🏺  
بستر کاشت باید زهکشی مناسب (مثل پرلیت یا ورمی‌کولیت) و ظرفیت نگهداری آب (مثل پیت‌ماس) داشته باشه. pH خاک برای اکثر گیاهان 6-7 ایده‌آله، ولی گونه‌های اسیددوست (*Azalea*) به 4.5-5.5 نیاز دارن. ترکیب 50% کوکوپیت، 30% پرلیت و 20% خاک برگ برای آپارتمانی‌ها مناسبه. تست خاک قبل از کاشت ضروریه. سوالی داری؟ بپرس! 🌱"""
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
                caption="اینم PDF جنگل خودتو بساز هیوا! امیدوارم به کارت بیاد 🌿"
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="مشکلی پیش اومد! نمی‌تونم PDF رو بفرستم. بعداً دوباره امتحان کن."
            )
    elif choice == "products":
        await query.edit_message_text(
            "محصولاتمون رو اینجا ببین:",  # پیام کوتاه
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به کانال 🌱", url="https://t.me/hiwagarden")]
            ])
        )
    elif choice == "visit_home":
        await query.edit_message_text(
            "ویزیت حضوری 🌿:\n"
            "موارد لازم واسه هر گیاه گفته می‌شه و حداکثر ۲۰ تا گلدون بررسی می‌شه.\n"
            "بررسی کودهای مورد نیاز هم انجام می‌شه.\n\n"
            "لطفاً تعداد گیاهان و توضیحات رو بنویس و بعد مشخصات و آدرس رو وارد کن:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "آدرس:\n"
            "هر خط یه بخش رو پر کن و بفرست.",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_home"
        context.user_data["awaiting_visit_home_info"] = True
    elif choice == "pay_visit_home_gateway":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="درگاه پرداخت بزودی فعال می‌شه!",
            reply_markup=main_reply_keyboard()
        )
    elif choice == "pay_visit_home_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"قابلتونو نداره مبلغ ۲۰۰ هزار تومان باید برای بیعانه پرداخت کنید\nلطفاً مبلغ رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_home"
    elif choice == "visit_online":
        await query.edit_message_text(
            "ویزیت آنلاین 🌱:\n"
            "موارد لازم واسه هر گیاه گفته می‌شه و حداکثر ۲۰ تا گلدون بررسی می‌شه.\n"
            "بررسی کودهای مورد نیاز هم انجام می‌شه.\n\n"
            "لطفاً تعداد گیاهان و توضیحات رو بنویس و بعد مشخصات رو وارد کن:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "هر خط یه بخش رو پر کن و بفرست.",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_online"
        context.user_data["awaiting_visit_online_info"] = True
    elif choice == "pay_visit_online_gateway":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="درگاه پرداخت بزودی فعال می‌شه!",
            reply_markup=main_reply_keyboard()
        )
    elif choice == "pay_visit_online_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"قابلتونو نداره مبلغ ۲۵۰ هزار تومان باید برای بیعانه پرداخت کنید\nلطفاً مبلغ رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_online"
    elif choice == "back_to_main":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="به دستیار گل و گیاهتون هیوا خوش اومدین💚\nیه گزینه رو انتخاب کن:",
            reply_markup=main_reply_keyboard()
        )

# مدیریت متن‌ها
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    section = context.user_data.get("section", None)
    text = update.message.text
    print(f"متن دریافت‌شده: {text}")
    
    # پیام ادمین به آخرین کاربر
    if str(user_id) == ADMIN_ID:
        last_user_id = context.bot_data.get("last_user_id")
        if last_user_id:
            await context.bot.send_message(
                chat_id=last_user_id,
                text=update.message.text
            )
            print(f"پیام ادمین به کاربر {last_user_id} ارسال شد")
        else:
            await update.message.reply_text("هنوز کاربری پیام نفرستاده که جواب بدم!")
        return
    
    # مدیریت انتخاب از کیبورد ثابت
    if text == "درمان بیماری گیاهان":
        await update.message.reply_text(
            "لطفاً نوع گیاهت یا مشکلی که داره رو توضیح بده و اگه می‌تونی یه عکس بفرست! 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
        return
    elif text == "نحوه نگهداری گیاهان":
        await update.message.reply_text(
            "چه نوع گیاهی داری؟ 🌱 یه دسته‌بندی انتخاب کن:",
            reply_markup=care_category_menu()
        )
        return
    elif text == "آموزش":
        await update.message.reply_text(
            "یه موضوع آموزشی انتخاب کن:",
            reply_markup=education_menu()
        )
        return
    elif text == "محصولات":
        await update.message.reply_text(
            "محصولاتمون رو اینجا ببین:",  # پیام کوتاه
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به کانال 🌱", url="https://t.me/hiwagarden")]
            ])
        )
        return
    elif text == "ویزیت حضوری":
        await update.message.reply_text(
            "ویزیت حضوری 🌿:\n"
            "موارد لازم واسه هر گیاه گفته می‌شه و حداکثر ۲۰ تا گلدون بررسی می‌شه.\n"
            "بررسی کودهای مورد نیاز هم انجام می‌شه.\n\n"
            "لطفاً تعداد گیاهان و توضیحات رو بنویس و بعد مشخصات و آدرس رو وارد کن:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "آدرس:\n"
            "هر خط یه بخش رو پر کن و بفرست.",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_home"
        context.user_data["awaiting_visit_home_info"] = True
        return
    elif text == "ویزیت آنلاین":
        await update.message.reply_text(
            "ویزیت آنلاین 🌱:\n"
            "موارد لازم واسه هر گیاه گفته می‌شه و حداکثر ۲۰ تا گلدون بررسی می‌شه.\n"
            "بررسی کودهای مورد نیاز هم انجام می‌شه.\n\n"
            "لطفاً تعداد گیاهان و توضیحات رو بنویس و بعد مشخصات رو وارد کن:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "هر خط یه بخش رو پر کن و بفرست.",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_online"
        context.user_data["awaiting_visit_online_info"] = True
        return
    
    # بقیه منطق برای آدرس و ویزیت‌ها
    if context.user_data.get("awaiting_visit_home_info", False):
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
            await update.message.reply_text("ممنون! حالا لوکیشنتو بفرست 🌍", reply_markup=main_reply_keyboard())
        else:
            await update.message.reply_text("لطفاً تعداد گیاهان، نام، شماره و آدرس رو توی حداقل ۳ خط بفرست!", reply_markup=main_reply_keyboard())
        return
    
    if context.user_data.get("awaiting_visit_online_info", False):
        text_lines = text.split("\n")
        print(f"اطلاعات ویزیت آنلاین دریافت‌شده: {text_lines}")
        if len(text_lines) >= 2:
            context.user_data["visit_online_info"] = {
                "plants": text_lines[0],
                "name": text_lines[1],
                "phone": text_lines[2] if len(text_lines) > 2 else ""
            }
            context.user_data["awaiting_visit_online_info"] = False
            await update.message.reply_text(
                "ممنون! حالا مبلغ ۲۵۰ هزار تومان رو پرداخت کن:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("پرداخت از درگاه", callback_data="pay_visit_online_gateway")],
                    [InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_online_card")]
                ])
            )
        else:
            await update.message.reply_text("لطفاً تعداد گیاهان، نام و شماره رو توی حداقل ۲ خط بفرست!", reply_markup=main_reply_keyboard())
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id  # ذخیره آخرین کاربر
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    if section in ["treatment", "care"]:
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        print(f"متن به ادمین فوروارد شد (بخش: {section})")
        
        if context.user_data.get("first_message", True):
            loading_msg = await update.message.reply_text("در حال فکر کردن... 🌱")
            context.user_data["first_message"] = False
        else:
            loading_msg = await update.message.reply_text("در حال فکر کردن... 🌿")
        
        try:
            conversation = context.user_data.get("conversation", [])
            conversation.append({"role": "user", "content": text})
            
            prompt = f"""
            شما یک متخصص گیاه‌شناسی بسیار آگاه و با تجربه هستید که دانش عمیقی در زمینه‌های مختلف گیاهان از جمله گیاهان آپارتمانی، گیاهان دارویی، گیاهان کشاورزی، درختان، گل‌ها و سایر انواع گیاهان دارید. شما قادر به پاسخگویی دقیق و جامع به سوالات کاربران در مورد شناسایی گیاهان، نحوه نگهداری صحیح، مشکلات و بیماری‌های گیاهان، روش‌های تکثیر، خواص گیاهان دارویی و هر موضوع مرتبط دیگر هستید.

            اصول پاسخگویی شما:
            - دقت و صحت: همواره پاسخ‌های دقیق و مبتنی بر دانش علمی ارائه دهید.
            - جامعیت: تمام جوانب سوال کاربر را پوشش دهید.
            - وضوح و سادگی: از زبانی ساده و قابل فهم استفاده کنید.
            - راهنمایی عملی: راهکارهای عملی و قابل اجرا ارائه دهید.
            - توجه به جزئیات: به جزئیات مطرح‌شده توسط کاربر توجه کنید.
            - پرسش‌های تکمیلی: در صورت نیاز سوالات تکمیلی بپرس مثل "چند روز در هفته آبیاری می‌کنی؟" یا "خاکش چطوره؟".
            - احتیاط در تشخیص: یادآوری کنید که تشخیص دقیق بدون مشاهده مستقیم ممکن نیست.
            - لحن دوستانه: با لحنی صمیمی و مشتاق به کمک پاسخ دهید.
            - از اموجی‌های مرتبط مثل 🌱، 💧، ☀️، 🐞 استفاده کن.
            - پاسخ‌ها کوتاه‌تر باشن: جوابات رو سعی کن خیلی طولانی نباشن، سوالات کوتاه و دوستانه بپرس.
            - درخواست عکس: اگه کاربر هنوز عکس نفرستاده، آخر پیام ازش بخواه عکس بفرسته. اگه عکس فرستاده، دیگه درخواست نکن.
            - بخش درمان: سوالات کوتاه درباره مشکل گیاه بپرس.
            - بخش نگهداری: سوالات کوتاه درباره نگهداری بپرس و اسم گیاه رو بپرس.

            کاربر در مورد {section} گیاهش داره حرف می‌زنه.
            {f"دسته‌بندی گیاه: {context.user_data.get('care_category', 'مشخص نشده')}" if section == "care" else ""}
            تاریخچه مکالمه: {conversation}.
            آخرین پیام کاربر: "{text}".
            آیا کاربر عکس فرستاده؟ {"بله" if context.user_data.get('has_photo', False) else "خیر"}.
            به فارسی، دوستانه و محترمانه جواب بده.
            """
            response = model.generate_content(prompt)
            answer_fa = response.text
            
            conversation.append({"role": "assistant", "content": answer_fa})
            context.user_data["conversation"] = conversation
            
            await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
            await update.message.reply_text(answer_fa, reply_markup=main_reply_keyboard())
        except Exception as e:
            await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
            await update.message.reply_text(f"خطا: {str(e)}. دوباره امتحان کن! ⚠️", reply_markup=main_reply_keyboard())

# مدیریت عکس‌ها
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    section = context.user_data.get("section", None)
    if str(user_id) == ADMIN_ID:
        print(f"عکس از ادمین ({user_id}) بود، نادیده گرفته شد")
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id  # ذخیره آخرین کاربر
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    if context.user_data.get("awaiting_receipt", False):
        pending_type = context.user_data.get("pending_type")
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"رسید پرداخت از کاربر با آیدی: {user_id} (نوع: {pending_type})"
        )
        await update.message.reply_text(
            "رسیدت رو دریافت کردیم و در صورت تایید توسط ادمین باهاتون جهت هماهنگی تماس می‌گیریم؛ تشکر از انتخابتون 💚",
            reply_markup=main_reply_keyboard()
        )
        print(f"رسید پرداخت به ادمین فوروارد شد (نوع: {pending_type})")
        context.user_data["awaiting_receipt"] = False
    elif section in ["treatment", "care"]:
        context.user_data["has_photo"] = True  # کاربر عکس فرستاده
        await update.message.reply_text(
            "برای متخصصمون فرستادم، بزودی بهت جواب می‌دیم 🫰🏼",
            reply_markup=main_reply_keyboard()
        )
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        print("عکس درمان/نگهداری به ادمین فوروارد شد")
    else:
        await update.message.reply_text(
            "عکس رو گرفتم، ولی نمی‌دونم چی باهاش کنم! لطفاً توضیح بده 🌱",
            reply_markup=main_reply_keyboard()
        )
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        print("عکس نامشخص به ادمین فوروارد شد")

# مدیریت لوکیشن
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) == ADMIN_ID:
        print(f"لوکیشن از ادمین ({user_id}) بود، نادیده گرفته شد")
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id  # ذخیره آخرین کاربر
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    if context.user_data.get("section") == "visit_home" and "visit_home_info" in context.user_data:
        context.user_data["visit_home_info"]["location"] = update.message.location
        await update.message.reply_text(
            "ممنون ازت! حالا بیعانه ۲۰۰ هزار تومان رو پرداخت کن:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پرداخت از درگاه", callback_data="pay_visit_home_gateway")],
                [InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_home_card")]
            ])
        )
        try:
            visit_info = context.user_data["visit_home_info"]
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"درخواست ویزیت حضوری از کاربر با آیدی: {user_id}\n"
                     f"تعداد گیاهان و توضیحات: {visit_info['plants']}\n"
                     f"نام: {visit_info['name']}\n"
                     f"شماره: {visit_info['phone']}\n"
                     f"آدرس: {visit_info['address']}"
            )
            await context.bot.send_location(
                chat_id=ADMIN_ID,
                latitude=update.message.location.latitude,
                longitude=update.message.location.longitude
            )
            print("اطلاعات و لوکیشن با موفقیت به ادمین ارسال شد")
        except Exception as e:
            print(f"خطا در ارسال اطلاعات و لوکیشن به ادمین: {e}")

# مدیریت تماس
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    contact = update.message.contact
    save_user(user_id, contact)
    await update.message.reply_text(
        "ممنون! حالا ثبت شدی 🌱 یه گزینه انتخاب کن:",
        reply_markup=main_reply_keyboard()
    )

# اجرای ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # حذف وب‌هوک قبل از شروع polling
    app.bot.delete_webhook()
    print("وب‌هوک با موفقیت حذف شد")
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", back_to_menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"یه خطا پیش اومد: {context.error}")
        if update and hasattr(update, "message") and update.message:
            await update.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن ⚠️", reply_markup=main_reply_keyboard())
        elif update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن ⚠️", reply_markup=main_reply_keyboard())
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
