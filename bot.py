import os
import json
import threading
import time
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

print("="*60)
print("🔥 PREMIUM WELCOME BOT STARTING...")
print("="*60)

# ============ FLASK ============
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "Premium Welcome Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ============ CONFIG ============
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = 7760830347

# ============ FILES ============
USERS_FILE = "users.json"
LOGS_FILE = "logs.json"
ADMINS_FILE = "admins.json"
BANNED_FILE = "banned.json"
VIDEOS_FILE = "videos.json"

# ============ BUTTONS (UPDATED LINKS) ============
CHANNEL1_NAME = "🔞 Demo Porn Video"
CHANNEL1_LINK = "https://t.me/DEMOxPORN"

CHANNEL2_NAME = "🔥 PRIME VIDEOS BABY"
CHANNEL2_LINK = "https://t.me/+r01wW1uP4so5ZTY1"

PREMIUM_USERNAME = "PORNxVIP"
WELCOME_PHOTO = "https://i.ibb.co/8wQB8sd/photo-AQADPx-Fr-G3e6c-VZ.jpg"

# ============ DATABASE ============
def load_json(f, default=None):
    if os.path.exists(f):
        try:
            with open(f, 'r', encoding='utf-8') as x:
                data = json.load(x)
                if data is None:
                    return default
                return data
        except:
            return default
    return default

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
    if not isinstance(banned, list):
        return False
    return str(user_id) in banned

def ban_user(user_id):
    banned = load_json(BANNED_FILE, [])
    if not isinstance(banned, list):
        banned = []
    if str(user_id) not in banned:
        banned.append(str(user_id))
        save_json(BANNED_FILE, banned)
        return True
    return False

def unban_user(user_id):
    banned = load_json(BANNED_FILE, [])
    if not isinstance(banned, list):
        banned = []
    if str(user_id) in banned:
        banned.remove(str(user_id))
        save_json(BANNED_FILE, banned)
        return True
    return False

# ============ USERS ============
def register_user(user_id, username, first_name):
    users = load_json(USERS_FILE, {})
    if not isinstance(users, dict):
        users = {}
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
    data = load_json(USERS_FILE, {})
    if not isinstance(data, dict):
        return {}
    return data

# ============ LOGS ============
def add_log(user_id, username, action, details=""):
    logs = load_json(LOGS_FILE, [])
    if not isinstance(logs, list):
        logs = []
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
    data = load_json(LOGS_FILE, [])
    if not isinstance(data, list):
        return []
    return data

# ============ VIDEOS ============
def get_videos():
    return load_json(VIDEOS_FILE, [])

def add_video(file_id, caption=""):
    videos = get_videos()
    if not isinstance(videos, list):
        videos = []
    videos.append({
        "file_id": file_id,
        "caption": caption,
        "added": str(datetime.now())
    })
    save_json(VIDEOS_FILE, videos)
    return True

def get_all_videos():
    return get_videos()

# ============ PREMIUM STYLE ============
def fancy(text):
    fancy_map = {
        'A':'𝘼','B':'𝘽','C':'𝘾','D':'𝘿','E':'𝙀','F':'𝙁','G':'𝙂','H':'𝙃',
        'I':'𝙄','J':'𝙅','K':'𝙆','L':'𝙇','M':'𝙈','N':'𝙉','O':'𝙊','P':'𝙋',
        'Q':'𝙌','R':'𝙍','S':'𝙎','T':'𝙏','U':'𝙐','V':'𝙑','W':'𝙒','X':'𝙓',
        'Y':'𝙔','Z':'𝙕','a':'𝙖','b':'𝙗','c':'𝙘','d':'𝙙','e':'𝙚','f':'𝙛',
        'g':'𝙜','h':'𝙝','i':'𝙞','j':'𝙟','k':'𝙠','l':'𝙡','m':'𝙢','n':'𝙣',
        'o':'𝙤','p':'𝙥','q':'𝙦','r':'𝙧','s':'𝙨','t':'𝙩','u':'𝙪','v':'𝙫',
        'w':'𝙬','x':'𝙭','y':'𝙮','z':'𝙯'
    }
    return ''.join(fancy_map.get(c, c) for c in text)

# ============ COMMANDS ============

async def start_command(update, context):
    try:
        user = update.effective_user
        user_id = user.id
        username = user.username or "Unknown"
        first_name = user.first_name or "User"
        
        register_user(user_id, username, first_name)
        add_log(user_id, username, "STARTED BOT")
        
        if is_banned(user_id):
            await update.message.reply_text("🚫 You are banned!")
            return
        
        photo_url = WELCOME_PHOTO
        
        keyboard = [
            [InlineKeyboardButton(f"🔞 {fancy('Demo Porn Video')}", url=CHANNEL1_LINK)],
            [InlineKeyboardButton(f"🔥 {fancy('Main Channel')}", url=CHANNEL2_LINK)],
            [InlineKeyboardButton(f"💎 {fancy('Buy Premium')}", url=f"https://t.me/{PREMIUM_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        caption = f"""🔥 {fancy('Welcome')} {fancy(first_name)}!

📌 {fancy('Join our channels for updates')}
💎 {fancy('Buy premium for exclusive features')}

{fancy('Use /help for commands')}
👑 {fancy('Bot Owner')}: @{PREMIUM_USERNAME}"""
        
        await update.message.reply_photo(
            photo=photo_url,
            caption=caption,
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def help_command(update, context):
    user_id = update.effective_user.id
    
    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned!")
        return
    
    msg = f"""{fancy('📌 HELP MENU')}
{fancy('========================')}
/start - {fancy('Welcome')}
/help - {fancy('This menu')}
/owner - {fancy('Admin panel (Admins only)')}
/videos - {fancy('Watch videos')}

{fancy('Commands')}:
/approve USER_ID - {fancy('Add admin (Owner only)')}
/removeadmin USER_ID - {fancy('Remove admin (Owner only)')}
/ban USER_ID - {fancy('Ban user (Admin only)')}
/unban USER_ID - {fancy('Unban user (Admin only)')}
/users - {fancy('List all users (Admin only)')}
/logs - {fancy('View logs (Owner only)')}
/uploadvideo - {fancy('Upload video (Admin only)')}
{fancy('========================')}
{fancy('Bot Owner')}: @{PREMIUM_USERNAME}"""
    
    await update.message.reply_text(msg)

async def videos_command(update, context):
    user_id = update.effective_user.id
    
    if is_banned(user_id):
        await update.message.reply_text("🚫 You are banned!")
        return
    
    videos = get_all_videos()
    
    if not videos:
        await update.message.reply_text("📭 No videos uploaded yet!")
        return
    
    total = len(videos)
    await update.message.reply_text(f"📹 {fancy('Total Videos')}: {total}")
    
    for video in videos[:5]:  # Max 5 videos per request
        try:
            await update.message.reply_video(
                video=video["file_id"],
                caption=video.get("caption", "")
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending video: {e}")

async def owner_command(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    add_log(user_id, username, "OPENED OWNER PANEL")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    total_users = len(get_all_users())
    total_logs = len(get_logs())
    total_videos = len(get_all_videos())
    
    msg = f"""{fancy('👑 OWNER PANEL')}
{fancy('========================')}
{fancy('User ID')}: {user_id}
{fancy('Total Users')}: {total_users}
{fancy('Total Logs')}: {total_logs}
{fancy('Total Videos')}: {total_videos}

{fancy('Admin Commands')}:
/approve USER_ID - {fancy('Add admin')}
/removeadmin USER_ID - {fancy('Remove admin')}
/ban USER_ID - {fancy('Ban user')}
/unban USER_ID - {fancy('Unban user')}
/users - {fancy('List all users')}
/logs - {fancy('View logs')}
/uploadvideo - {fancy('Upload video (reply to video)')}
/videos - {fancy('View all videos')}
{fancy('========================')}
{fancy('Bot Owner')}: @{PREMIUM_USERNAME}"""
    
    await update.message.reply_text(msg)

async def uploadvideo_command(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("📝 Reply to a video with /uploadvideo")
        return
    
    video = update.message.reply_to_message.video
    if not video:
        await update.message.reply_text("❌ Please reply to a video file!")
        return
    
    file_id = video.file_id
    caption = update.message.reply_to_message.caption or ""
    
    add_video(file_id, caption)
    add_log(user_id, username, "UPLOADED VIDEO", f"Caption: {caption[:30]}")
    
    await update.message.reply_text(f"✅ {fancy('Video uploaded successfully!')}")

async def approve_command(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
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
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
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
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
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
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
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
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    add_log(user_id, username, "VIEWED USERS")
    
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("No users yet!")
        return
    
    msg = f"👥 {fancy('TOTAL USERS')}: {len(users)}\n{fancy('========================')}\n"
    for uid, data in list(users.items())[:20]:
        status = "🚫 BANNED" if is_banned(int(uid)) else "✅ ACTIVE"
        uname = data.get('username', 'Unknown')
        msg += f"ID: {uid} | @{uname} | {status}\n"
    
    if len(users) > 20:
        msg += f"\n... and {len(users)-20} more"
    
    await update.message.reply_text(msg)

async def logs_command(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only owner can view logs!")
        return
    
    logs = get_logs()
    
    if not logs:
        await update.message.reply_text("No logs yet!")
        return
    
    msg = f"📋 {fancy('TOTAL LOGS')}: {len(logs)}\n{fancy('========================')}\n"
    for log in list(logs)[-20:]:
        uname = log.get('username', 'Unknown')
        action = log.get('action', '')
        details = log.get('details', '')
        log_time = log.get('time', '')
        msg += f"👤 @{uname}\n📌 {action}"
        if details:
            msg += f"\n📝 {details}"
        msg += f"\n🕐 {log_time}\n{fancy('------------------------')}\n"
    
    await update.message.reply_text(msg)

# ============ MAIN ============
def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    time.sleep(2)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("videos", videos_command))
    application.add_handler(CommandHandler("owner", owner_command))
    application.add_handler(CommandHandler("uploadvideo", uploadvideo_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("removeadmin", removeadmin_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("logs", logs_command))
    
    print("="*60)
    print("🔥 PREMIUM WELCOME BOT STARTED SUCCESSFULLY!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📢 Channel 1 (Demo Porn): {CHANNEL1_LINK}")
    print(f"📢 Channel 2 (Main): {CHANNEL2_LINK}")
    print(f"💎 Premium: @{PREMIUM_USERNAME}")
    print("="*60)
    
    application.run_polling()

if __name__ == "__main__":
    main()
