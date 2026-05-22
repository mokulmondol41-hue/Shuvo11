import telebot
from telebot import types
import json
import os
import requests  # API কল করার জন্য নতুন ইম্পোর্ট

# --- কনফিগারেশন ---
API_TOKEN = '8476418925:AAEC9BCB5p4HzI51kFQV7KGWvzyYOM7QBdY'
ADMIN_ID = 7596820363  
LOG_GROUP_ID = -1002467930331 
CHANNELS = ["@shuvobhai533", "@shuvo_bhai11"] 
DB_FILE = "users_db.json"

# --- SMM PANEL কনফিগারেশন ---
SMM_API_URL = "https://rxsmm.top/api/v2"
SMM_API_KEY = "0d042abd54422c1750d174b47f07846f"
SMM_SERVICE_ID = "13554"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

# --- ডাটাবেস ম্যানেজমেন্ট ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {"users": {}}
    return {"users": {}}

def save_data(db_data):
    with open(DB_FILE, "w") as f:
        json.dump(db_data, f, indent=4)

db = load_data()

# --- SMM API ফাংশন ---
def place_smm_order(link, quantity):
    payload = {
        'key': SMM_API_KEY,
        'action': 'add',
        'service': SMM_SERVICE_ID,
        'link': link,
        'quantity': quantity
    }
    try:
        response = requests.post(SMM_API_URL, data=payload)
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
    markup.row(types.KeyboardButton("📊 Stats"), types.KeyboardButton("🏠 Back to Main"))
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
        bot.send_message(message.chat.id, "🚫 <b>Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ!</b>\n\n⚠️ Jᴏɪɴ Tʜᴇ Cʜᴀɴɴᴇʟꜱ Bᴇʟᴏৱ Tᴏ Uꜱᴇ Tʜɪꜱ Bᴏᴛ:", reply_markup=markup)
    else:
        if db["users"][user_id].get("is_new") and db["users"][user_id]["referred_by"]:
            ref_id = db["users"][user_id]["referred_by"]
            db["users"][ref_id]["coins"] += 15
            db["users"][user_id]["is_new"] = False
            save_data(db)
            try: bot.send_message(ref_id, "🎉 <b>Nᴇᴡ Rᴇꜰᴇʀʀᴀʟ Jᴏɪɴᴇᴅ!</b>\n💰 Yᴏᴜ Iɴꜱᴛᴀɴᴛʟʏ Rᴇᴄᴇɪᴠᴇᴅ +15 Cᴏɪɴꜱ!")
            except: pass
            
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

    if text == "👤 Mʏ Aᴄᴄᴏᴜɴᴛ":
        coins = db["users"][user_id]["coins"]
        bot.send_message(message.chat.id, f"👤 <b>Aᴄᴄᴇꜱꜱ Dᴇᴛᴀɪʟꜱ:</b>\n\n💰 Bᴀʟᴀɴᴄᴇ: <b>{coins} Cᴏɪɴꜱ</b>\n🆔 ID: <code>{user_id}</code>")

    elif text == "🎁 Rᴇꜰᴇʀ & Eᴀʀɴ":
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={user_id}"
        coins = db["users"][user_id]["coins"]
        msg = (f"🎁 <b>Rᴇꜰᴇʀ & Eᴀʀɴ Sʏꜱᴛᴇᴍ</b>\n\n"
               f"🔗 <b>Yᴏᴜʀ Iɴᴠɪᴛᴇ Lɪɴᴋ:</b>\n{link}\n\n"
               f"💰 <b>Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ:</b> {coins} Cᴏɪɴs\n\n"
               f"👥 1 Rᴇꜰᴇʀ = 15 Cᴏɪɴꜱ\n"
               f"📊 100 Cᴏɪɴꜱ = 100 Sᴜʙꜱᴄʀɪʙᴇʀꜱ")
        bot.send_message(message.chat.id, msg)

    elif text == "🚀 Gᴇᴛ Sᴜʙꜱᴄʀɪʙᴇʀꜱ":
        msg = bot.send_message(message.chat.id, "❯ <b>Eɴᴛᴇʀ Yᴏᴜʀ Cʜᴀɴɴᴇʟ Oʀ Gʀᴏᴜᴘ Lɪɴᴋ:</b>", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_link)

    elif text == "🏠 Back to Main":
        bot.send_message(message.chat.id, "🏠 <b>Main Menu</b>", reply_markup=main_menu())

    if message.chat.id == ADMIN_ID:
        if text == "➕ Add Coins":
            msg = bot.send_message(ADMIN_ID, "👤 Enter User ID to add coins:")
            bot.register_next_step_handler(msg, process_add_id)
        elif text == "➖ Remove Coins":
            msg = bot.send_message(ADMIN_ID, "👤 Enter User ID to remove coins:")
            bot.register_next_step_handler(msg, process_rem_id)
        elif text == "🗑 Delete User":
            msg = bot.send_message(ADMIN_ID, "👤 Enter User ID to delete all data of that user:")
            bot.register_next_step_handler(msg, process_delete_user)
        elif text == "🧨 Reset All Data":
            msg = bot.send_message(ADMIN_ID, "⚠️ Are you sure? This will delete ALL users data!\n\nType <b>CONFIRM</b> to reset:")
            bot.register_next_step_handler(msg, process_reset_all)
        elif text == "📊 Stats":
            total_users = len(db["users"])
            bot.send_message(ADMIN_ID, f"📊 <b>Total Users:</b> {total_users}")

# --- এডমিন ফাংশনালিটি ---

def process_delete_user(message):
    target_id = message.text
    if target_id in db["users"]:
        del db["users"][target_id]
        save_data(db)
        bot.send_message(ADMIN_ID, f"✅ User <code>{target_id}</code> data has been cleared!")
    else:
        bot.send_message(ADMIN_ID, "❌ User not found!")

def process_reset_all(message):
    if message.text == "CONFIRM":
        db["users"] = {}
        save_data(db)
        bot.send_message(ADMIN_ID, "🧨 <b>Database Reset Successful!</b> All user data cleared.")
    else:
        bot.send_message(ADMIN_ID, "❌ Reset cancelled. You must type 'CONFIRM'.")

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
        try: bot.send_message(target_id, f"💰 <b>Admin added {amount} coins to your balance!</b>")
        except: pass
    else: bot.send_message(ADMIN_ID, "❌ Invalid Amount.")

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
    else: bot.send_message(ADMIN_ID, "❌ Invalid Amount.")

# --- অর্ডার প্রসেস ---
def get_link(message):
    if "t.me/" not in message.text:
        bot.send_message(message.chat.id, "❌ Iɴᴠᴀʟɪᴅ Lɪɴᴋ!", reply_markup=main_menu())
        return
    db["users"][str(message.chat.id)]["temp_link"] = message.text
    save_data(db)
    bot.send_message(message.chat.id, "❯ <b>Eɴᴛᴇʀ Tʜᴇ Qᴜᴀɴᴛɪᴛʏ (Min: 100):</b>")
    bot.register_next_step_handler(message, get_quantity)

def get_quantity(message):
    user_id = str(message.chat.id)
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ɴᴜᴍʙᴇʀ!", reply_markup=main_menu())
        return
    
    qty = int(message.text)
    user_coins = db["users"][user_id]["coins"]

    if qty < 100:
        bot.send_message(message.chat.id, "❌ <b>Mɪɴɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ 100 Sᴜʙꜱᴄʀɪʙᴇʀꜱ!</b>", reply_markup=main_menu())
    elif qty > user_coins:
        bot.send_message(message.chat.id, f"❌ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ Bᴀʟᴀɴᴄᴇ! (Yᴏᴜ ʜᴀᴠᴇ {user_coins} Cᴏɪɴꜱ)", reply_markup=main_menu())
    else:
        db["users"][user_id]["coins"] -= qty
        link = db["users"][user_id]["temp_link"]
        save_data(db)
        
        bot.send_message(message.chat.id, f"✅ <b>Oʀᴅᴇʀ Pʟᴀᴄᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n🔗 Lɪɴᴋ: {link}\n📊 Qᴛʏ: {qty}\n\n<i>Wait for Admin approval.</i>", reply_markup=main_menu())
        
        log_msg = f"📥 <b>Nᴇᴡ Oʀᴅᴇʀ Pᴇɴᴅɪɴɢ!</b>\n\n👤 Uꜱᴇʀ: {message.from_user.first_name}\n🆔 ID: <code>{user_id}</code>\n🔗 Lɪɴᴋ: {link}\n📊 Qᴛʏ: {qty}\nStatus: 🟡 Pending"
        bot.send_message(LOG_GROUP_ID, log_msg)

        admin_markup = types.InlineKeyboardMarkup()
        # এখানে কলব্যাকে আমরা লিঙ্কটিও পাস করার চেষ্টা করব অথবা মেসেজ থেকে খুঁজে নেব
        btn_accept = types.InlineKeyboardButton("✅ Accept", callback_data=f"ord_acc:{user_id}:{qty}")
        btn_reject = types.InlineKeyboardButton("❌ Reject", callback_data=f"ord_rej:{user_id}:{qty}")
        admin_markup.add(btn_accept, btn_reject)
        bot.send_message(ADMIN_ID, log_msg, reply_markup=admin_markup)

# --- কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)

    if call.data == "check_join":
        if is_joined(call.message.chat.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined all channels yet!", show_alert=True)

    elif call.data.startswith("ord_acc"):
        _, target_id, qty = call.data.split(":")
        
        # মেসেজ থেকে লিঙ্ক বের করা
        original_msg = call.message.text
        try:
            link = original_msg.split("🔗 Lɪɴᴋ: ")[1].split("\n")[0]
        except:
            link = db["users"].get(target_id, {}).get("temp_link", "")

        # --- SMM Panel এ অর্ডার পাঠানো ---
        smm_response = place_smm_order(link, qty)
        
        if "order" in smm_response:
            order_id = smm_response["order"]
            status_text = f"✅ <b>Order Accepted & Sent to SMM!</b>\nOrder ID: {order_id}\nUser ID: {target_id}\nQty: {qty}"
            bot.edit_message_text(status_text, call.message.chat.id, call.message.message_id)
            bot.send_message(LOG_GROUP_ID, f"✅ <b>Order Processed!</b>\n👤 User ID: {target_id}\n📊 Qty: {qty}\n🆔 SMM ID: {order_id}\nStatus: 🟢 Complete")
            try: bot.send_message(target_id, f"🥳 <b>Your order for {qty} subscribers has been accepted and is being processed!</b>")
            except: pass
        else:
            error_msg = smm_response.get("error", "Unknown SMM Error")
            bot.answer_callback_query(call.id, f"❌ SMM Error: {error_msg}", show_alert=True)
            bot.edit_message_text(f"❌ <b>SMM API ERROR</b>\n{error_msg}", call.message.chat.id, call.message.message_id)

    elif call.data.startswith("ord_rej"):
        _, target_id, qty = call.data.split(":")
        qty = int(qty)
        if target_id in db["users"]:
            db["users"][target_id]["coins"] += qty
            save_data(db)
        
        bot.edit_message_text(f"❌ <b>Order Rejected!</b>\nUser ID: {target_id}\nQty: {qty}\n(Coins Refunded)", call.message.chat.id, call.message.message_id)
        bot.send_message(LOG_GROUP_ID, f"❌ <b>Order Rejected!</b>\n👤 User ID: {target_id}\n📊 Qty: {qty}\nStatus: 🔴 Refunded")
        try: bot.send_message(target_id, f"❌ <b>Your order for {qty} subscribers was rejected and coins refunded.</b>")
        except: pass

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()