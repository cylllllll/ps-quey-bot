import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler
from notion_client import Client

# Load API keys
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
ALLOWED_GROUP_IDS = os.getenv("ALLOWED_GROUP_IDS", "").split(",")

notion = Client(auth=NOTION_TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def is_allowed(update: Update):
    if not ALLOWED_GROUP_IDS or ALLOWED_GROUP_IDS == [""]:
        return True
    return str(update.effective_chat.id) in ALLOWED_GROUP_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot ready! Send /query <game_name>")

async def query_notion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Please provide a game name.")
        return

    # Basic query logic
    results = notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": "Name",
                "title": { "contains": query }
            }
        }
    )
    
    if not results["results"]:
        await update.message.reply_text("No results found.")
    else:
        # Simplistic display
        text = "\n".join([r['properties']['Name']['title'][0]['plain_text'] for r in results['results'][:5]])
        await update.message.reply_text(f"Found:\n{text}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    query_handler = CommandHandler('query', query_notion)
    application.add_handler(start_handler)
    application.add_handler(query_handler)
    
    application.run_polling()
