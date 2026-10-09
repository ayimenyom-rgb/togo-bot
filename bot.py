import os, json, uuid, glob, threading
import telebot, yt_dlp
from flask import Flask

TOKEN = "8853673018:AAHx8guyhVOSeXkRGOaroPz26xSX41q7ei4"
ADMIN_ID = 8853673018

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot Togo OK"
def run_flask(): app_flask.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

bot = telebot.TeleBot(TOKEN, threaded=False)
db = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "BOT TOGO 🇹🇬\nEnvoie un lien TikTok maintenant!")

@bot.message_handler(func=lambda x: "http" in x.text)
def dl(m):
    msg = bot.reply_to(m, "⏳ Telechargement...")
    fid = str(uuid.uuid4())[:6]
    try:
        opts = {'format':'mp4','outtmpl':fid+'.mp4','quiet':True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([m.text.strip()])
        with open(fid+'.mp4','rb') as f:
            bot.send_video(m.chat.id, f, caption="Voila 🇹🇬")
        bot.delete_message(m.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"Erreur: {e}", m.chat.id, msg.message_id)
    finally:
        for fn in glob.glob(f"{fid}*"):
            try: os.remove(fn)
            except: pass

bot.remove_webhook()
bot.infinity_polling()
