import os
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- Flask keep-alive para Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- Lógica del bot ---
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text
    bot_username = context.bot.username

    # Solo responde si le mencionan o es chat privado
    es_privado = update.message.chat.type == "private"
    lo_mencionaron = f"@{bot_username}" in mensaje

    if not es_privado and not lo_mencionaron:
        return

    # Limpia la mención del texto
    texto = mensaje.replace(f"@{bot_username}", "").strip()

    await update.message.chat.send_action("typing")

    respuesta = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="Eres un asistente útil en un grupo de Telegram. Responde de forma clara y concisa en el idioma del usuario.",
        messages=[{"role": "user", "content": texto}]
    )

    await update.message.reply_text(respuesta.content[0].text)

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    telegram_app = ApplicationBuilder().token(token).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    # Corre Flask en hilo separado
    Thread(target=run_flask, daemon=True).start()

    print("Bot corriendo...")
    telegram_app.run_polling()

if __name__ == "__main__":
    main()
