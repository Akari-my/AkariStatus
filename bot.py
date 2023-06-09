import telebot
import requests
import socket
import json
from telebot import types

# Inserisci il tuo token del bot di Telegram
API_TOKEN = '6192433648:AAH6lBH4F70wJJakAmEEJvexpfx8aKZiSpQ'

bot = telebot.TeleBot(API_TOKEN)

admin_id = "5854028945"
user_stats = {}

def get_java_server_status(server_ip):
    url = f"https://api.mcsrvstat.us/2/{server_ip}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_bedrock_server_status(server_ip):
    url = f"https://api.mcsrvstat.us/bedrock/2/{server_ip}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def load_user_stats():
    try:
        with open('user_stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_stats(user_stats):
    with open('user_stats.json', 'w') as f:
        json.dump(user_stats, f)


user_stats = load_user_stats()

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()

    git_button = types.InlineKeyboardButton(text="👨‍💻 Developer 👨‍💻", url="https://t.me/akari_m")

    username = message.from_user.username

    user_id = message.from_user.id
    user_stats[user_id] = user_stats.get(user_id, 0) + 1
    save_user_stats(user_stats)

    keyboard.add(git_button)

    bot.send_message(message.chat.id, f"👋| Benvenuto @{username} nel bot AkariStatus!\n\n🤖| Questo bot ti darà le informazioni dei server Minecraft Java e Bedrock....\n\n/java <ip>\n/bedrock <ip>\n\n©️ | Copyright by @akari_m\n\n", reply_markup=keyboard)


@bot.message_handler(commands=['stats'])
def stats(message):
    if str(message.from_user.id) == admin_id:
        total_users = len(user_stats)
        bot.send_message(admin_id, f"🙎‍♂️ {total_users} Users.")
    else:
        bot.send_message(message.chat.id, "Non hai il permesso di utilizzare questo comando.")





@bot.message_handler(commands=['java'])
def send_java_status(message):
    send_status(message, bedrock=False)

@bot.message_handler(commands=['bedrock'])
def send_bedrock_status(message):
    send_status(message, bedrock=True)

def send_status(message, bedrock=False):
    try:
        # Estrai l'IP del server Minecraft dal messaggio
        server_ip = message.text.split(' ')[1]
    except IndexError:
        server_type = "Java" if not bedrock else "Bedrock"
        bot.reply_to(message, f"Devi fornire l'IP del server Minecraft {server_type}: /{server_type.lower()} <ip server minecraft {server_type}>")
        return

    server_status = get_java_server_status(server_ip) if not bedrock else get_bedrock_server_status(server_ip)

    if server_status and server_status["online"]:
        try:
            # Risolve il nome host in un indirizzo IP numerico
            numeric_ip = socket.gethostbyname(server_ip)
        except socket.gaierror:
            numeric_ip = "Sconosciuto"

        software = server_status.get('software', 'Sconosciuto')
        server_type = "Java" if not bedrock else "Bedrock"
        response = (
            f"Status {server_type} {server_ip}\n\n"
            f"IP: {numeric_ip}\n"
            f"Porta: {server_status['port']}\n"
            f"Software: {software}\n"
            f"Giocatori online: {server_status['players']['online']}/{server_status['players']['max']}\n"
        )
    else:
        server_type = "Java" if not bedrock else "Bedrock"
        response = f"Impossibile ottenere lo stato del server {server_type} {server_ip}"

    bot.send_message(message.chat.id, response)

if __name__ == '__main__':
    bot.polling()