[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md)

# Notion PS+ Game Query Bot

A lightweight Telegram bot built to search your personal Notion database for PlayStation Plus game release history.

## Features
- **Searchable Database**: Retrieve game entry dates and status directly from Notion.
- **Privacy First**: Designed to run on your own infrastructure with secure environment variable management.
- **Access Control**: Whitelist specific groups and individual users via configuration.

## Prerequisites
1. **Telegram Bot Token**: Get one by messaging [@BotFather](https://t.me/botfather).
2. **Notion Integration**:
   - Create an integration at [Notion Developers](https://www.notion.so/my-integrations).
   - Share your database with the integration.
   - Copy your **Integration Internal Token** and **Database ID**.

## Setup
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd bot-notion
   ```
2. **Environment Configuration:**
   Copy `config.example` to `.env` and add your credentials.

## Deploy with Docker
1. **Build the image:** `docker build -t notion-bot .`
2. **Run:** `docker run -d --name notion-bot --env-file .env --restart unless-stopped notion-bot`
