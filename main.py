import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from notion_client import Client

# Load API keys
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
ALLOWED_GROUP_IDS = os.getenv("ALLOWED_GROUP_IDS", "").split(",")
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "").split(",")

notion = Client(auth=NOTION_TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def is_allowed(update: Update):
    chat_type = update.effective_chat.type
    chat_id = str(update.effective_chat.id)

    if chat_type == 'private':
        if not ALLOWED_USER_IDS or ALLOWED_USER_IDS == [""]:
            return True
        return chat_id in ALLOWED_USER_IDS
    else: # Group or Supergroup
        if not ALLOWED_GROUP_IDS or ALLOWED_GROUP_IDS == [""]:
            return True
        return chat_id in ALLOWED_GROUP_IDS

async def perform_notion_query(query, chat_id, message_to_reply):
    if not query:
        await message_to_reply.reply_text("请输入要查询的游戏名称。")
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
        await message_to_reply.reply_text("未找到相关结果。")
    else:
        # Simplistic display
        text = "\n".join([r['properties']['Name']['title'][0]['plain_text'] for r in results['results'][:5]])
        await message_to_reply.reply_text(f"找到以下游戏:\n{text}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot ready! @我并输入游戏名称，或者发送 /query <游戏名称>")

async def query_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    query = " ".join(context.args)
    await perform_notion_query(query, update.effective_chat.id, update.message)

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    
    # 获取消息文本，去掉 bot 的用户名部分
    text = update.message.text or update.message.caption or ""
    bot_username = context.bot.username
    
    # 清洗文本，去掉 @botname
    query = text.replace(f"@{bot_username}", "").strip()
    
    # 如果是回复消息，也可以把被回复的那条消息的文本作为查询词（可选）
    if not query and update.message.reply_to_message:
        query = update.message.reply_to_message.text or ""

    await perform_notion_query(query, update.effective_chat.id, update.message)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 获取 bot 用户名用于清洗文本
    # 注意：为了让 bot.username 有效，需要在启动时或者通过 get_me 获取
    # 这里我们假设启动正常，应用会异步加载，但这儿简单起见直接用 command 处理器
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('query', query_command))
    
    # 处理 @mention 和回复
    application.add_handler(MessageHandler(filters.Entity("mention") | filters.REPLY, handle_mention))
    
    application.run_polling()
