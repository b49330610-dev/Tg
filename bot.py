import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

print("="*60)
print("🔥 WELCOME BOT STARTING...")
print("="*60)

# ============ FLASK ============
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "Welcome Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ============================================================
# 🔥 SIRF RENDER VARIABLES SE LENA HAI
# ============================================================
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = int(os.environ.get('OWNER_ID', 7760830347))  # ⬅️ UPDATED
# ============================================================

# ============ FILES ============
USERS_FILE = "users.json"
LOGS_FILE = "logs.json"
ADMINS_FILE = "admins.json"
BANNED_FILE = "banned.json"

# ============ BUTTONS ============
CHANNEL1_NAME = "Main Channel"
CHANNEL1_LINK = "https://t.me/yourchannel1"
CHANNEL2_NAME = "Backup Channel"
CHANNEL2_LINK = "https://t.me/yourchannel2"
PREMIUM_USERNAME = "PORNxVIP"  # ⬅️ UPDATED

# ============ DATABASE ============
def load_json(f, default=None):
    if os.path.exists(f):
        try:
            with open(f, 'r', encoding='utf-8') as x:
                return json.load(x)
        except:
            return default or {}
    return default or {}

def save_json(f, d):
    with open(f, 'w', encoding='utf-8') as x:
        json.dump(d, x, indent=2, ensure_ascii=False)

# ============ ADMINS ============
def get_admins():
    data = load_json(ADMINS_FILE, [])
    if not isinstance(data, list):
        data = []
    if OWNER_ID not in data:
        data.append(OWNER_ID)
        save_json(ADMINS_FILE, data)
    return data

def is_admin(user_id):
    return user_id in get_admins()

def add_admin(user_id):
    admins = get_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_json(ADMINS_FILE, admins)
        return True
    return False

def remove_admin(user_id):
    admins = get_admins()
    if user_id in admins and user_id != OWNER_ID:
        admins.remove(user_id)
        save_json(ADMINS_FILE, admins)
        return True
    return False

# ============ BANNED ============
def is_banned(user_id):
    banned = load_json(BANNED_FILE, [])
    return str(user_id) in banned

def ban_user(user_id):
    banned = load_json(BANNED_FILE, [])
    if str(user_id) not in banned:
        banned.append(str(user_id))
        save_json(BANNED_FILE, banned)
        return True
    return False

def unban_user(user_id):
    banned = load_json(BANNED_FILE, [])
    if str(user_id) in banned:
        banned.remove(str(user_id))
        save_json(BANNED_FILE, banned)
        return True
    return False

# ============ USERS ============
def register_user(user_id, username, first_name):
    users = load_json(USERS_FILE, {})
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "username": username,
            "name": first_name,
            "joined": str(datetime.now())
        }
        save_json(USERS_FILE, users)
        return True
    return False

def get_all_users():
    return load_json(USERS_FILE, {})

# ============ LOGS ============
def add_log(user_id, username, action, details=""):
    logs = load_json(LOGS_FILE, [])
    logs.append({
        "user_id": user_id,
        "username": username,
        "action": action,
        "details": details,
        "time": str(datetime.now())
    })
    save_json(LOGS_FILE, logs)
    return True

def get_logs():
    return load_json(LOGS_FILE, [])

# ============ COMMANDS ============

async def start_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    first_name = user.first_name or "User"
    
    register_user(user_id, username, first_name)
    add_log(user_id, username, "STARTED BOT", f"First name: {first_name}")
    
    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned!")
        return
    
    photo_url = "https://i.ibb.co/GfbR62Gt/photo-AQADy-BBr-G3e6c-VZ.jpg"
    
    keyboard = [
        [InlineKeyboardButton(f"📢 {CHANNEL1_NAME}", url=CHANNEL1_LINK)],
        [InlineKeyboardButton(f"📢 {CHANNEL2_NAME}", url=CHANNEL2_LINK)],
        [InlineKeyboardButton("💎 Buy Premium", url=f"https://t.me/{PREMIUM_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = f"""
👋 Welcome {first_name}!

📌 Join our channels for updates
💎 Buy premium for exclusive features

📌 Use /help for commands
    """
    
    await update.message.reply_photo(
        photo=photo_url,
        caption=caption,
        reply_markup=reply_markup
    )

async def help_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    add_log(user_id, username, "HELP COMMAND")
    
    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned!")
        return
    
    msg = """
📌 HELP MENU
========================
/start - Welcome
/help - This menu
/owner - Admin panel (Admins only)

========================
    """
    await update.message.reply_text(msg)

async def owner_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    add_log(user_id, username, "OPENED OWNER PANEL")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    logs = get_logs()
    total_users = len(get_all_users())
    total_logs = len(logs)
    
    msg = f"""
👑 OWNER PANEL
========================
User ID: {user_id}
Total Users: {total_users}
Total Logs: {total_logs}

Admin Commands:
/approve USER_ID - Add admin
/removeadmin USER_ID - Remove admin
/ban USER_ID - Ban user
/unban USER_ID - Unban user
/users - List all users
/logs - View logs
========================
    """
    await update.message.reply_text(msg)

async def approve_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only bot owner can approve!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID")
        return
    
    try:
        new_admin = int(context.args[0])
        if add_admin(new_admin):
            add_log(user_id, username, "APPROVED ADMIN", f"User {new_admin}")
            await update.message.reply_text(f"✅ User {new_admin} approved as admin!")
        else:
            await update.message.reply_text(f"⚠️ User {new_admin} already admin!")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def removeadmin_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only bot owner can remove admins!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /removeadmin USER_ID")
        return
    
    try:
        admin_id = int(context.args[0])
        if remove_admin(admin_id):
            add_log(user_id, username, "REMOVED ADMIN", f"User {admin_id}")
            await update.message.reply_text(f"✅ Admin {admin_id} removed!")
        else:
            await update.message.reply_text(f"⚠️ Cannot remove {admin_id}")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def ban_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban USER_ID")
        return
    
    try:
        target_id = int(context.args[0])
        if target_id == OWNER_ID:
            await update.message.reply_text("❌ Cannot ban owner!")
            return
        if ban_user(target_id):
            add_log(user_id, username, "BANNED USER", f"User {target_id}")
            await update.message.reply_text(f"✅ User {target_id} banned!")
        else:
            await update.message.reply_text(f"⚠️ User {target_id} already banned!")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def unban_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban USER_ID")
        return
    
    try:
        target_id = int(context.args[0])
        if unban_user(target_id):
            add_log(user_id, username, "UNBANNED USER", f"User {target_id}")
            await update.message.reply_text(f"✅ User {target_id} unbanned!")
        else:
            await update.message.reply_text(f"⚠️ User {target_id} not banned!")
    except:
        await update.message.reply_text("❌ Invalid user ID!")

async def users_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    add_log(user_id, username, "VIEWED USERS")
    
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("No users yet!")
        return
    
    msg = f"👥 TOTAL USERS: {len(users)}\n========================\n"
    for uid, data in list(users.items())[:20]:
        status = "🚫 BANNED" if is_banned(int(uid)) else "✅ ACTIVE"
        msg += f"ID: {uid} | @{data.get('username', 'Unknown')} | {status}\n"
    
    if len(users) > 20:
        msg += f"\n... and {len(users)-20} more"
    
    await update.message.reply_text(msg)

async def logs_command(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only owner can view logs!")
        return
    
    logs = get_logs()
    
    if not logs:
        await update.message.reply_text("No logs yet!")
        return
    
    msg = f"📋 TOTAL LOGS: {len(logs)}\n========================\n"
    for log in list(logs)[-20:]:
        msg += f"👤 @{log.get('username', 'Unknown')}\n"
        msg += f"📌 {log.get('action', '')}\n"
        if log.get('details'):
            msg += f"📝 {log.get('details', '')}\n"
        msg += f"🕐 {log.get('time', '')}\n"
        msg += "------------------------\n"
    
    await update.message.reply_text(msg)

# ============ MAIN ============
def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("owner", owner_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("removeadmin", removeadmin_command))
    application.add_handler(CommandHandler("logs", logs_command))
    
    print("="*60)
    print("✅ WELCOME BOT STARTED SUCCESSFULLY!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📢 Channel 1: {CHANNEL1_NAME} - {CHANNEL1_LINK}")
    print(f"📢 Channel 2: {CHANNEL2_NAME} - {CHANNEL2_LINK}")
    print(f"💎 Premium: @{PREMIUM_USERNAME}")
    print("="*60)
    
    application.run_polling()

if __name__ == "__main__":
    main()