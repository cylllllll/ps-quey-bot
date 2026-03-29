# Notion PS+ Game Query Bot

A lightweight Telegram bot built to search your personal Notion database for PlayStation Plus game release history.

## Features
- **Searchable Database**: Retrieve game entry dates and status directly from Notion.
- **Privacy First**: Designed to run on your own infrastructure with secure environment variable management.
- **Easy Deployment**: Fully Dockerized for rapid setup on any VPS.

## Prerequisites

Before setting up, ensure you have:
1. **Telegram Bot Token**: Get one by messaging [@BotFather](https://t.me/botfather) on Telegram.
2. **Notion Integration**:
   - Create an integration at [Notion Developers](https://www.notion.so/my-integrations).
   - Share your database with the integration (click the "..." menu in your Notion database -> Add Connections -> Select your integration).
   - Copy your **Integration Internal Token** and **Database ID**.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd bot-notion
   ```

2. **Environment Configuration:**
   Copy the example config and fill in your keys:
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials:
   # TELEGRAM_BOT_TOKEN=...
   # NOTION_API_KEY=...
   # NOTION_DATABASE_ID=...
   ```

## Deploy with Docker

1. **Build the image:**
   ```bash
   docker build -t notion-bot .
   ```

2. **Run in background:**
   ```bash
   docker run -d \
     --name notion-bot \
     --env-file .env \
     --restart unless-stopped \
     notion-bot
   ```

## Usage
- `/start`: Check bot status.
- `/query <game_name>`: Search for a specific game in your PS+ list.
- `/help`: Show available commands.

## Troubleshooting
- **Database not found?** Ensure the Notion integration has permission to access the page/database.
- **Bot unresponsive?** Check logs using `docker logs notion-bot`.
