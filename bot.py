import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import requests
import json
import os
from aiohttp import web
import telegram.error

# تنظیم لاگ برای عیب‌یابی
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# آیدی عددی تلگرام ادمین‌ها
ADMIN_IDS = ["1478363268", "6325733331"]

# توکن و کلید API از متغیرهای محیطی
BOT_TOKEN = os.getenv("BOT_TOKEN", "7990694940:AAFAftck3lNCMdt4ts7LWfJEmqAxLu1r2g4")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCPUX41Xo_N611S5ToS3eI-766Z7oHt2B4")

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
    logger.info(f"کاربر {user_id} ذخیره شد")

# تابع برای گرفتن لیست کاربرها
def get_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# کیبورد ثابت برای دسته‌بندی‌ها
def main_reply_keyboard():
    return ReplyKeyboardMarkup([
        ["درمان بیماری گیاهان", "نحوه نگهداری گیاهان"],
        ["آموزش", "محصولات"],
        ["ویزیت حضوری", "ویزیت آنلاین"],
    ], resize_keyboard=True, one_time_keyboard=False)

# منوی اصلی (اینلاین)
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("درمان بیماری گیاهان", callback_data="treatment")],
        [InlineKeyboardButton("نحوه نگهداری گیاهان", callback_data="care")],
        [InlineKeyboardButton("آموزش", callback_data="education")],
        [InlineKeyboardButton("محصولات", callback_data="products")],
        [InlineKeyboardButton("ویزیت حضوری", callback_data="visit_home")],
        [InlineKeyboardButton("ویزیت آنلاین", callback_data="visit_online")],
    ])

# منوی دسته‌بندی گیاهان برای نگهداری
def care_category_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("گیاهان آپارتمانی", callback_data="care_apartment")],
        [InlineKeyboardButton("گیاهان دارویی", callback_data="care_medicinal")],
        [InlineKeyboardButton("گیاهان کشاورزی", callback_data="care_agricultural")],
        [InlineKeyboardButton("درختان", callback_data="care_trees")],
        [InlineKeyboardButton("گل‌ها", callback_data="care_flowers")],
        [InlineKeyboardButton("برگشت به منوی اصلی", callback_data="back_to_main")],
    ])

# منوی آموزش
def education_menu():
    return InlineKeyboardMarkup([
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
    ])

# منوی بلاگ
def blog_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("دریافت PDF جنگل خودتو بساز هیوا", callback_data="download_pdf")],
        [InlineKeyboardButton("بازگشت", callback_data="back_to_education")],
        [InlineKeyboardButton("برگشت به منوی اصلی", callback_data="back_to_main")],
    ])

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info(f"فرمان /start از کاربر {user_id} دریافت شد")
    users = get_users()
    
    if str(user_id) not in users:
        keyboard = [[KeyboardButton("اطلاعات تماس", request_contact=True)]]
        await update.message.reply_text(
            "سلام! به دستیار گل و گیاهتون هیوا خوش اومدید 💚\nبرای شروع، لطفاً اطلاعات تماستون رو بفرستید تا ثبت‌نام بشید!",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        )
    else:
        await update.message.reply_text(
            "سلام! خوش اومدید به هیوا 💚 چطور می‌تونم بهتون کمک کنم؟ یه گزینه انتخاب کنید:",
            reply_markup=main_reply_keyboard()
        )

# برگشت به منوی اصلی
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("برگشتید به منوی اصلی 🌱 یه گزینه انتخاب کنید!", reply_markup=main_reply_keyboard())

# مدیریت دکمه‌ها (اینلاین)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    logger.info(f"دکمه زده شده: {choice}")
    
    if choice == "treatment":
        await query.edit_message_text(
            "لطفاً درباره گیاهتون یا مشکلی که داره بگید، اگه عکسی هم دارید بفرستید تا بهتر بتونم کمک کنم! 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif choice == "care":
        await query.edit_message_text("چه نوع گیاهی دارید؟ 🌱 یه دسته‌بندی انتخاب کنید:", reply_markup=care_category_menu())
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
            text=f"درباره {context.user_data['care_category']} بگید، چه کمکی می‌تونم بهتون بکنم؟ 🌿",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "care"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif choice == "education":
        await query.edit_message_text("یه موضوع آموزشی انتخاب کنید تا باهم یاد بگیریم:", reply_markup=education_menu())
    elif choice.startswith("edu_"):
        education_content = {
            "edu_1": """**مبانی اولیه گیاه‌شناسی** 🌿  
گیاهان با نور خورشید غذا درست می‌کنن و بخش‌های مختلفی مثل ریشه، ساقه و برگ دارن. ریشه آب و مواد غذایی می‌گیره، ساقه منتقل می‌کنه و برگ‌ها انرژی تولید می‌کنن. مثلاً گیاهان آپارتمانی مثل *Spathiphyllum* به رطوبت و نور غیرمستقیم نیاز دارن. سوالی دارید؟ بپرسید! 🌱""",
            "edu_2": """**روش‌های آبیاری و تغذیه گیاهان** 💧  
هر گیاهی نیاز آبی خاص خودشو داره؛ مثلاً کاکتوس‌ها هر دو هفته یه بار آب می‌خوان، ولی *Calathea* خاکش باید همیشه مرطوب باشه. کود هم برای رشدشون مهمه، نیتروژن برای برگ‌ها و فسفر برای ریشه‌ها. سوالی هست؟ بگید! 🌱"""
        }
        photo_urls = {
            "edu_1": "https://www.mediafire.com/view/hbd3ibb19ggw9gz/image.png/file",
            "edu_2": "https://www.mediafire.com/view/8v893e6yvaj5aif/image%25282%2529.png/file"
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
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text=content, reply_markup=blog_menu())
    elif choice == "download_pdf":
        pdf_url = "https://raw.githubusercontent.com/Mamdism/PlantBot/main/جنگل_خودتو_بساز_هیوا.pdf"
        response = requests.get(pdf_url)
        if response.status_code == 200:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=response.content,
                filename="جنگل_خودتو_بساز_هیوا.pdf",
                caption="اینم PDF جنگل خودتو بساز هیوا! امیدوارم به کارتون بیاد 🌿"
            )
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="مشکلی پیش اومد و نمی‌تونم PDF رو بفرستم!")
    elif choice == "products":
        await query.edit_message_text(
            "محصولاتمون رو اینجا ببینید! 🥰",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ورود به کانال 🌱", url="https://t.me/hiwagarden")]])
        )
    elif choice == "visit_home":
        await query.edit_message_text(
            "ویزیت حضوری 🌿:\nلطفاً تعداد گیاهان و توضیحات رو بنویسید و بعد مشخصات و آدرستون رو بفرستید:\nنام و نام خانوادگی:\nشماره تلفن:\nآدرس:",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_home"
        context.user_data["awaiting_visit_home_info"] = True
    elif choice == "visit_online":
        await query.edit_message_text(
            "ویزیت آنلاین 🌱:\nلطفاً تعداد گیاهان و توضیحات رو بنویسید و بعد مشخصاتتون رو بفرستید:\nنام و نام خانوادگی:\nشماره تلفن:",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_online"
        context.user_data["awaiting_visit_online_info"] = True
    elif choice == "pay_visit_home_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"لطفاً ۲۰۰ هزار تومن بیعانه رو به این کارت واریز کنید و رسیدش رو بفرستید:\n{CARD_INFO}",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_home"
    elif choice == "pay_visit_online_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"لطفاً ۲۵۰ هزار تومن رو به این کارت واریز کنید و رسیدش رو بفرستید:\n{CARD_INFO}",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_online"
    elif choice == "back_to_main":
        context.user_data.clear()
        await context.bot.send_message(chat_id=query.message.chat_id, text="سلام دوباره! 💚 یه گزینه انتخاب کنید:", reply_markup=main_reply_keyboard())

# مدیریت متن‌ها
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text
    section = context.user_data.get("section", None)
    logger.info(f"متن دریافت‌شده از کاربر {user_id}: {text}")
    
    if str(user_id) in ADMIN_IDS:
        last_user_id = context.bot_data.get("last_user_id")
        if last_user_id:
            await context.bot.send_message(chat_id=last_user_id, text=text)
            logger.info(f"پیام ادمین به کاربر {last_user_id} ارسال شد")
        return
    
    if text == "درمان بیماری گیاهان":
        await update.message.reply_text("لطفاً درباره گیاهتون یا مشکلی که داره بگید! 🌿", reply_markup=main_reply_keyboard())
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif text == "نحوه نگهداری گیاهان":
        await update.message.reply_text("چه نوع گیاهی دارید؟ 🌱 یه دسته‌بندی انتخاب کنید:", reply_markup=care_category_menu())
    elif text == "آموزش":
        await update.message.reply_text("یه موضوع آموزشی انتخاب کنید:", reply_markup=education_menu())
    elif text == "محصولات":
        await update.message.reply_text(
            "محصولاتمون رو اینجا ببینید! 🥰",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ورود به کانال 🌱", url="https://t.me/hiwagarden")]])
        )
    elif text == "ویزیت حضوری":
        await update.message.reply_text(
            "ویزیت حضوری 🌿:\nلطفاً تعداد گیاهان و توضیحات رو بنویسید و بعد مشخصات و آدرستون رو بفرستید:\nنام و نام خانوادگی:\nشماره تلفن:\nآدرس:",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_home"
        context.user_data["awaiting_visit_home_info"] = True
    elif text == "ویزیت آنلاین":
        await update.message.reply_text(
            "ویزیت آنلاین 🌱:\nلطفاً تعداد گیاهان و توضیحات رو بنویسید و بعد مشخصاتتون رو بفرستید:\nنام و نام خانوادگی:\nشماره تلفن:",
            reply_markup=main_reply_keyboard()
        )
        context.user_data["section"] = "visit_online"
        context.user_data["awaiting_visit_online_info"] = True
    elif section == "visit_home" and context.user_data.get("awaiting_visit_home_info", False):
        text_lines = text.split("\n")
        if len(text_lines) >= 3:
            context.user_data["visit_home_info"] = {
                "plants": text_lines[0],
                "name": text_lines[1],
                "phone": text_lines[2],
                "address": "\n".join(text_lines[3:]) if len(text_lines) > 3 else ""
            }
            context.user_data["awaiting_visit_home_info"] = False
            await update.message.reply_text(
                "ممنون! حالا نحوه پرداخت رو انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_home_card")]])
            )
        else:
            await update.message.reply_text("لطفاً تعداد گیاهان، اسم، شماره و آدرس رو توی حداقل ۳ خط بفرستید!")
    elif section == "visit_online" and context.user_data.get("awaiting_visit_online_info", False):
        text_lines = text.split("\n")
        if len(text_lines) >= 2:
            context.user_data["visit_online_info"] = {
                "plants": text_lines[0],
                "name": text_lines[1],
                "phone": text_lines[2] if len(text_lines) > 2 else ""
            }
            context.user_data["awaiting_visit_online_info"] = False
            await update.message.reply_text(
                "ممنون! حالا نحوه پرداخت رو انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_online_card")]])
            )
        else:
            await update.message.reply_text("لطفاً تعداد گیاهان، اسم و شماره رو توی حداقل ۲ خط بفرستید!")
    elif section in ["treatment", "care"]:
        context.user_data["user_id"] = user_id
        context.bot_data["last_user_id"] = user_id
        for admin_id in ADMIN_IDS:
            await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
        loading_msg = await update.message.reply_text("یه لحظه صبر کنید... 🌱")
        conversation = context.user_data.get("conversation", [])
        conversation.append({"role": "user", "content": text})
        prompt = f"تو یه متخصص گیاه‌شناسی هستی. کاربر داره درباره {section} گیاهش حرف می‌زنه. پیامش: '{text}'. به فارسی و صمیمی جواب بده!"
        response = model.generate_content(prompt)
        answer_fa = response.text
        conversation.append({"role": "assistant", "content": answer_fa})
        context.user_data["conversation"] = conversation
        await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
        await update.message.reply_text(answer_fa, reply_markup=main_reply_keyboard())

# مدیریت عکس‌ها
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    section = context.user_data.get("section", None)
    logger.info(f"عکس از کاربر {user_id} دریافت شد")
    if str(user_id) in ADMIN_IDS:
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id
    
    if context.user_data.get("awaiting_receipt", False) and section in ["visit_home", "visit_online"]:
        pending_type = context.user_data.get("pending_type")
        for admin_id in ADMIN_IDS:
            await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
            await context.bot.send_message(chat_id=admin_id, text=f"رسید پرداخت از کاربر {user_id} (نوع: {pending_type})")
        await update.message.reply_text("رسیدتون رو گرفتم! بعد از تأیید ادمین باهاتون تماس می‌گیرن. 💚", reply_markup=main_reply_keyboard())
        context.user_data["awaiting_receipt"] = False
        context.user_data.pop("pending_type", None)
    elif section in ["treatment", "care"]:
        context.user_data["has_photo"] = True
        for admin_id in ADMIN_IDS:
            await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
        await update.message.reply_text("عکستون رو برای متخصصمون فرستادم! به‌زودی جواب می‌دم 🌱", reply_markup=main_reply_keyboard())

# مدیریت فایل‌ها
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    section = context.user_data.get("section", None)
    if str(user_id) in ADMIN_IDS:
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id
    
    file = update.message.document
    file_type = file.mime_type
    
    if context.user_data.get("awaiting_receipt", False) and section in ["visit_home", "visit_online"]:
        pending_type = context.user_data.get("pending_type")
        for admin_id in ADMIN_IDS:
            await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
            await context.bot.send_message(chat_id=admin_id, text=f"رسید پرداخت (فایل) از کاربر {user_id} (نوع: {pending_type})")
        await update.message.reply_text("فایل رسیدتون رو گرفتم! بعد از تأیید ادمین باهاتون تماس می‌گیرن. 💚", reply_markup=main_reply_keyboard())
        context.user_data["awaiting_receipt"] = False
        context.user_data.pop("pending_type", None)
    elif section in ["treatment", "care"] and file_type.startswith("image/"):
        context.user_data["has_photo"] = True
        for admin_id in ADMIN_IDS:
            await context.bot.forward_message(chat_id=admin_id, from_chat_id=user_id, message_id=update.message.message_id)
        await update.message.reply_text("عکس رو به‌صورت فایل فرستادید! برای متخصصمون فرستادم، به‌زودی جواب می‌دم 🌱", reply_markup=main_reply_keyboard())

# مدیریت لوکیشن
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) in ADMIN_IDS:
        return
    
    context.user_data["user_id"] = user_id
    context.bot_data["last_user_id"] = user_id
    
    if context.user_data.get("section") == "visit_home" and "visit_home_info" in context.user_data:
        context.user_data["visit_home_info"]["location"] = update.message.location
        await update.message.reply_text(
            "ممنون! حالا نحوه پرداخت رو انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_home_card")]])
        )
        visit_info = context.user_data["visit_home_info"]
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"درخواست ویزیت حضوری از کاربر {user_id}\nتعداد گیاهان: {visit_info['plants']}\nنام: {visit_info['name']}\nشماره: {visit_info['phone']}\nآدرس: {visit_info['address']}"
            )
            await context.bot.send_location(chat_id=admin_id, latitude=update.message.location.latitude, longitude=update.message.location.longitude)

# مدیریت تماس
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    contact = update.message.contact
    save_user(user_id, contact)
    await update.message.reply_text("ممنون! حالا جزو خانواده ما شدید 🌱 یه گزینه انتخاب کنید:", reply_markup=main_reply_keyboard())

# تابع Webhook Handler
async def webhook_handler(request):
    logger.info("درخواست Webhook دریافت شد")
    try:
        update = Update.de_json(await request.json(), app.bot)
        if update:
            logger.info(f"آپدیت دریافت شد: {update.update_id}")
            await app.process_update(update)
        else:
            logger.warning("آپدیت نامعتبر بود")
    except Exception as e:
        logger.error(f"خطا در پردازش Webhook: {e}")
    return web.Response(text="OK")

# اجرای ربات
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", back_to_menu))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
app.add_handler(MessageHandler(filters.LOCATION, handle_location))
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

async def main():
    await app.initialize()
    await app.start()
    
    # حذف وب‌هوک قبلی
    await app.bot.delete_webhook(drop_pending_updates=True)
    logger.info("وب‌هوک قبلی حذف شد")
    
    # تنظیم پورت و دامنه برای Railway
    port = int(os.getenv("PORT", 8080))
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "plantbot.up.railway.app")  # دامنه پیش‌فرض
    webhook_url = f"https://{domain}/webhook"
    logger.info(f"تلاش برای تنظیم وب‌هوک با URL: {webhook_url}")
    
    # تنظیم وب‌هوک با مدیریت خطا
    try:
        await app.bot.set_webhook(url=webhook_url)
        logger.info(f"وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
    except telegram.error.TelegramError as e:
        logger.error(f"خطا در تنظیم وب‌هوک: {e}")
        return
    
    # راه‌اندازی سرور
    web_app = web.Application()
    web_app.router.add_post('/webhook', webhook_handler)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"سرور روی پورت {port} اجرا شد")
    
    # حلقه برای نگه داشتن برنامه
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
