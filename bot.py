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
        context.user_data["selected_product_price"] = product["price"]  # ذخیره قیمت برای پرداخت
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

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users = get_users()
    
    if str(user_id) not in users:
        keyboard = [[KeyboardButton("اطلاعات تماس شما", request_contact=True)]]
        await update.message.reply_text(
            "به دستیار گل و گیاهتون هیوا خوش اومدین💚\nلطفاً برای ثبت‌نام، اطلاعات تماس خودت رو اشتراک کن:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        )
    else:
        await update.message.reply_text("به دستیار گل و گیاهتون هیوا خوش اومدین💚\nیه گزینه رو انتخاب کن:", reply_markup=main_menu())

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
        await query.edit_message_text(f"درباره {context.user_data['care_category']} بگو، چه کمکی می‌خوای؟ 🌿")
        context.user_data["section"] = "care"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
        context.user_data["has_photo"] = False
    elif choice == "education":
        await query.edit_message_text("یه موضوع آموزشی انتخاب کن:", reply_markup=education_menu())
    elif choice.startswith("edu_"):
        education_content = {
            "edu_1": """**مبانی اولیه گیاه‌شناسی** 🌿✨\nبرای شروع کار با گیاهان، باید با اصول اولیه آشنا بشین. گیاهان موجودات زنده‌ای هستن که به نور، آب، خاک مناسب و کمی توجه نیاز دارن. هر گیاه ساختار خاص خودش رو داره: ریشه برای جذب آب و مواد مغذی، ساقه برای انتقال این مواد و برگ‌ها برای فتوسنتز و تولید انرژی. شناخت نوع گیاه (مثلاً آپارتمانی یا فضای باز) بهتون کمک می‌کنه تا نیازهاش رو بهتر بشناسین و محیط مناسب براش فراهم کنین.\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_2": """**روش‌های آبیاری و تغذیه گیاهان** 💧🌱\nآبیاری درست یکی از مهم‌ترین بخش‌های نگهداری گیاهه. هر گیاه نیاز متفاوتی به آب داره؛ مثلاً کاکتوس‌ها کم‌آب می‌خوان، ولی گیاهان برگ‌دار مثل پتوس به آب بیشتری نیاز دارن. همیشه خاک رو چک کنین، اگه خشک بود آب بدین. تغذیه هم با کودهای مناسب مثل NPK (نیتروژن، فسفر، پتاسیم) انجام می‌شه که رشد، گل‌دهی و سلامت ریشه رو تقویت می‌کنه. یادتون باشه زیاده‌روی نکنین!\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_3": """**تکثیر و پرورش گیاهان** 🌿\nتکثیر گیاهان راهی عالی برای افزایش تعداد گلدوناتونه! روش‌های رایج شامل قلمه‌زنی (مثل بریدن یه شاخه و کاشتنش)، تقسیم ریشه و کاشت بذره. مثلاً برای قلمه‌زنی، یه ساقه سالم رو جدا کنین، توی آب یا خاک بذارین تا ریشه بده. صبر و مراقبت مهمه تا گیاه جدید جون بگیره.\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_4": """**کنترل آفات و بیماری‌ها** 🐞\nگیاهاتون ممکنه با آفاتی مثل شته یا کنه و بیماری‌هایی مثل قارچ روبه‌رو بشن. اولین قدم، مشاهده دقیق برگ‌ها و ساقه‌هاست. برای آفات، می‌تونین از آب و صابون ملایم یا حشره‌کش طبیعی استفاده کنین. برای بیماری‌ها، تهویه خوب و آبیاری متعادل مهمه. پیشگیری بهتر از درمانه!\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_5": """**طراحی و نگهداری فضای سبز** 🌳\nفضای سبز یه ترکیب قشنگ از گیاهان مختلفه که به محیط زندگی‌تون روح می‌ده. برای طراحی، به نور، اندازه گیاه و نیاز آبی‌شون توجه کنین. نگهداری هم شامل هرس منظم، کوددهی و آبیاری به موقعه. یه باغچه مرتب حس آرامش می‌ده!\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_6": """**مشکلات رایج و راهکارها** ⚠️\nزرد شدن برگ‌ها، افتادگی یا خشک شدن گیاه از مشکلات شایعه. زردی می‌تونه از آبیاری زیاد یا کمبود نور باشه، افتادگی از کم‌آبی یا ریشه ضعیف. با چک کردن خاک، نور و برنامه آبیاری می‌تونین مشکل رو حل کنین.\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_7": """**روش‌های خاص نگهداری** 🌡️\nبعضی گیاهان نیازهای خاص دارن. مثلاً ارکیده به رطوبت بالا و بنفشه آفریقایی به نور غیرمستقیم نیاز داره. دما، رطوبت و نوع گلدون رو بر اساس گیاهتون تنظیم کنین تا همیشه شاداب بمونه.\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_8": """**نور** ☀️\nنور قلب تپنده گیاهان شماست! گیاهان آپارتمانی مثل سانسوریا نور کم رو تحمل می‌کنن، ولی گل‌هایی مثل رز به نور زیاد نیاز دارن. نور مستقیم یا غیرمستقیم رو با توجه به نوع گیاه تنظیم کنین تا رشدشون عالی بشه.\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱""",
            "edu_9": """**گلدان مناسب** 🏺\nانتخاب گلدون درست به ریشه گیاهتون اجازه نفس کشیدن می‌ده. گلدون باید زهکشی خوبی داشته باشه و اندازه‌ش با ریشه متناسب باشه. جنسش (سفالی، پلاستیکی) هم روی رطوبت خاک اثر داره.\nاگه سوالی داری، می‌تونی با برگشت به صفحه اصلی از هوش مصنوعی هیوا بپرسی 🌱"""
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
            text=f"قابلتونو نداره\nمبلغ قابل پرداخت: {context.user_data.get('selected_product_price', 'مشخص نشده')} تومان\nلطفاً مبلغ رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}"
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
            text=f"قابلتونو نداره مبلغ ۲۰۰ هزار تومان باید برای بیعانه پرداخت کنید\nلطفاً مبلغ رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}"
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
            text=f"قابلتونو نداره مبلغ ۲۵۰ هزار تومان باید برای بیعانه پرداخت کنید\nلطفاً مبلغ رو به این کارت واریز کن و رسیدش رو بفرست:\n{CARD_INFO}"
        )
        context.user_data["awaiting_receipt"] = True
        context.user_data["pending_type"] = "visit_online"
    elif choice == "back_to_main":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="به دستیار گل و گیاهتون هیوا خوش اومدین💚\nیه گزینه رو انتخاب کن:",
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
    
    # پیام ادمین به آخرین کاربر (بدون بازنویسی جیمینی)
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
                "ممنونم! حالا نحوه پرداختت رو انتخاب کن:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("پرداخت از درگاه", callback_data="pay_visit_online_gateway")],
                    [InlineKeyboardButton("کارت به کارت", callback_data="pay_visit_online_card")]
                ])
            )
        else:
            await update.message.reply_text("لطفاً تعداد گیاهان، نام و شماره رو توی حداقل ۲ خط بفرست!")
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
            conversation.append({"role": "user", "content": update.message.text})
            
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
            آخرین پیام کاربر: "{update.message.text}".
            آیا کاربر عکس فرستاده؟ {"بله" if context.user_data.get('has_photo', False) else "خیر"}.
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
        await update.message.reply_text("رسیدت رو دریافت کردیم و در صورت تایید توسط ادمین باهاتون جهت هماهنگی تماس می‌گیریم؛ تشکر از انتخابتون 💚")
        print(f"رسید پرداخت به ادمین فوروارد شد (نوع: {pending_type})")
        context.user_data["awaiting_receipt"] = False
    elif section in ["treatment", "care"]:
        context.user_data["has_photo"] = True  # کاربر عکس فرستاده
        await update.message.reply_text("برای متخصصمون فرستادم، بزودی بهت جواب می‌دیم 🫰🏼")
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
        print("عکس درمان/نگهداری به ادمین فوروارد شد")
    else:
        await update.message.reply_text("عکس رو گرفتم، ولی نمی‌دونم چی باهاش کنم! لطفاً توضیح بده 🌱")
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
            "ممنونم ازت! نحوه پرداختت رو انتخاب کن:",
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
    await update.message.reply_text("ممنون! حالا ثبت شدی 🌱 یه گزینه انتخاب کن:", reply_markup=main_menu())

# اجرای ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
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
            await update.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن ⚠️")
        elif update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن ⚠️")
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
