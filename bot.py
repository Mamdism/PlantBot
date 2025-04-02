from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import requests
import asyncio

# آیدی عددی تلگرام ادمین
ADMIN_ID = "1478363268"

# توکن ربات
BOT_TOKEN = "7990694940:AAFAftck3lNCMdt4ts7LWfJEmqAxLu1r2g4"

# کلید API Gemini
GEMINI_API_KEY = "AIzaSyCPUX41Xo_N611S5ToS3eI-766Z7oHt2B4"

# آیدی کانال تلگرامی
CHANNEL_ID = "-1002560592686"

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

# گرفتن محصولات از کانال (بدون عکس)
async def fetch_products(context: ContextTypes.DEFAULT_TYPE, category: str):
    products = []
    print(f"در حال بررسی کانال {CHANNEL_ID} برای دسته‌بندی: {category}")
    
    # یه تأخیر کوچک برای کاهش فشار
    await asyncio.sleep(1)
    
    # گرفتن آپدیت‌ها از تلگرام
    try:
        updates = await context.bot.get_updates()
    except Exception as e:
        print(f"خطا در گرفتن آپدیت‌ها: {e}")
        return products
    
    for update in updates:
        if update and hasattr(update, 'channel_post') and update.channel_post is not None:
            message = update.channel_post
            if hasattr(message, 'chat_id') and message.chat_id is not None and str(message.chat_id) == CHANNEL_ID:
                print(f"پیام پیدا شد: text={message.text}")
                if message.text:
                    print(f"پست با متن پیدا شد: {message.text}")
                    lines = message.text.split('\n')
                    product = {}
                    for line in lines:
                        print(f"خط در حال بررسی: {line}")
                        if "دسته‌بندی:" in line:
                            product["category"] = line.split(":")[1].strip()
                        elif "نام:" in line:
                            product["name"] = line.split(":")[1].strip()
                        elif "سایز:" in line:
                            product["size"] = line.split(":")[1].strip()
                        elif "رنگ:" in line:
                            product["color"] = line.split(":")[1].strip()
                        elif "تعداد:" in line:
                            product["stock"] = int(line.split(":")[1].strip())
                        elif "قیمت:" in line:
                            product["price"] = int(line.split(":")[1].strip().replace(" تومان", ""))
                    if product.get("category") == category:
                        products.append(product)
                        print(f"محصول اضافه شد: {product}")
    
    print(f"تعداد محصولات پیدا شده: {len(products)}")
    return products

# نمایش رسید
async def show_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = context.user_data["selected_product"]
    products = await fetch_products(context, context.user_data["selected_category"])
    product = next(p for p in products if p["name"] == product_name)
    
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

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! به ربات هیوا خوش اومدی. یه گزینه رو انتخاب کن:", reply_markup=main_menu())

# مدیریت دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "treatment":
        await query.edit_message_text("لطفاً نوع گیاهت یا مشکلی که داره رو توضیح بده و اگه می‌تونی یه عکس بفرست!")
        context.user_data["section"] = "treatment"
        context.user_data["first_message"] = True
        context.user_data["conversation"] = []
    elif choice == "care":
        await query.edit_message_text("لطفاً نوع گیاهت یا سوالی که در مورد نگهداریش داری رو بگو و اگه می‌تونی عکس بفرست!")
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
            await query.edit_message_text("محصولی توی این دسته‌بندی پیدا نشد! مطمئن شو توی کانال با فرمت درست پست گذاشتی.")
            return
        
        for product in products:
            caption = (f"نام: {product['name']}\n"
                       f"سایز: {product['size']}\n"
                       f"رنگ: {product['color']}\n"
                       f"تعداد موجود: {product['stock']}\n"
                       f"**قیمت: {product['price']} تومان**")
            keyboard = [[InlineKeyboardButton("خرید", callback_data=f"buy_{product['name']}")]]
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
    elif choice.startswith("buy_"):
        product_name = choice.replace("buy_", "")
        context.user_data["selected_product"] = product_name
        await query.edit_message_text(
            "لطفاً مشخصات و آدرس رو وارد کن:\n"
            "نام و نام خانوادگی:\n"
            "شماره تلفن:\n"
            "استان:\n"
            "شهر:\n"
            "آدرس:\n"
            "کدپستی:\n"
            "هر خط یه بخش رو پر کن و بفرست."
        )
        context.user_data["awaiting_address"] = True
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
    elif choice == "back_to_main":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="سلام! به ربات هیوا خوش اومدی. یه گزینه رو انتخاب کن:",
            reply_markup=main_menu()
        )
        context.user_data.clear()
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
    
    if context.user_data.get("awaiting_address", False):
        text = update.message.text.split("\n")
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
            await show_receipt(update, context)
        else:
            await update.message.reply_text("لطفاً همه‌ی اطلاعات رو توی ۶ خط بفرست!")
        return
    
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
            if context.user_data.get("first_message", True):
                loading_msg = await update.message.reply_text("یه لحظه صبر کن، دارم فکر می‌کنم!")
                context.user_data["first_message"] = False
            else:
                loading_msg = await update.message.reply_text("در حال فکر کردن...")
            
            try:
                conversation = context.user_data.get("conversation", [])
                conversation.append({"role": "user", "content": update.message.text})
                
                prompt = f"""
                تو یه متخصص گل و گیاه هستی. کاربر در مورد {section} گیاهش داره باهات حرف می‌زنه.
                این تاریخچه مکالمه‌ست: {conversation}.
                آخرین پیام کاربر: "{update.message.text}".
                به زبان فارسی، دوستانه و محترمانه جواب بده. اگه فکر می‌کنی برای جواب دقیق‌تر نیاز به اطلاعات بیشتر یا عکس داری، محترمانه بگو، وگرنه کامل جواب بده.
                """
                response = model.generate_content(prompt)
                answer_fa = response.text
                
                conversation.append({"role": "assistant", "content": answer_fa})
                context.user_data["conversation"] = conversation
                
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
    if context.user_data.get("awaiting_receipt", False):
        await update.message.reply_text("رسیدت رو گرفتم! سفارش در حال بررسیه.")
        context.user_data["awaiting_receipt"] = False
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
    elif user_id != int(ADMIN_ID):
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
    # تنظیم اندازه pool و timeout با مقادیر بزرگ‌تر
    app = Application.builder().token(BOT_TOKEN).connect_timeout(30).pool_timeout(30).connection_pool_size(50).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"یه خطا پیش اومد: {context.error}")
        if update and hasattr(update, "message") and update.message:
            await update.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن.")
        elif update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.message.reply_text("مشکلی پیش اومد! لطفاً دوباره امتحان کن.")
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
