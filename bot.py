import telebot
import requests
import socket

# Inserisci il tuo token del bot di Telegram
API_TOKEN = '6192433648:AAH6lBH4F70wJJakAmEEJvexpfx8aKZiSpQ'

bot = telebot.TeleBot(API_TOKEN)

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
            f"Status {server_type} {server_ip}\n"
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