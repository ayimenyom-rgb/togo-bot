import os, json, uuid, glob, threading
import telebot
import yt_dlp
from flask import Flask

# === CONFIG ===
TOKEN = "8853673018:AAHx8guyhVOSeXkRGOaroPz26xSX41q7ei4"
DB_FILE = "users.json"
ADMIN_ID = 8853673018 # TON ID = début de ton token, tu es admin
# === FIN CONFIG ===

# Mini serveur pour Render (reste en ligne 24h/24)
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Togo OK 24/24"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

bot = telebot.TeleBot(TOKEN, threaded=False)

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return {}
def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)
db = load_db()

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)
    if uid not in db: db[uid] = {"free": 0, "premium": False}; save_db(db)
    bot.reply_to(m, f"🇹🇬 BOT TOGO TÉLÉCHARGEUR\n\nEnvoie lien TikTok / FB / YouTube / Insta\n\n🆔 Ton ID: {uid}\n🎁 Gratuit: 3/jour\n\n💎 /premium -> 500F illimité")

@bot.message_handler(commands=['premium'])
def prem(m):
    uid = str(m.from_user.id)
    bot.reply_to(m, f"💎 PREMIUM 500F / mois\n\n1. Envoie 500F sur TMoney: 92 31 69 98 (REMPLACE)\n2. Envoie capture + ID {uid} sur WhatsApp\n\nActivation en 5min!")

@bot.message_handler(commands=['activer'])
def activer(m):
    if m.from_user.id!= ADMIN_ID:
        bot.reply_to(m, f"Pas admin. Ton ID {m.from_user.id}"); return
    try:
        target = m.text.split()[1]
        if target not in db: db[target] = {"free": 0, "premium": False}
        db[target]["premium"] = True; save_db(db)
        bot.reply_to(m, f"✅ {target} est PREMIUM")
        bot.send_message(int(target), "🎉 Tu es PREMIUM illimité! Merci 🙏")
    except: bot.reply_to(m, "Usage: /activer ID_DU_CLIENT")

@bot.message_handler(func=lambda m: "http" in m.text)
def download_handler(m):
    uid = str(m.from_user.id)
    url = m.text.strip()
    if uid not in db: db[uid] = {"free": 0, "premium": False}
    if not db[uid].get("premium") and db[uid].get("free",0) >= 3:
        bot.reply_to(m, "❌ Limite 3/jour. Tape /premium pour 500F illimité"); return

    msg = bot.reply_to(m, "⏳ Téléchargement en cours...")
    filename = None
    uid_file = str(uuid.uuid4())[:8]
    try:
        # FORMAT CORRIGÉ - accepte tout
        opts={
            'format': 'mp4/best',
            'outtmpl': f'{uid_file}_%(title).20s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Cherche vrai fichier si nom différent
            if not os.path.exists(filename):
                matches = glob.glob(f"{uid_file}_*")
                if matches: filename = matches[0]

        if not filename or not os.path.exists(filename):
            raise Exception("Fichier non trouvé après DL")

        with open(filename, 'rb') as f:
            bot.send_video(m.chat.id, f, caption="✅ Voilà - Bot Togo 🇹🇬")

        db[uid]["free"] = db[uid].get("free",0) + 1; save_db(db)
        bot.delete_message(m.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Erreur: {str(e)[:400]}", m.chat.id, msg.message_id)
    finally:
        for f in glob.glob(f"{uid_file}_*"):
            try: os.remove(f)
            except: pass

print("Bot lancé... version 24/24")
bot.infinity_polling()
