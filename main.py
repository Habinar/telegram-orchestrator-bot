import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from orchestrator import Orchestrator
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

orchestrator = Orchestrator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 **Multi-Agent Orchestrator Bot** (OpenAI-Powered)\n\n"
        "I can help you with:\n"
        "• 🔍 Product search: 'Find wireless headphones on Amazon'\n"
        "• 🎨 Image generation: 'Generate an image of a sunset'\n"
        "• ⏰ Reminders: 'Remind me to call mom at 6pm'\n"
        "• 💾 Memory: 'Remember my favorite color is blue'\n"
        "• 💬 General questions: Ask me anything!\n\n"
        "Powered by GPT-4 with rigorous validation!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    async def notify(text: str):
        await update.message.reply_text(text, parse_mode="Markdown")
    
    result = await orchestrator.process(user_message, user_id, notify)
    
    if result["success"]:
        output = result["output"]
        await format_and_send_output(update, output, result)
    else:
        await update.message.reply_text(
            f"❌ Sorry, I couldn't complete your request.\n"
            f"Error: {result.get('message', 'Unknown error')}"
        )

async def format_and_send_output(update: Update, output: dict, result: dict):
    """Format output based on type"""
    
    # Product search results
    if "results" in output:
        results = output.get("results", [])
        message = "🔍 **Search Results:**\n\n"
        for i, item in enumerate(results[:5], 1):
            name = item.get("name", "Unknown")
            link = item.get("link", "")
            price = item.get("price", "N/A")
            desc = item.get("description", "")
            message += f"{i}. **{name}**\n"
            if price != "N/A":
                message += f"   💰 {price}\n"
            if desc:
                message += f"   📝 {desc}\n"
            if link:
                message += f"   🔗 {link}\n"
            message += "\n"
        await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=True)
    
    # Image generation
    elif "url" in output and output.get("media_type") == "image":
        file_url = output.get("url")
        caption = output.get("revised_prompt", "Generated image")
        await update.message.reply_photo(photo=file_url, caption=caption)
    
    # Reminder creation
    elif "cron_expression" in output:
        cron = output.get("cron_expression")
        next_exec = output.get("next_execution", "Soon")
        description = output.get("description", "Reminder set")
        await update.message.reply_text(
            f"✅ **Reminder Set!**\n\n"
            f"📋 {description}\n"
            f"📅 Next execution: {next_exec}\n"
            f"🔄 Cron: `{cron}`\n"
            f"⏰ Timezone: Europe/Kiev",
            parse_mode="Markdown"
        )
    
    # Memory storage
    elif "note_id" in output:
        content = output.get("content", "")
        await update.message.reply_text(
            f"✅ **Saved to memory!**\n\n"
            f"📝 {content}\n\n"
            f"I'll remember this information.",
            parse_mode="Markdown"
        )
    
    # General response
    elif "response" in output:
        response_text = output.get("response", "")
        await update.message.reply_text(response_text, parse_mode="Markdown")
    
    # Media generation guidance
    elif "message" in output:
        await update.message.reply_text(output.get("message"), parse_mode="Markdown")
    
    # Fallback
    else:
        await update.message.reply_text(str(output))

async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Health check endpoint"""
    await update.message.reply_text("✅ Bot is running!")

def main():
    """Start the bot"""
    if not config.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set! Please set it in environment variables.")
        return
    
    # Check if running on Railway (has PORT env var)
    port = os.getenv("PORT")
    webhook_url = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("RAILWAY_STATIC_URL")
    
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("health", health_check))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    if port and webhook_url:
        # Webhook mode for Railway
        logger.info(f"Starting bot in WEBHOOK mode on port {port}")
        logger.info(f"Webhook URL: https://{webhook_url}")
        
        application.run_webhook(
            listen="0.0.0.0",
            port=int(port),
            url_path=config.TELEGRAM_BOT_TOKEN,
            webhook_url=f"https://{webhook_url}/{config.TELEGRAM_BOT_TOKEN}"
        )
    else:
        # Polling mode for local development
        logger.info("Starting bot in POLLING mode (local development)")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()