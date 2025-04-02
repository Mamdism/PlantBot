from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import requests
import json

# آیدی عددی تلگرام ادمین
ADMIN_ID = "1478363268"

# توکن ربات
BOT_TOKEN = "7990694940:AAFAftck3lNCMdt4ts7LWfJEmqAxLu1r2g4"

# کلید API Gemini
GEMINI_API_KEY = "AIzaSyCPUX41Xo_N611S5ToS3eI-766Z7oHt2B4"

# مشخصات حساب برای کارت به کارت
CARD_INFO = "محمد باقری\n6219-8619-6996-9723"

# تنظیم کلاینت Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

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

# منوی دسته‌بندی گیاهان برای نگهداری
def care_category_menu():
    keyboard = [
        [InlineKeyboardButton("گیاهان آپارتمانی", callback_data="care_apartment")],
        [InlineKeyboardButton("گیاهان دارویی", callback_data="care_medicinal")],
        [InlineKeyboardButton("گیاهان کشاورزی", callback_data="care_agricultural")],
        [InlineKeyboardButton("درختان", callback_data="care_trees")],
        [InlineKeyboardButton("گل‌ها", callback_data="care_flowers")],
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

# منوی بلاگ
def blog_menu():
    keyboard = [
        [InlineKeyboardButton("دریافت PDF جنگل خودتو بساز هیوا", callback_data="download_pdf")],
        [InlineKeyboardButton("بازگشت", callback_data="back_to_education")]
    ]
    return InlineKeyboardMarkup(keyboard)

# منوی محصولات
def products_menu():
    keyboard = [
        [InlineKeyboardButton("گیاهان", callback_data="cat_plants")],
        [InlineKeyboardButton("خاک", callback_data="cat_soil")],
        [InlineKeyboardButton("گلدان", callback_data="cat_pots")],
        [InlineKeyboardButton("بذر", callback_data="cat_seeds")],
        [InlineKeyboardButton("کود", callback_data="cat_fertilizers")],
        [InlineKeyboardButton("ملزومات باغبانی", callback_data="cat_tools")],
        [InlineKeyboardButton("برگشت به منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# گرفتن محصولات از فایل JSON
async def fetch_products(context: ContextTypes.DEFAULT_TYPE, category: str):
    print(f"در حال بررسی محصولات برای دسته‌بندی: {category}")
    try:
        with open("products.json", "r", encoding="utf-8") as file:
            all_products = json.load(file)
            products = all_products.get(category, [])
            print(f"محصولات پیدا شده برای {category}: {products}")
            return products
    except FileNotFoundError:
        print("فایل products.json پیدا نشد، محصول تستی برمی‌گردونم")
        return [{
            "name": "کاکتوس تستی",
            "size": "کوچک",
            "color": "سبز",
            "stock": 5,
            "price": 50000,
            "photo_url": "https://www.mediafire.com/convkey/5e46/ejxbgzriujkkg116g.jpg"
        }]
    except Exception as e:
        print(f"خطا در خوندن فایل JSON: {e}")
        return []

# نمایش رسید خرید محصول
async def show_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("ورود به تابع show_receipt")
    product_name = context.user_data.get("selected_product")
    category = context.user_data.get("selected_category")
    if not product_name or not category:
        await update.message.reply_text("مشکلی پیش اومد! محصول یا دسته‌بندی انتخاب نشده.")
        print("خطا: محصول یا دسته‌بندی در context.user_data نیست")
        return
    
    products = await fetch_products(context, category)
    try:
        product = next(p for p in products if p["name"] == product_name)
        print(f"محصول پیدا شده: {product}")
    except StopIteration:
        print(f"خطا: محصول {product_name} توی دسته‌بندی {category} پیدا نشد!")
        await update.message.reply_text(f"مشکلی پیش اومد! محصول '{product_name}' توی دسته‌بندی '{category}' پیدا نشد.")
        return
    
    receipt = (f"رسید خرید:\n"
               f"محصول: {product_name}\n"
               f"**هزینه گیاه: {product['price']} تومان**\n"
               f"هزینه ارسال: پسکرایه\n"
               f"مشخصات:\n"
               f"نام: {context.user_data['address']['name']}\n"
               f"شماره: {context.user_data['address']['phone']}\n"
               f"آدرس: {context.user_data['address']['province']}، {context.user_data['address']['city']}، {context.user_data['address']['address']}\n"
               f"کدپستی: {context.user_data['address']['postal_code']}")
    
    keyboard = [
        [InlineKeyboardButton("پرداخت از درگاه", callback_data="pay_gateway")],
        [InlineKeyboardButton("کارت به کارت", callback_data="pay_card")]
    ]
    await update.message.reply_text(receipt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    print("رسید با موفقیت به کاربر ارسال شد")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"سفارش جدید:\n{receipt}", parse_mode="Markdown")
    print("رسید برای ادمین ارسال شد")

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! به ربات هیوا خوش اومدی 🌱 یه گزینه رو انتخاب کن:", reply_markup=main_menu())

# برگشت به منوی اصلی
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("برگشتی به منوی اصلی 🌱 یه گزینه انتخاب کن:", reply_markup=main_menu())

# مدیریت دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    print(f"دکمه زده شده: {choice}")
    
    if choice == "treatment":
        await query.edit_message_text("لطفاً نوع گیاهت یا مشکلی که داره رو توضیح بده و اگه می‌تونی یه عکس بفرست! 🌿")
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
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
        await query.edit_message_text(f"درباره {context.user_data['care_category']} بگو، چه کمکی می‌خوای؟ 🌿")
        context.user_data["section"] = "care"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
    elif choice == "education":
        await query.edit_message_text("یه موضوع آموزشی انتخاب کن:", reply_markup=education_menu())
    elif choice.startswith("edu_"):
        education_content = {
            "edu_1": """راهنمای جامع مبانی گیاه‌شناسی: هر آنچه برای نگهداری گیاهان باید بدانید! 🌿✨ ...""",
            "edu_2": """روش‌های آبیاری و تغذیه گیاهان 💧🌱 ...""",
            "edu_3": """تکثیر و پرورش گیاهان 🌿 ...""",
            "edu_4": """کنترل آفات و بیماری‌ها 🐞 ...""",
            "edu_5": """طراحی و نگهداری فضای سبز 🌳 ...""",
            "edu_6": """مشکلات رایج و راهکارها ⚠️ ...""",
            "edu_7": """روش‌های خاص نگهداری 🌡️ ...""",
            "edu_8": """نور: مهم‌ترین فاکتور برای رشد گیاهان ☀️ ...""",
            "edu_9": """گلدان مناسب 🏺 ..."""
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
        await query.edit_message_text("یه دسته‌بندی انتخاب کن:", reply_markup=products_menu())
    elif choice.startswith("cat_"):
        category_map = {
            "cat_plants": "گیاهان",
            "cat_soil": "خاک",
            "cat_pots": "گلدان",
            "cat_seeds": "بذر",
            "cat_fertilizers": "کود",
            "cat_tools": "ملزومات باغبانی"
        }
        category = category_map[choice]
        context.user_data["selected_category"] = category
        products = await fetch_products(context, category)
        if not products:
            await query.edit_message_text("محصولی توی این دسته‌بندی پیدا نشد!")
            return
        
        for product in products:
            caption = (f"نام: {product['name']}\n"
                       f"سایز: {product['size']}\n"
                       f"رنگ: {product['color']}\n"
                       f"تعداد موجود: {product['stock']}\n"
                       f"**قیمت: {product['price']} تومان**")
            keyboard = [[InlineKeyboardButton("خرید", callback_data=f"buy_{product['name']}")]]
            if "photo_url" in product and product["photo_url"]:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=product["photo_url"],
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=caption,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
    elif choice.startswith("buy_"):
        product_name = choice.replace("buy_", "")
        print(f"محصول انتخاب‌شده برای خرید: {product_name}")
        context.user_data["selected_product"] = product_name
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="لطفاً مشخصات و آدرس رو وارد کن:\n"
                 "نام و نام خانوادگی:\n"
                 "شماره تلفن:\n"
                 "استان:\n"
                 "شهر:\n"
                 "آدرس:\n"
                 "کدپستی:\n"
                 "هر خط یه بخش رو پر کن و بفرست."
        )
        context.user_data["awaiting_address"] = True
        print("پیام درخواست آدرس ارسال شد")
    elif choice == "pay_gateway":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="درگاه پرداخت بزودی فعال می‌شه!"
        )
    elif choice == "pay_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"لطفاً مبلغ رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}"
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "product"
        print("منتظر دریافت عکس رسید از کاربر")
    elif choice == "visit_home":
        await query.edit_message_text(
            "ویزیت حضوری 🌿:\n"
            "موارد لازم واسه هر گیاه گفته می‌شه و حداکثر ۲۰ تا گلدون بررسی می‌شه.\n"
            "بررسی کودهای مورد نیاز هم انجام می‌شه.\n\n"
            "لطفاً تعداد گیاهان و توضیحات رو بنویس و بعد مشخصات و آدرس رو وارد کن:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "آدرس:\n"
            "هر خط یه بخش رو پر کن و بفرست."
        )
        context.user_data["section"] = "visit_home"
        context.user_data["awaiting_visit_home_info"] = True
    elif choice == "pay_visit_home_gateway":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="درگاه پرداخت بزودی فعال می‌شه!"
        )
    elif choice == "pay_visit_home_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"لطفاً مبلغ ۲۰۰ هزار تومان رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}"
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
            "هر خط یه بخش رو پر کن و بفرست."
        )
        context.user_data["section"] = "visit_online"
        context.user_data["awaiting_visit_online_info"] = True
    elif choice == "pay_visit_online_gateway":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="درگاه پرداخت بزودی فعال می‌شه!"
        )
    elif choice == "pay_visit_online_card":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"لطفاً مبلغ ۲۵۰ هزار تومان رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}"
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_online"
    elif choice == "back_to_main":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="سلام! به ربات هیوا خوش اومدی 🌱 یه گزینه رو انتخاب کن:",
            reply_markup=main_menu()
        )
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
    print(f"متن دریافت‌شده: {update.message.text}")
    
    if context.user_data.get("awaiting_address", False):
        text = update.message.text.split("\n")
        print(f"اطلاعات آدرس دریافت‌شده: {text}")
        if len(text) == 6:
            context.user_data["address"] = {
                "name": text[0],
                "phone": text[1],
                "province": text[2],
                "city": text[3],
                "address": text[4],
                "postal_code": text[5]
            }
            context.user_data["awaiting_address"] = False
            print("آدرس با موفقیت ذخیره شد:")
            print(context.user_data["address"])
            await show_receipt(update, context)
        else:
            await update.message.reply_text("لطفاً همه‌ی اطلاعات رو توی ۶ خط بفرست!")
        return
    
    if context.user_data.get("awaiting_visit_home_info", False):
        text = update.message.text.split("\n")
        print(f"اطلاعات ویزیت حضوری دریافت‌شده: {text}")
        if len(text) >= 3:
            context.user_data["visit_home_info"] = {
                "plants": text[0],
                "name": text[1],
                "phone": text[2],
                "address": "\n".join(text[3:]) if len(text) > 3 else ""
            }
            context.user_data["awaiting_visit_home_info"] = False
            await update.message.reply_text("ممنون! حالا لوکیشنتو بفرست 🌍")
        else:
            await update.message.reply_text("لطفاً تعداد گیاهان، نام، شماره و آدرس رو توی حداقل ۳ خط بفرست!")
        return
    
    if context.user_data.get("awaiting_visit_online_info", False):
        text = update.message.text.split("\n")
        print(f"اطلاعات ویزیت آنلاین دریافت‌شده: {text}")
        if len(text) >= 2:
            context.user_data["visit_online_info"] = {
                "plants": text[0],
                "name": text[1],
                "phone": text[2] if len(text) > 2 else ""
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
            await update.message.reply_text("لطفاً تعداد گیاهان، نام و شماره رو توی حداقل ۲ خط بفرست!")
        return
    
    if user_id == int(ADMIN_ID):
        if update.message.reply_to_message and hasattr(update.message.reply_to_message, "forward_from") and update.message.reply_to_message.forward_from:
            target_user_id = update.message.reply_to_message.forward_from.id
            text = update.message.text.strip()
            
            if context.user_data.get("awaiting_receipt", False):
                pending_type = context.user_data.get("pending_type")
                
                if pending_type == "product":
                    category = context.user_data.get("selected_category")
                    product_name = context.user_data.get("selected_product")
                    if text.startswith("تایید"):
                        category_messages = {
                            "گیاهان": "گیاه جدیدت مبارکت باشه! 🌱 سفارشت با موفقیت ثبت شد.\nسوالی داری ازم بپرس؟",
                            "خاک": "خاک جدیدت مبارکت باشه! 🌿 سفارشت با موفقیت ثبت شد.\nسوالی داری ازم بپرس؟",
                            "گلدان": "گلدان جدیدت مبارکت باشه! 🏺 سفارشت با موفقیت ثبت شد.\nسوالی داری ازم بپرس؟",
                            "بذر": "بذر جدیدت مبارکت باشه! 🌾 سفارشت با موفقیت ثبت شد.\nسوالی داری ازم بپرس؟",
                            "کود": "کود جدیدت مبارکت باشه! 💪 سفارشت با موفقیت ثبت شد.\nسوالی داری ازم بپرس؟",
                            "ملزومات باغبانی": "ابزار جدیدت مبارکت باشه! 🛠️ سفارشت با موفقیت ثبت شد.\nسوالی داری ازم بپرس؟"
                        }
                        message = category_messages.get(category, "خریدت مبارکت باشه! 🎉 سفارشت با موفقیت ثبت شد.\nسوالی داری ازم بپرس؟")
                        await context.bot.send_message(chat_id=target_user_id, text=message)
                        await update.message.reply_text(f"سفارش '{product_name}' تایید شد و پیام به کاربر ارسال شد.")
                        context.user_data["awaiting_receipt"] = False
                    elif text.startswith("تایید نشد"):
                        reason = text.replace("تایید نشد", "").strip() or "دلیل مشخص نشده"
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=f"سفارشت تایید نشد 😔\nدلیل: {reason}\nسوالی داری ازم بپرس؟"
                        )
                        await update.message.reply_text(f"سفارش '{product_name}' تایید نشد و دلیل به کاربر ارسال شد.")
                        context.user_data["awaiting_receipt"] = False
                
                elif pending_type == "visit_home":
                    if text.startswith("تایید"):
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text="رزرو وقت ویزیت حضوری برای شما با موفقیت انجام شد 🌿 بزودی با شما تماس گرفته خواهد شد.\nسوالی داری ازم بپرس؟"
                        )
                        await update.message.reply_text("ویزیت حضوری تایید شد و پیام به کاربر ارسال شد.")
                        context.user_data["awaiting_receipt"] = False
                    elif text.startswith("تایید نشد"):
                        reason = text.replace("تایید نشد", "").strip() or "دلیل مشخص نشده"
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=f"رزرو ویزیت حضوری شما تایید نشد 😔\nدلیل: {reason}\nسوالی داری ازم بپرس؟"
                        )
                        await update.message.reply_text("ویزیت حضوری تایید نشد و دلیل به کاربر ارسال شد.")
                        context.user_data["awaiting_receipt"] = False
                
                elif pending_type == "visit_online":
                    if text.startswith("تایید"):
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text="رزرو وقت ویزیت آنلاین برای شما با موفقیت انجام شد 🌱 بزودی با شما تماس گرفته خواهد شد.\nسوالی داری ازم بپرس؟"
                        )
                        await update.message.reply_text("ویزیت آنلاین تایید شد و پیام به کاربر ارسال شد.")
                        context.user_data["awaiting_receipt"] = False
                    elif text.startswith("تایید نشد"):
                        reason = text.replace("تایید نشد", "").strip() or "دلیل مشخص نشده"
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=f"رزرو ویزیت آنلاین شما تایید نشد 😔\nدلیل: {reason}\nسوالی داری ازم بپرس؟"
                        )
                        await update.message.reply_text("ویزیت آنلاین تایید نشد و دلیل به کاربر ارسال شد.")
                        context.user_data["awaiting_receipt"] = False
            
            else:
                await context.bot.send_message(chat_id=target_user_id, text=text)
                await update.message.reply_text("جوابت برای کاربر فرستاده شد!")
        else:
            await update.message.reply_text("لطفاً به پیام فورواردشده کاربر ریپلای کن تا جواب براش بره!")
    elif user_id != int(ADMIN_ID):
        context.user_data["user_id"] = user_id
        print(f"آیدی کاربر ذخیره شد: {user_id}")
        
        if section in ["treatment", "care"]:
            if context.user_data.get("first_message", True):
                loading_msg = await update.message.reply_text("یه لحظه صبر کن، دارم فکر می‌کنم! 🌱")
                context.user_data["first_message"] = False
            else:
                loading_msg = await update.message.reply_text("در حال فکر کردن... 🌿")
            
            try:
                conversation = context.user_data.get("conversation", [])
                conversation.append({"role": "user", "content": update.message.text})
                
                prompt = f"""
                شما یک متخصص گیاه‌شناسی بسیار آگاه و با تجربه هستید که دانش عمیقی در زمینه‌های مختلف گیاهان از جمله گیاهان آپارتمانی، گیاهان دارویی، گیاهان کشاورزی، درختان، گل‌ها و سایر انواع گیاهان دارید. شما قادر به پاسخگویی دقیق و جامع به سوالات کاربران در مورد شناسایی گیاهان، نحوه نگهداری صحیح، مشکلات و بیماری‌های گیاهان، روش‌های تکثیر، خواص گیاهان دارویی و هر موضوع مرتبط دیگر هستید.

                اصول پاسخگویی شما:
                - دقت و صحت: همواره پاسخ‌های دقیق و مبتنی بر دانش علمی ارائه دهید. از ارائه اطلاعات نادرست یا غیرمطمئن خودداری کنید.
                - جامعیت: سعی کنید تا حد امکان تمام جوانب سوال کاربر را پوشش دهید و اطلاعات کاملی ارائه کنید.
                - وضوح و سادگی: از زبانی ساده و قابل فهم برای کاربر استفاده کنید، حتی اگر موضوع پیچیده باشد. اصطلاحات تخصصی را در صورت نیاز توضیح دهید.
                - راهنمایی عملی: علاوه بر ارائه اطلاعات نظری، راهکارهای عملی و قابل اجرا برای حل مشکلات یا بهبود شرایط گیاهان ارائه دهید.
                - توجه به جزئیات: به جزئیات مطرح شده توسط کاربر توجه کنید و پاسخ خود را بر اساس اطلاعات ارائه شده تنظیم کنید.
                - پرسش‌های تکمیلی: در صورت نیاز برای درک بهتر سوال کاربر، سوالات تکمیلی بپرسید.
                - احتیاط در تشخیص بیماری از طریق متن: به کاربر یادآوری کنید که تشخیص دقیق بیماری گیاه بدون مشاهده مستقیم ممکن نیست و توضیحات شما بر اساس اطلاعات ارائه شده است. در صورت امکان، توصیه کنید برای تشخیص دقیق‌تر به یک متخصص گیاه‌شناسی مراجعه کنند.
                - لحن دوستانه و کمک‌کننده: با لحنی صمیمی و مشتاق به کمک پاسخ دهید تا کاربر احساس راحتی کند.
                - پاسخ‌ها خلاصه‌تر باشن، ولی خیلی کوتاه نباشن و اطلاعات کامل بمونه.
                - از اموجی‌های مرتبط مثل 🌱، 💧، ☀️، 🐞 استفاده کن.

                مثال‌هایی از نحوه پاسخگویی:
                سوال: برگ‌های گیاه آپارتمانی من زرد شده‌اند، علت چیست؟
                پاسخ: زرد شدن برگ‌ها می‌تونه از آبیاری زیاد 💧، نور کم ☀️ یا کمبود مواد مغذی باشه. نوع گیاهت چیه؟ چند وقت یه بار آب می‌دی؟ علائم دیگه‌ای هم داره؟
                سوال: چگونه می‌توانم گیاه رزماری را تکثیر کنم؟
                پاسخ: بهترین روش برای رزماری، قلمه زدنه 🌿. یه شاخه 10-15 سانتی‌متری ببر، برگ‌های پایینش رو جدا کن و توی خاک یا آب بذار تا ریشه بده. بعد بکارش توی گلدون!
                سوال: خواص دارویی گیاه اسطوخودوس چیست؟
                پاسخ: اسطوخودوس برای کاهش استرس 😌، بهبود خواب 💤 و تسکین سردرد خوبه. از اسانسش برای آروماتراپی یا دمنوش استفاده می‌شه. قبلش با پزشک مشورت کن!

                کاربر در مورد {section} گیاهش داره حرف می‌زنه.
                {f"دسته‌بندی گیاه: {context.user_data.get('care_category', 'مشخص نشده')}" if section == "care" else ""}
                تاریخچه مکالمه: {conversation}.
                آخرین پیام کاربر: "{update.message.text}".
                به فارسی، دوستانه و محترمانه جواب بده.
                """
                response = model.generate_content(prompt)
                answer_fa = response.text
                
                conversation.append({"role": "assistant", "content": answer_fa})
                context.user_data["conversation"] = conversation
                
                await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
                await update.message.reply_text(answer_fa)
            except Exception as e:
                await context.bot.delete_message(chat_id=user_id, message_id=loading_msg.message_id)
                await update.message.reply_text(f"خطا: {str(e)}. دوباره امتحان کن! ⚠️")
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        else:
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
            await update.message.reply_text("پیامت رو برای ادمین فرستادم، منتظر باش! 🌿")

# مدیریت عکس‌ها و لوکیشن
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.user_data["user_id"] = user_id
    print(f"آیدی کاربر ذخیره شد: {user_id}")
    
    if context.user_data.get("awaiting_receipt", False):
        pending_type = context.user_data.get("pending_type")
        
        if pending_type == "product":
            await update.message.reply_text("رسیدت رو گرفتم! منتظر تایید ادمین باش 🌱")
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
            print("عکس رسید خرید برای ادمین فوروارد شد")
        elif pending_type == "visit_home":
            await update.message.reply_text("رسید بیعانه رو گرفتم! منتظر تایید ادمین باش 🌿")
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"رسید بیعانه ویزیت حضوری:\n"
                     f"تعداد گیاهان و توضیحات: {context.user_data['visit_home_info']['plants']}\n"
                     f"نام: {context.user_data['visit_home_info']['name']}\n"
                     f"شماره: {context.user_data['visit_home_info']['phone']}\n"
                     f"آدرس: {context.user_data['visit_home_info']['address']}\n"
                     f"لوکیشن: ({context.user_data['visit_home_info']['location'].latitude}, {context.user_data['visit_home_info']['location'].longitude})"
            )
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
            print("عکس رسید ویزیت حضوری برای ادمین فوروارد شد")
        elif pending_type == "visit_online":
            await update.message.reply_text("رسیدت رو گرفتم! منتظر تایید ادمین باش 🌱")
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"رسید ویزیت آنلاین:\n"
                     f"تعداد گیاهان و توضیحات: {context.user_data['visit_online_info']['plants']}\n"
                     f"نام: {context.user_data['visit_online_info']['name']}\n"
                     f"شماره: {context.user_data['visit_online_info']['phone']}"
            )
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
            print("عکس رسید ویزیت آنلاین برای ادمین فوروارد شد")
    elif user_id != int(ADMIN_ID):
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        await update.message.reply_text("عکس رو گرفتم! منتظر جواب متخصص باش 🌿")
        if context.user_data.get("section") in ["treatment", "care"]:
            conversation = context.user_data.get("conversation", [])
            conversation.append({"role": "user", "content": "کاربر یک عکس از گیاهش فرستاده است."})
            context.user_data["conversation"] = conversation

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.user_data["user_id"] = user_id
    if context.user_data.get("section") == "visit_home" and "visit_home_info" in context.user_data:
        context.user_data["visit_home_info"]["location"] = update.message.location
        await update.message.reply_text(
            "ممنون ازت! حالا بیعانه ۲۰۰ هزار تومان رو پرداخت کن:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پرداخت از درگاه", callback_data="pay_visit_home_gateway")],
                [InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_home_card")]
            ])
        )

# اجرای ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", back_to_menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"یه خطا پیش اومد: {context.error}")
        if update and hasattr(update, "message") and update.message:
            await update.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن ⚠️")
        elif update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن ⚠️")
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
