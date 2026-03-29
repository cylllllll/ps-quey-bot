import os
import logging
from math import ceil
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from notion_client import Client, APIResponseError

# Load environment variables
load_dotenv()

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
        return chat_id in ALLOWED_USER_IDS
    return chat_id in ALLOWED_GROUP_IDS

def get_page_title(page):
    props = page.get("properties", {})
    for key, value in props.items():
        if value.get("type") == "title":
            title_arr = value.get("title", [])
            if title_arr:
                return title_arr[0].get("plain_text", "未知标题")
    return "未命名游戏"

def format_game(r):
    props = r.get("properties", {})
    
    # 1. 游戏名称
    cn_name = get_page_title(r)
    en_prop = props.get("英文名称", {})
    en_name = ""
    if en_prop.get("type") == "rich_text" and en_prop.get("rich_text"):
        en_name = en_prop["rich_text"][0].get("plain_text", "")
    
    full_name = cn_name
    if en_name:
        full_name += f" / {en_name}"
        
    # 2. 入库日期 (兼容旧的 会免日期 或 Date)
    date_str = "未知"
    if "入库日期" in props and props["入库日期"].get("date"):
        date_str = props["入库日期"]["date"].get("start", "未知")
    elif "会免日期" in props and props["会免日期"].get("rich_text"):
        date_str = props["会免日期"]["rich_text"][0].get("plain_text", "未知")
    elif "Date" in props and props["Date"].get("date"):
        date_str = props["Date"]["date"].get("start", "未知")
        
    # 组装基础信息
    result_lines = [f"游戏名称: {full_name}", f"入库日期: {date_str}"]
        
    # 3. 档位及状态逻辑 (区分会免和订阅)
    tier_str = ""
    if "档位" in props and props["档位"].get("select"):
        tier_str = props["档位"]["select"].get("name", "")
        
    if not tier_str:
        # 没有填写档位信息的，默认归为会免，且不显示状态
        result_lines.append("档位: 会免")
    else:
        # 有填写档位信息（如 2档 / 3档）
        result_lines.append(f"档位: {tier_str}")
        
        # 订阅游戏需要显示出入库状态
        status_str = "未知"
        if "状态" in props and props["状态"].get("select"):
            status_str = props["状态"]["select"].get("name", "未知")
        result_lines.append(f"状态: {status_str}")
        
    return "\n".join(result_lines)

async def show_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    results = context.chat_data.get('results', [])
    page_size = 3
    max_page = max(0, ceil(len(results) / page_size) - 1)
    page = max(0, min(page, max_page))
    context.chat_data['current_page'] = page

    start = page * page_size
    end = start + page_size
    page_items = results[start:end]

    text = ""
    formatted_games = [format_game(r) for r in page_items]
    text += "\n\n".join(formatted_games)
    
    # 在底部补充页码信息 (如果只有一页就不补充了)
    if max_page > 0:
        text += f"\n\n(第 {page + 1}/{max_page + 1} 页)"

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data="prev"))
    if page < max_page:
        buttons.append(InlineKeyboardButton("下一页 ➡️", callback_data="next"))
    
    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None

    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    elif hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text(text, reply_markup=reply_markup)
    else:
        # Fallback if passed a raw Message
        await update.reply_text(text, reply_markup=reply_markup)

async def perform_notion_query(query, chat_id, message_to_reply, context: ContextTypes.DEFAULT_TYPE):
    if not query:
        await message_to_reply.reply_text("请输入要查询的游戏名称。")
        return

    try:
        # 使用全局 Search API 拉取候选名单
        raw_results = notion.search(
            query=query,
            filter={
                "property": "object",
                "value": "page"
            }
        ).get("results", [])

        # 在本地进行严格清洗过滤
        filtered_results = []
        target_db = DATABASE_ID.replace("-", "")
        
        for r in raw_results:
            # 1. 确保该页面属于我们的目标数据库
            parent_db = r.get("parent", {}).get("database_id", "").replace("-", "")
            if parent_db != target_db:
                continue
            
            # 2. 确保游戏标题中确实包含搜索关键字（忽略大小写）
            title = get_page_title(r)
            if query.lower() in title.lower():
                filtered_results.append(r)
                
        results = {"results": filtered_results}

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
    if not update.message: return
    raw_text = update.message.text or update.message.caption or ""
    if not raw_text: return
    
    bot_username = context.bot.username
    is_mentioned = False
    text = raw_text
    
    if update.effective_chat.type == 'private':
        is_mentioned = True
    elif bot_username and f"@{bot_username}" in raw_text:
        is_mentioned = True
        text = raw_text.replace(f"@{bot_username}", "").strip()
    elif update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
        is_mentioned = True
        text = raw_text.strip()
        
    if not is_mentioned:
        return

    if not is_allowed(update): return
    
    if not text and update.message.reply_to_message: 
        text = update.message.reply_to_message.text or ""
        
    if not text: return
    
    logging.info(f"Parsed query: {text}")
    await perform_notion_query(text, update.effective_chat.id, update.message, context)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    async def command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_allowed(update): return
        query = " ".join(context.args)
        await perform_notion_query(query, update.effective_chat.id, update.message, context)

    application.add_handler(CommandHandler('query', command_wrapper))
    application.add_handler(MessageHandler(filters.TEXT, handle_mention))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling()
