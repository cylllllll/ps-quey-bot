# Notion PS+ Game Query Bot

A simple Telegram bot that queries your personal Notion PS+ game database.

## Features
- **Query Games**: Find PS+ game details directly from your Notion database.
- **Dockerized**: Easy to deploy on any VPS using Docker.
- **Environment Driven**: No sensitive keys in code.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd bot-notion
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot API token.
   - `NOTION_API_KEY`: Your Notion integration API key.
   - `NOTION_DATABASE_ID`: The IDs of your Notion databases.

## Deploy with Docker

1. **Build:**
   ```bash
   docker build -t notion-bot .
   ```

2. **Run:**
   ```bash
   docker run -d \
     --name notion-bot \
     -e TELEGRAM_BOT_TOKEN="your_token" \
     -e NOTION_API_KEY="your_notion_key" \
     -e NOTION_DATABASE_ID="your_db_id" \
     --restart unless-stopped \
     notion-bot
   ```

## Usage
In Telegram:
- `/start` to verify the bot is online.
- `/query <game_name>` to search your Notion database.
