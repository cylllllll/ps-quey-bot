[English](README.en.md) | [简体中文](README.md) | [繁體中文](README.zh-TW.md)

# Notion PS+ Game Query Bot (简体中文)

一个轻量级的 Telegram 机器人，用于查询你个人的 Notion 数据库中的 PlayStation Plus 游戏领取记录。

## 功能特点
- **数据库查询**: 直接从 Notion 获取游戏的领取日期和状态。
- **隐私优先**: 设计为在本地或私有 VPS 上运行，通过环境变量管理敏感信息。
- **访问控制**: 通过配置设置白名单，支持群组和个人用户区分管理。

## 前置准备
1. **Telegram Bot Token**: 通过 [BotFather](https://t.me/botfather) 创建机器人并获取 Token。
2. **Notion 集成**:
   - 在 [Notion Developers](https://www.notion.so/my-integrations) 创建 Integration。
   - 将你的 Notion 数据库与该 Integration 共享。
   - 获取 **Integration Internal Token** 和 **Database ID**。

## 快速安装
1. **克隆代码**:
   ```bash
   git clone <your-repo-url>
   cd bot-notion
   ```
2. **环境变量配置**: 复制 `config.example` 到 `.env`，填入你的 Token 和 ID。

## Docker 部署
1. **构建镜像**: `docker build -t notion-bot .`
2. **运行容器**: `docker run -d --name notion-bot --env-file .env --restart unless-stopped notion-bot`

## 指令
- `/start`: 检查机器人状态。
- `/query <游戏名称>`: 搜索数据库中的游戏。
- `/help`: 查看帮助。
