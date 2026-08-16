import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import os

# ================= Configuration =================
TOKEN = "8789663271:AAGvegQaN115LF6hgQYLxHwAFD93H8LVli8"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7743715314
CHANNEL_LINK = "https://t.me/+3BeaW6cXHkBiZmE1"
BOT_TASK_LINK = "https://t.me/CloudFarmWalletBot/cloud?startapp=7743715314"
CHANNEL_ID = "-1002545140979" 

DB_FILE = "database.json"

# ================= Database Functions =================
def load_db():
    if not os.path.exists(DB_FILE):
        return {"gift_codes": {}}
    with open(DB_FILE, "r") as f:
        db = json.load(f)
        if "gift_codes" not in db:
            db["gift_codes"] = {}
        return db

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

user_states = {}

# ================= Main Menu =================
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("👤 My Account"),
        KeyboardButton("🔗 Invite & Earn"),
        KeyboardButton("💳 Withdraw Funds"),
        KeyboardButton("🎧 Support Center"),
        KeyboardButton("🎁 Redeem Gift Code")
    )
    return markup

# ================= Admin Commands (Gift Codes & Broadcast) =================
@bot.message_handler(commands=['addgift'])
def add_gift(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split()
        code = args[1].upper()
        amount = float(args[2])
        limit = int(args[3]) 
        
        db = load_db()
        db["gift_codes"][code] = {"amount": amount, "limit": limit, "claims": 0}
        save_db(db)
        
        bot.reply_to(message, f"✅ **Gift Code Successfully Created!**\n\n🎁 Code: `{code}`\n💰 Reward: **${amount}**\n👥 Max Claims: **{limit} users**", parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ **Invalid Format!**\nUse: `/addgift <CODE> <AMOUNT> <LIMIT>`\nExample: `/addgift NEWYEAR 5 10`", parse_mode="Markdown")

@bot.message_handler(commands=['delgift'])
def del_gift(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        code = message.text.split()[1].upper()
        db = load_db()
        
        if code in db["gift_codes"]:
            del db["gift_codes"][code]
            save_db(db)
            bot.reply_to(message, f"🗑️ Gift code `{code}` has been successfully removed!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Code not found in the active list.")
    except:
        bot.reply_to(message, "⚠️ **Format error!**\nUse: `/delgift <CODE>`\nExample: `/delgift NEWYEAR`", parse_mode="Markdown")

@bot.message_handler(commands=['gifts'])
def list_gifts(message):
    if message.from_user.id != ADMIN_ID:
        return
    db = load_db()
    codes = db.get("gift_codes", {})
    
    if not codes:
        bot.reply_to(message, "⚠️ No active gift codes available at the moment.")
        return
        
    text = "🎁 **Active Gift Codes Dashboard:**\n\n"
    for c, data in codes.items():
        if isinstance(data, dict):
            text += f"▪️ `{c}` : **${data['amount']}** ({data['claims']}/{data['limit']} claimed)\n"
        else:
            text += f"▪️ `{c}` : **${data}** (Old format)\n"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not message.reply_to_message and len(message.text.split(maxsplit=1)) < 2:
        bot.reply_to(message, "⚠️ **Invalid Format!**\nUse: `/broadcast <message>` or reply to any message (photo, text, video) with `/broadcast`", parse_mode="Markdown")
        return

    db = load_db()
    success_count = 0
    failed_count = 0
    
    bot.reply_to(message, "📢 **Broadcast started...** Please wait.", parse_mode="Markdown")
    
    for user_id in list(db.keys()):
        if user_id == "gift_codes":
            continue
        try:
            if message.reply_to_message:
                bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
            else:
                broadcast_text = message.text.split(maxsplit=1)[1]
                bot.send_message(user_id, broadcast_text, parse_mode="Markdown")
            success_count += 1
        except Exception as e:
            failed_count += 1
            
    bot.send_message(
        ADMIN_ID,
        f"✅ **Broadcast System Report**\n\n"
        f"📤 Successfully sent: `{success_count}` users\n"
        f"❌ Failed (Blocked bot): `{failed_count}` users",
        parse_mode="Markdown"
    )

# ================= Start Command =================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None

    db = load_db()
    if user_id not in db:
        db[user_id] = {"balance": 0, "referred_by": referrer_id, "referrals": 0, "joined": False, "used_codes": []}
        save_db(db)

    markup = InlineKeyboardMarkup(row_width=1)
    btn_channel = InlineKeyboardButton("📢 Join Official Channel", url=CHANNEL_LINK)
    btn_bot = InlineKeyboardButton("🤖 Start Partner Task", url=BOT_TASK_LINK)
    btn_confirm = InlineKeyboardButton("✅ I Have Completed The Tasks", callback_data="check_join")
    markup.add(btn_channel, btn_bot, btn_confirm)

    welcome_text = (
        "🚀 **Welcome to USDT MANIA!**\n\n"
        "To unlock all features and start earning, you must complete two quick steps:\n\n"
        "**Step 1:** Join our official Telegram channel.\n"
        "**Step 2:** Start our partner bot task.\n\n"
        "⏳ _Once you have completed both steps, click the button below to verify._"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# ================= Callbacks (Confirm & Withdraw) =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.from_user.id)
    db = load_db()

    if call.data == "check_join":
        try:
            status = bot.get_chat_member(CHANNEL_ID, user_id).status
            if status in ['member', 'administrator', 'creator']:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                
                if not db[user_id].get("joined", False):
                    db[user_id]["joined"] = True
                    referrer = db[user_id].get("referred_by")
                    if referrer and referrer in db and referrer != user_id:
                        db[referrer]["balance"] += 1
                        db[referrer]["referrals"] += 1
                        bot.send_message(referrer, "🎊 **Referral Success!** A new user joined using your link. **$1.00** has been credited to your wallet.")
                    save_db(db)

                bot.send_message(
                    call.message.chat.id, 
                    "🎉 **Verification Successful!**\n\nWelcome aboard! Your account is now fully active. Use the menu below to navigate.", 
                    reply_markup=main_menu(),
                    parse_mode="Markdown"
                )
            else:
                bot.answer_callback_query(call.id, "⚠️ Verification Failed: Please make sure you have joined the channel.", show_alert=True)
        except Exception as e:
            bot.answer_callback_query(call.id, "System Error: Bot is not functioning properly in the channel.", show_alert=True)

    elif call.data == "proceed_to_payment":
        wallet = db[user_id].get("temp_wallet")
        amount = db[user_id].get("temp_withdraw_amount")
        
        if not amount or not wallet:
            bot.answer_callback_query(call.id, "Session expired. Please try again.", show_alert=True)
            return
            
        fee_usd = amount * 0.05 # 5% Fee in USD
        fee_inr = fee_usd * 85 # Calculation for INR equivalent
        
        db[user_id]["temp_fee_usd"] = fee_usd
        save_db(db)
        
        upi_id = "winrahaman@fam"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa={upi_id}&pn=USDT%20Mania&am={fee_inr:.2f}&cu=INR"

        user_states[user_id] = "waiting_for_utr"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ I Have Paid (Submit UTR)", callback_data="submit_utr_prompt"))

        payment_text = (
            "🛡️ **Fee Payment Required (5%)**\n\n"
            f"💵 Withdrawal Amount: **${amount:.2f} USDT**\n"
            f"⚙️ Fee (5%): **${fee_usd:.2f} USDT** (Approx. **₹{fee_inr:.2f} INR**)\n\n"
            f"📌 **Please pay the fee to the UPI ID below:**\n"
            f"🔹 UPI ID: `{upi_id}`\n\n"
            "Scan the QR code below using any UPI app (GPay, PhonePe, Paytm, etc.) to complete the payment."
        )
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_photo(call.message.chat.id, qr_url, caption=payment_text, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "submit_utr_prompt":
        bot.send_message(call.message.chat.id, "📝 Please reply with your **12-digit UTR / Transaction ID** of the payment you made:", parse_mode="Markdown")

# ================= Menu Button Handlers =================
@bot.message_handler(func=lambda message: message.text in ["👤 My Account", "🔗 Invite & Earn", "💳 Withdraw Funds", "🎧 Support Center", "🎁 Redeem Gift Code"])
def handle_menu(message):
    user_id = str(message.from_user.id)
    db = load_db()
    
    if message.text == "👤 My Account":
        balance = db.get(user_id, {}).get("balance", 0)
        text = (
            "👤 **Account Dashboard**\n\n"
            f"💼 **Current Balance:** `${balance:.2f}` USDT\n"
            f"📈 **Status:** Active\n\n"
            "_Keep earning by referring friends or claiming exclusive gift codes!_"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
    elif message.text == "🔗 Invite & Earn":
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        refs = db.get(user_id, {}).get("referrals", 0)
        text = (
            "🚀 **Referral Program**\n\n"
            "Build your network and earn passive income! You will receive **$1.00 USDT** for every valid user who joins using your link.\n\n"
            f"👥 **Your Total Invites:** {refs}\n\n"
            "🔗 **Your Unique Referral Link:**\n"
            f"`{ref_link}`\n\n"
            "_Tap the link to copy and share it with your friends!_"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
    elif message.text == "💳 Withdraw Funds":
        balance = db.get(user_id, {}).get("balance", 0)
        if balance >= 10:
            user_states[user_id] = "waiting_for_withdraw_amount"
            text = (
                "💳 **Initiate Withdrawal**\n\n"
                f"💰 **Your Balance:** `${balance:.2f} USDT`\n\n"
                "Please enter the **amount** you want to withdraw (e.g., 10, 15, 20).\n\n"
                "⚠️ _Rules:_\n"
                "▪️ Minimum: **$10**\n"
                "▪️ Maximum: **$50**\n"
                "▪️ Withdrawal Fee: **5% (Payable in INR via UPI)**"
            )
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ **Insufficient Funds**\n\nYou need a minimum balance of **$10.00 USDT** to request a withdrawal.", parse_mode="Markdown")
            
    elif message.text == "🎧 Support Center":
        user_states[user_id] = "waiting_for_support"
        bot.send_message(message.chat.id, "🎧 **Customer Support**\n\nDescribe your issue or ask your question in a single message below. Our admin team will respond to you as soon as possible.", parse_mode="Markdown")
        
    elif message.text == "🎁 Redeem Gift Code":
        user_states[user_id] = "waiting_for_gift_code"
        bot.send_message(message.chat.id, "🎁 **Gift Code Redemption**\n\nEnter your exclusive promotional code below to claim your free reward:", parse_mode="Markdown")

# ================= Text Input Handlers =================
@bot.message_handler(func=lambda message: str(message.from_user.id) in user_states)
def handle_user_input(message):
    user_id = str(message.from_user.id)
    state = user_states[user_id]
    
    if state == "waiting_for_withdraw_amount":
        try:
            amount = float(message.text)
            db = load_db()
            balance = db[user_id]["balance"]
            
            if amount < 10 or amount > 50:
                bot.send_message(message.chat.id, "❌ **Invalid Amount!**\nPlease enter an amount between **$10** and **$50**.")
            elif amount > balance:
                bot.send_message(message.chat.id, f"❌ **Insufficient Balance!**\nYou only have **${balance:.2f} USDT** in your account.")
            else:
                db[user_id]["temp_withdraw_amount"] = amount
                save_db(db)
                
                user_states[user_id] = "waiting_for_wallet"
                bot.send_message(message.chat.id, "✅ **Amount Accepted**\n\nPlease reply with your valid **USDT (BEP20)** wallet address where you want to receive your funds.\n\n⚠️ _Ensure the network is BEP20._", parse_mode="Markdown")
        except ValueError:
            bot.send_message(message.chat.id, "❌ **Invalid Input!**\nPlease enter a valid number (e.g., 10 or 15.5).")

    elif state == "waiting_for_wallet":
        wallet_address = message.text
        db = load_db()
        db[user_id]["temp_wallet"] = wallet_address
        amount = db[user_id].get("temp_withdraw_amount", 10)
        save_db(db)
        
        del user_states[user_id] 
        
        fee_usd = amount * 0.05 # 5% Fee
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Accept Terms & Pay Fee", callback_data="proceed_to_payment"))
        
        summary_text = (
            "🧾 **Withdrawal Summary & Terms:**\n\n"
            f"💵 **Requested Amount:** `${amount:.2f} USDT`\n"
            f"⚙️ **Withdrawal Fee (5%):** `${fee_usd:.2f} USDT` (Payable in INR)\n"
            f"💰 **You Will Receive:** `${amount:.2f} USDT` (in USDT)\n\n"
            f"🏦 **Destination Address:**\n`{wallet_address}`\n\n"
            "⚠️ *Terms & Conditions:*\n"
            "1. You will receive the full requested amount in USDT.\n"
            "2. A 5% fee must be paid in INR via UPI to proceed.\n"
            "3. Incorrect wallet addresses will lead to permanent loss.\n\n"
            "Do you accept the terms and wish to proceed to payment?"
        )
        
        bot.send_message(message.chat.id, summary_text, reply_markup=markup, parse_mode="Markdown")

    elif state == "waiting_for_utr":
        utr_number = message.text.strip()
        db = load_db()
        
        amount = db[user_id].get("temp_withdraw_amount", 0)
        wallet = db[user_id].get("temp_wallet", "")
        fee_usd = db[user_id].get("temp_fee_usd", 0)
        
        if db[user_id]["balance"] >= amount:
            db[user_id]["balance"] -= amount
            save_db(db)
            
            admin_msg = (
                f"🚨 **NEW WITHDRAWAL & FEE SUBMISSION** 🚨\n\n"
                f"👤 **User ID:** `{user_id}`\n"
                f"💵 **Withdrawal Amount:** `${amount:.2f} USDT`\n"
                f"⚙️ **Fee Paid (5%):** `${fee_usd:.2f} USDT` equivalent in INR\n"
                f"💳 **Wallet (BEP20):** `{wallet}`\n"
                f"📝 **UTR / Transaction ID:** `{utr_number}`\n\n"
                f"⚠️ _Admin Action: Verify the UTR in your bank/UPI app and reply directly to this message to approve._"
            )
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
            
            bot.send_message(
                message.chat.id, 
                "✅ **Withdrawal Successfully Submitted!**\n\n"
                "Your UTR has been received and sent for verification. Once approved by the admin, your USDT will be sent to your wallet.\n\n"
                "📌 _Status: Pending Admin Approval_", 
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
        else:
            bot.send_message(message.chat.id, "❌ Insufficient balance to complete this request.")
            
        del user_states[user_id]
        
    elif state == "waiting_for_support":
        bot.send_message(ADMIN_ID, f"📩 **New Support Ticket**\n\n👤 **User ID:** `{user_id}`\n💬 **Message:** {message.text}\n\n_Reply to this message to answer the user._", parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ **Message Sent!**\n\nYour query has been forwarded to the admin. Kindly wait for a response.", parse_mode="Markdown")
        del user_states[user_id]
        
    elif state == "waiting_for_gift_code":
        code = message.text.strip().upper() 
        db = load_db()
        
        if "used_codes" not in db[user_id]:
            db[user_id]["used_codes"] = []
            
        gift_data = db.get("gift_codes", {}).get(code)
        
        if gift_data and isinstance(gift_data, dict):
            if code in db[user_id]["used_codes"]:
                bot.send_message(message.chat.id, "⚠️ **Already Redeemed!**\nYou have already used this gift code.", parse_mode="Markdown")
            elif gift_data["claims"] >= gift_data["limit"]:
                bot.send_message(message.chat.id, "❌ **Code Expired!**\nThis gift code has reached its maximum claim limit.", parse_mode="Markdown")
            else:
                value = gift_data["amount"]
                db[user_id]["balance"] += value
                db[user_id]["used_codes"].append(code) 
                
                db["gift_codes"][code]["claims"] += 1
                save_db(db)
                
                bot.send_message(message.chat.id, f"🎉 **Congratulations!**\n\nYou successfully redeemed the code `{code}`.\n💰 **${value} USDT** has been instantly added to your wallet!", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ **Invalid Code!**\nPlease check your spelling and try again.", parse_mode="Markdown")
            
        del user_states[user_id]

# ================= Admin Reply Handler (Support & Withdraw) =================
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.reply_to_message)
def admin_reply(message):
    try:
        reply_text = message.reply_to_message.text
        
        if "NEW WITHDRAWAL & FEE SUBMISSION" in reply_text and "User ID:" in reply_text:
            user_id = reply_text.split("User ID: ")[1].split("\n")[0].strip('`')
            admin_note = message.text 
            
            success_msg = (
                f"🟢 **WITHDRAWAL APPROVED & PROCESSED** 🟢\n\n"
                f"Your fee payment has been verified and your withdrawal request has been successfully approved by the admin!\n\n"
                f"💬 **Admin Note / Txn Info:** {admin_note}\n\n"
                f"Thank you for using USDT MANIA!"
            )
            bot.send_message(user_id, success_msg, parse_mode="Markdown")
            bot.send_message(ADMIN_ID, "✅ **Withdrawal approved and user notified successfully!**", parse_mode="Markdown")
            
        elif "New Support Ticket" in reply_text and "User ID:" in reply_text:
            user_id = reply_text.split("User ID: ")[1].split("\n")[0].strip('`')
            bot.send_message(user_id, f"🎧 **Admin Response:**\n\n{message.text}", parse_mode="Markdown")
            bot.send_message(ADMIN_ID, "✅ Support reply sent successfully.")
            
    except Exception as e:
        bot.send_message(ADMIN_ID, "❌ Failed to send reply or process confirmation.")

# Start the bot
print("USDT MANIA Bot is running with Broadcast System & 5% INR Fee features...")
bot.infinity_polling()
