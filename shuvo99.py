import telebot
from telebot import types
import json
import os
import requests

# --- কনফিগারেশন ---
API_TOKEN = '8476418925:AAE57Jcsa_VKnh_LC8vCmRJN03TKA6VBG0g'
ADMIN_ID = 7596820363  
LOG_GROUP_ID = -1002467930331 
CHANNELS = ["@shuvobhai533", "@shuvo_bhai11"] 
DB_FILE = "users_db.json"

# --- SMM PANEL কনফিগারেশন ---
SMM_API_URL = "https://rxsmm.top/api/v2"
SMM_API_KEY = "dd70fd0310730fa0a5c3edcd2ae13439"
SMM_SERVICE_ID = "13554"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

# --- ডাটাবেস ম্যানেজমেন্ট ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {"users": {}, "settings": {}}
    return {"users": {}, "settings": {}}

def save_data(db_data):
    with open(DB_FILE, "w") as f:
        json.dump(db_data, f, indent=4)

db = load_data()

# --- ডিফল্ট সেটিংস ---
def get_settings():
    defaults = {
        "coins_per_refer": 15,
        "coins_per_subscriber": 1,   # ১ কয়েন = ১ সাবস্ক্রাইবার
        "min_order": 100,
        "auto_order": True           # True = অটো SMM-এ যাবে, False = এডমিন approve লাগবে
    }
    s = db.get("settings", {})
    for k, v in defaults.items():
        if k not in s:
            s[k] = v
    db["settings"] = s
    return s

# --- SMM API ফাংশন ---
def place_smm_order(link, quantity):
    payload = {
        'key': SMM_API_KEY,
        'action': 'add',
        'service': SMM_SERVICE_ID,
        'link': link,
        'quantity': int(quantity)  # FIX: সবসময় integer
    }
    try:
        response = requests.post(SMM_API_URL, data=payload, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- মেম্বারশিপ চেক ফাংশন ---
def is_joined(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status in ['left', 'kicked', 'restricted']:
                return False
        except:
            return False
    return True

# --- কিবোর্ড বাটন ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🚀 Gᴇᴛ Sᴜʙꜱᴄʀɪʙᴇʀꜱ"))
    markup.row(types.KeyboardButton("🎁 Rᴇꜰᴇʀ & Eᴀʀɴ"), types.KeyboardButton("👤 Mʏ Aᴄᴄᴏᴜɴᴛ"))
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("➕ Add Coins"), types.KeyboardButton("➖ Remove Coins"))
    markup.row(types.KeyboardButton("🗑 Delete User"), types.KeyboardButton("🧨 Reset All Data"))
    markup.row(types.KeyboardButton("📊 Stats"), types.KeyboardButton("⚙️ Settings"))
    markup.row(types.KeyboardButton("🏠 Back to Main"))
    return markup

def settings_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🔄 Refer Coins"), types.KeyboardButton("📊 Coins Per Sub"))
    markup.row(types.KeyboardButton("📦 Min Order"), types.KeyboardButton("🤖 Auto Order Toggle"))
    markup.row(types.KeyboardButton("🔙 Admin Menu"))
    return markup

# --- স্টার্ট কমান্ড ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    args = message.text.split()
    
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "coins": 0,
            "referred_by": None,
            "is_new": True,
            "name": message.from_user.first_name,
            "temp_link": ""
        }
        if len(args) > 1:
            ref_id = args[1]
            if ref_id in db["users"] and ref_id != user_id:
                db["users"][user_id]["referred_by"] = ref_id
        save_data(db)

    if not is_joined(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton(f"🔗 Jᴏɪɴ {ch}", url=f"https://t.me/{ch[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Jᴏɪɴᴇᴅ", callback_data="check_join"))
        bot.send_message(message.chat.id, "🚫 <b>Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ!</b>\n\n⚠️ Jᴏɪɴ Tʜᴇ Cʜᴀɴɴᴇʟꜱ Bᴇʟᴏᴡ Tᴏ Uꜱᴇ Tʜɪꜱ Bᴏᴛ:", reply_markup=markup)
    else:
        settings = get_settings()
        if db["users"][user_id].get("is_new") and db["users"][user_id]["referred_by"]:
            ref_id = db["users"][user_id]["referred_by"]
            refer_coins = settings["coins_per_refer"]
            db["users"][ref_id]["coins"] += refer_coins
            db["users"][user_id]["is_new"] = False
            save_data(db)
            try:
                bot.send_message(ref_id, f"🎉 <b>Nᴇᴡ Rᴇꜰᴇʀʀᴀʟ Jᴏɪɴᴇᴅ!</b>\n💰 Yᴏᴜ Rᴇᴄᴇɪᴠᴇᴅ +{refer_coins} Cᴏɪɴꜱ!")
            except:
                pass

        bot.send_message(message.chat.id, "✨ <b>Wᴇʟᴄᴏᴍᴇ! Pʟᴇᴀꜱᴇ ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ:</b>", reply_markup=main_menu())

# --- এডমিন কমান্ড ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🛠 <b>Admin Panel</b>", reply_markup=admin_menu())

# --- টেক্সট মেসেজ হ্যান্ডলার ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = str(message.chat.id)
    text = message.text

    if not is_joined(message.chat.id) and text != "/start":
        start(message)
        return

    # ইউজার মেনু
    if text == "👤 Mʏ Aᴄᴄᴏᴜɴᴛ":
        settings = get_settings()
        coins = db["users"][user_id]["coins"]
        subs = coins // settings["coins_per_subscriber"]
        bot.send_message(message.chat.id,
            f"👤 <b>Aᴄᴄᴇꜱꜱ Dᴇᴛᴀɪʟꜱ:</b>\n\n"
            f"💰 Bᴀʟᴀɴᴄᴇ: <b>{coins} Cᴏɪɴꜱ</b>\n"
            f"📊 Yᴏᴜ ᴄᴀɴ ɢᴇᴛ: <b>{subs} Sᴜʙꜱᴄʀɪʙᴇʀꜱ</b>\n"
            f"🆔 ID: <code>{user_id}</code>")

    elif text == "🎁 Rᴇꜰᴇʀ & Eᴀʀɴ":
        settings = get_settings()
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={user_id}"
        coins = db["users"][user_id]["coins"]
        msg = (f"🎁 <b>Rᴇꜰᴇʀ & Eᴀʀɴ Sʏꜱᴛᴇᴍ</b>\n\n"
               f"🔗 <b>Yᴏᴜʀ Iɴᴠɪᴛᴇ Lɪɴᴋ:</b>\n{link}\n\n"
               f"💰 <b>Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ:</b> {coins} Cᴏɪɴꜱ\n\n"
               f"👥 1 Rᴇꜰᴇʀ = {settings['coins_per_refer']} Cᴏɪɴꜱ\n"
               f"📊 {settings['coins_per_subscriber']} Cᴏɪɴ = 1 Sᴜʙꜱᴄʀɪʙᴇʀ")
        bot.send_message(message.chat.id, msg)

    elif text == "🚀 Gᴇᴛ Sᴜʙꜱᴄʀɪʙᴇʀꜱ":
        msg = bot.send_message(message.chat.id, "❯ <b>Eɴᴛᴇʀ Yᴏᴜʀ Cʜᴀɴɴᴇʟ Oʀ Gʀᴏᴜᴘ Lɪɴᴋ:</b>", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_link)

    elif text == "🏠 Back to Main":
        bot.send_message(message.chat.id, "🏠 <b>Main Menu</b>", reply_markup=main_menu())

    # এডমিন মেনু
    if message.chat.id == ADMIN_ID:
        if text == "➕ Add Coins":
            msg = bot.send_message(ADMIN_ID, "👤 Enter User ID to add coins:")
            bot.register_next_step_handler(msg, process_add_id)

        elif text == "➖ Remove Coins":
            msg = bot.send_message(ADMIN_ID, "👤 Enter User ID to remove coins:")
            bot.register_next_step_handler(msg, process_rem_id)

        elif text == "🗑 Delete User":
            msg = bot.send_message(ADMIN_ID, "👤 Enter User ID to delete:")
            bot.register_next_step_handler(msg, process_delete_user)

        elif text == "🧨 Reset All Data":
            msg = bot.send_message(ADMIN_ID, "⚠️ Type <b>CONFIRM</b> to reset all data:")
            bot.register_next_step_handler(msg, process_reset_all)

        elif text == "📊 Stats":
            settings = get_settings()
            total_users = len(db["users"])
            auto_status = "✅ ON" if settings["auto_order"] else "❌ OFF"
            bot.send_message(ADMIN_ID,
                f"📊 <b>Bot Stats</b>\n\n"
                f"👥 Total Users: <b>{total_users}</b>\n"
                f"🤖 Auto Order: <b>{auto_status}</b>\n"
                f"🔄 Refer Coins: <b>{settings['coins_per_refer']}</b>\n"
                f"📦 Min Order: <b>{settings['min_order']}</b>\n"
                f"💰 Coins/Sub: <b>{settings['coins_per_subscriber']}</b>")

        elif text == "⚙️ Settings":
            settings = get_settings()
            auto_status = "✅ ON" if settings["auto_order"] else "❌ OFF"
            bot.send_message(ADMIN_ID,
                f"⚙️ <b>Current Settings:</b>\n\n"
                f"🔄 Refer Coins: <b>{settings['coins_per_refer']}</b>\n"
                f"💰 Coins Per Sub: <b>{settings['coins_per_subscriber']}</b>\n"
                f"📦 Min Order: <b>{settings['min_order']}</b>\n"
                f"🤖 Auto Order: <b>{auto_status}</b>",
                reply_markup=settings_menu())

        elif text == "🔙 Admin Menu":
            bot.send_message(ADMIN_ID, "🛠 <b>Admin Panel</b>", reply_markup=admin_menu())

        # --- Settings Handlers ---
        elif text == "🔄 Refer Coins":
            msg = bot.send_message(ADMIN_ID, f"💰 Current Refer Coins: <b>{get_settings()['coins_per_refer']}</b>\n\nEnter new value:")
            bot.register_next_step_handler(msg, lambda m: update_setting(m, "coins_per_refer", "Refer Coins"))

        elif text == "📊 Coins Per Sub":
            msg = bot.send_message(ADMIN_ID, f"📊 Current Coins/Sub: <b>{get_settings()['coins_per_subscriber']}</b>\n\nEnter new value (e.g. 1 = 1 coin per subscriber):")
            bot.register_next_step_handler(msg, lambda m: update_setting(m, "coins_per_subscriber", "Coins Per Sub"))

        elif text == "📦 Min Order":
            msg = bot.send_message(ADMIN_ID, f"📦 Current Min Order: <b>{get_settings()['min_order']}</b>\n\nEnter new value:")
            bot.register_next_step_handler(msg, lambda m: update_setting(m, "min_order", "Min Order"))

        elif text == "🤖 Auto Order Toggle":
            settings = get_settings()
            settings["auto_order"] = not settings["auto_order"]
            db["settings"] = settings
            save_data(db)
            status = "✅ ON" if settings["auto_order"] else "❌ OFF"
            bot.send_message(ADMIN_ID, f"🤖 Auto Order is now: <b>{status}</b>", reply_markup=settings_menu())

# --- সেটিং আপডেট ---
def update_setting(message, key, label):
    if message.text.isdigit():
        val = int(message.text)
        settings = get_settings()
        settings[key] = val
        db["settings"] = settings
        save_data(db)
        bot.send_message(ADMIN_ID, f"✅ <b>{label}</b> updated to <b>{val}</b>", reply_markup=settings_menu())
    else:
        bot.send_message(ADMIN_ID, "❌ Invalid value. Enter a number.", reply_markup=settings_menu())

# --- এডমিন ফাংশনালিটি ---
def process_delete_user(message):
    target_id = message.text
    if target_id in db["users"]:
        del db["users"][target_id]
        save_data(db)
        bot.send_message(ADMIN_ID, f"✅ User <code>{target_id}</code> deleted!")
    else:
        bot.send_message(ADMIN_ID, "❌ User not found!")

def process_reset_all(message):
    if message.text == "CONFIRM":
        db["users"] = {}
        save_data(db)
        bot.send_message(ADMIN_ID, "🧨 <b>Database Reset!</b> All data cleared.")
    else:
        bot.send_message(ADMIN_ID, "❌ Reset cancelled.")

def process_add_id(message):
    target_id = message.text
    if target_id in db["users"]:
        msg = bot.send_message(ADMIN_ID, "💰 Enter Amount to add:")
        bot.register_next_step_handler(msg, lambda m: process_add_final(m, target_id))
    else:
        bot.send_message(ADMIN_ID, "❌ User not found!")

def process_add_final(message, target_id):
    if message.text.isdigit():
        amount = int(message.text)
        db["users"][target_id]["coins"] += amount
        save_data(db)
        bot.send_message(ADMIN_ID, f"✅ Added {amount} coins to {target_id}")
        try:
            bot.send_message(int(target_id), f"💰 <b>Admin added {amount} coins!</b>")
        except:
            pass
    else:
        bot.send_message(ADMIN_ID, "❌ Invalid Amount.")

def process_rem_id(message):
    target_id = message.text
    if target_id in db["users"]:
        msg = bot.send_message(ADMIN_ID, "💰 Enter Amount to remove:")
        bot.register_next_step_handler(msg, lambda m: process_rem_final(m, target_id))
    else:
        bot.send_message(ADMIN_ID, "❌ User not found!")

def process_rem_final(message, target_id):
    if message.text.isdigit():
        amount = int(message.text)
        db["users"][target_id]["coins"] = max(0, db["users"][target_id]["coins"] - amount)
        save_data(db)
        bot.send_message(ADMIN_ID, f"✅ Removed {amount} coins from {target_id}")
    else:
        bot.send_message(ADMIN_ID, "❌ Invalid Amount.")

# --- অর্ডার প্রসেস ---
def get_link(message):
    if "t.me/" not in message.text:
        bot.send_message(message.chat.id, "❌ Iɴᴠᴀʟɪᴅ Lɪɴᴋ! t.me লিঙ্ক দিন।", reply_markup=main_menu())
        return
    db["users"][str(message.chat.id)]["temp_link"] = message.text
    save_data(db)
    settings = get_settings()
    msg = bot.send_message(message.chat.id, f"❯ <b>Eɴᴛᴇʀ Qᴜᴀɴᴛɪᴛʏ (Min: {settings['min_order']}):</b>")
    bot.register_next_step_handler(msg, get_quantity)

def get_quantity(message):
    user_id = str(message.chat.id)
    settings = get_settings()

    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ শুধু সংখ্যা দিন!", reply_markup=main_menu())
        return

    qty = int(message.text)
    coins_needed = qty * settings["coins_per_subscriber"]
    user_coins = db["users"][user_id]["coins"]

    if qty < settings["min_order"]:
        bot.send_message(message.chat.id, f"❌ <b>Mɪɴɪᴍᴜᴍ {settings['min_order']} Sᴜʙꜱᴄʀɪʙᴇʀꜱ!</b>", reply_markup=main_menu())
        return

    if coins_needed > user_coins:
        bot.send_message(message.chat.id,
            f"❌ <b>Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ Cᴏɪɴꜱ!</b>\n"
            f"💰 Tᴜ Aᴄʜᴇ: {user_coins} Cᴏɪɴꜱ\n"
            f"📊 Dᴀʀᴋᴀʀ: {coins_needed} Cᴏɪɴꜱ",
            reply_markup=main_menu())
        return

    # কয়েন কাটা
    db["users"][user_id]["coins"] -= coins_needed
    link = db["users"][user_id]["temp_link"]
    save_data(db)

    # অটো অর্ডার চালু থাকলে সরাসরি SMM-এ পাঠাও
    if settings["auto_order"]:
        bot.send_message(message.chat.id, "⏳ <b>Processing your order...</b>", reply_markup=main_menu())
        smm_response = place_smm_order(link, qty)

        if "order" in smm_response:
            order_id = smm_response["order"]
            bot.send_message(message.chat.id,
                f"✅ <b>Oʀᴅᴇʀ Sᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n\n"
                f"🔗 Link: {link}\n"
                f"📊 Qty: {qty}\n"
                f"🆔 SMM ID: {order_id}\n\n"
                f"<i>Subscribers will be added shortly!</i>",
                reply_markup=main_menu())
            # লগ গ্রুপে জানাও
            bot.send_message(LOG_GROUP_ID,
                f"✅ <b>Auto Order Complete!</b>\n"
                f"👤 {message.from_user.first_name} | <code>{user_id}</code>\n"
                f"🔗 {link}\n📊 Qty: {qty}\n🆔 SMM: {order_id}")
        else:
            # SMM ফেল হলে কয়েন ফেরত দাও
            error_msg = smm_response.get("error", "Unknown error")
            db["users"][user_id]["coins"] += coins_needed
            save_data(db)
            bot.send_message(message.chat.id,
                f"❌ <b>Order Failed!</b>\nSMM Error: {error_msg}\n\n💰 Coins refunded.",
                reply_markup=main_menu())
            bot.send_message(LOG_GROUP_ID,
                f"❌ <b>SMM Error!</b>\n👤 {user_id}\n🔗 {link}\n⚠️ {error_msg}")
    else:
        # ম্যানুয়াল মোড — এডমিন approve করবে
        bot.send_message(message.chat.id,
            f"✅ <b>Oʀᴅᴇʀ Pʟᴀᴄᴇᴅ!</b>\n\n🔗 {link}\n📊 Qty: {qty}\n\n<i>Waiting for Admin approval...</i>",
            reply_markup=main_menu())

        log_msg = (f"📥 <b>New Pending Order!</b>\n\n"
                   f"👤 {message.from_user.first_name}\n"
                   f"🆔 <code>{user_id}</code>\n"
                   f"🔗 {link}\n📊 Qty: {qty}\n"
                   f"Status: 🟡 Pending")
        bot.send_message(LOG_GROUP_ID, log_msg)

        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("✅ Accept", callback_data=f"ord_acc:{user_id}:{qty}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"ord_rej:{user_id}:{qty}")
        )
        bot.send_message(ADMIN_ID, log_msg, reply_markup=admin_markup)

# --- কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "check_join":
        if is_joined(call.message.chat.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Still not joined!", show_alert=True)

    elif call.data.startswith("ord_acc"):
        parts = call.data.split(":")
        target_id = parts[1]
        qty = int(parts[2])  # FIX: string থেকে int

        # লিঙ্ক বের করো
        try:
            link = call.message.text.split("🔗 ")[1].split("\n")[0]
        except:
            link = db["users"].get(target_id, {}).get("temp_link", "")

        bot.answer_callback_query(call.id, "⏳ Sending to SMM...")
        smm_response = place_smm_order(link, qty)

        if "order" in smm_response:
            order_id = smm_response["order"]
            bot.edit_message_text(
                f"✅ <b>Accepted & Sent!</b>\nUser: {target_id}\nQty: {qty}\nSMM ID: {order_id}",
                call.message.chat.id, call.message.message_id)
            bot.send_message(LOG_GROUP_ID,
                f"✅ <b>Order Done!</b>\n👤 {target_id}\n📊 {qty}\n🆔 SMM: {order_id}")
            try:
                bot.send_message(int(target_id), f"🥳 <b>Order accepted! {qty} subscribers coming soon!</b>")
            except:
                pass
        else:
            error_msg = smm_response.get("error", "Unknown SMM Error")
            # কয়েন ফেরত
            settings = get_settings()
            coins_refund = qty * settings["coins_per_subscriber"]
            if target_id in db["users"]:
                db["users"][target_id]["coins"] += coins_refund
                save_data(db)
            bot.edit_message_text(
                f"❌ <b>SMM Error!</b>\n{error_msg}\nCoins refunded.",
                call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, f"❌ SMM: {error_msg}", show_alert=True)

    elif call.data.startswith("ord_rej"):
        parts = call.data.split(":")
        target_id = parts[1]
        qty = int(parts[2])

        settings = get_settings()
        coins_refund = qty * settings["coins_per_subscriber"]
        if target_id in db["users"]:
            db["users"][target_id]["coins"] += coins_refund
            save_data(db)

        bot.edit_message_text(
            f"❌ <b>Order Rejected!</b>\nUser: {target_id}\nQty: {qty}\n(Coins Refunded)",
            call.message.chat.id, call.message.message_id)
        bot.send_message(LOG_GROUP_ID,
            f"❌ <b>Rejected!</b>\n👤 {target_id}\n📊 {qty}\n🔴 Refunded")
        try:
            bot.send_message(int(target_id), f"❌ <b>Order rejected. {coins_refund} coins refunded.</b>")
        except:
            pass

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
