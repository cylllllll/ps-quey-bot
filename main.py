import os
import logging
from math import ceil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from notion_client import Client, APIResponseError

# Load API keys
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
ALLOWED_GROUP_IDS = os.getenv("ALLOWED_GROUP_IDS", "").split(",")
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "").split(",")

notion = Client(auth=NOTION_TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def is_allowed(update: Update):
    chat_id = str(update.effective_chat.id)
    if update.effective_chat.type == 'private':
        return not ALLOWED_USER_IDS or ALLOWED_USER_IDS == [""] or chat_id in ALLOWED_USER_IDS
    return not ALLOWED_GROUP_IDS or ALLOWED_GROUP_IDS == [""] or chat_id in ALLOWED_GROUP_IDS

async def show_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    results = context.chat_data.get('results', [])
    page_size = 5
    max_page = max(0, ceil(len(results) / page_size) - 1)
    page = max(0, min(page, max_page))
    context.chat_data['current_page'] = page

    start = page * page_size
    end = start + page_size
    page_items = results[start:end]

    text = f"找到以下游戏 (第 {page + 1}/{max_page + 1} 页):\n\n"
    text += "\n".join([f"• {r['properties']['Name']['title'][0]['plain_text']}" for r in page_items])

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data="prev"))
    if page < max_page:
        buttons.append(InlineKeyboardButton("下一页 ➡️", callback_data="next"))
    
    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.effective_message.reply_text(text, reply_markup=reply_markup)

async def perform_notion_query(query, chat_id, message_to_reply, context: ContextTypes.DEFAULT_TYPE):
    if not query:
        await message_to_reply.reply_text("请输入要查询的游戏名称。")
        return

    try:
        results = notion.databases.query(**{
            "database_id": DATABASE_ID,
            "filter": {"property": "Name", "title": {"contains": query}}
        })
    except APIResponseError as e:
        logging.error(f"Notion API Error: {e}")
        await message_to_reply.reply_text("查询出错，请检查 Notion 权限或 API Key 配置。")
        return
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        await message_to_reply.reply_text("系统发生未知错误。")
        return
    
    if not results["results"]:
        await message_to_reply.reply_text("未找到相关结果。")
    else:
        context.chat_data['results'] = results["results"]
        await show_page(update=message_to_reply, context=context, page=0)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current_page = context.chat_data.get('current_page', 0)
    if query.data == "next":
        await show_page(update, context, current_page + 1)
    elif query.data == "prev":
        await show_page(update, context, current_page - 1)

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update): return
    text = (update.message.text or update.message.caption or "").replace(f"@{context.bot.username}", "").strip()
    if not text and update.message.reply_to_message: text = update.message.reply_to_message.text or ""
    await perform_notion_query(text, update.effective_chat.id, update.message, context)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 辅助: 包装一下 perform_notion_query 以适配 CommandHandler
    async def command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_allowed(update): return
        await perform_notion_query(" ".join(context.args), update.effective_chat.id, update.message, context)

    application.add_handler(CommandHandler('query', command_wrapper))
    application.add_handler(MessageHandler(filters.Entity("mention") | filters.REPLY, handle_mention))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling()
