import asyncio
import logging
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
        "🤖 **Multi-Agent Orchestrator Bot**\n\n"
        "I can help you with:\n"
        "• 🔍 Product search: 'Find wireless headphones on Amazon'\n"
        "• 🎨 Media generation: 'Generate an image of a sunset'\n"
        "• ⏰ Reminders: 'Remind me to call mom at 6pm'\n"
        "• 💾 Memory: 'Remember my favorite color is blue'\n\n"
        "I use rigorous validation to ensure accuracy!",
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
        if not result.get("needs_clarification"):
            await update.message.reply_text(
                f"❌ Sorry, I couldn't complete your request.\n"
                f"Error: {result.get('message', 'Unknown error')}"
            )

async def format_and_send_output(update: Update, output: dict, result: dict):
    """Format output based on type"""
    
    if "results" in output:
        results = output.get("results", [])
        message = "🔍 **Search Results:**\n\n"
        for i, item in enumerate(results[:5], 1):
            name = item.get("name", "Unknown")
            link = item.get("link", "")
            price = item.get("price", "N/A")
            message += f"{i}. **{name}**\n   💰 {price}\n   🔗 {link}\n\n"
        await update.message.reply_text(message, parse_mode="Markdown")
    
    elif "url" in output:
        file_url = output.get("url")
        media_type = output.get("media_type", "image")
        
        if media_type == "image":
            await update.message.reply_photo(photo=file_url)
        elif media_type == "video":
            await update.message.reply_video(video=file_url)
        elif media_type in ["audio", "voice"]:
            await update.message.reply_audio(audio=file_url)
    
    elif "schedule_id" in output:
        schedule_id = output.get("schedule_id")
        await update.message.reply_text(
            f"✅ **Reminder Set!**\n"
            f"🆔 Schedule ID: {schedule_id}",
            parse_mode="Markdown"
        )
    
    elif "note_id" in output:
        await update.message.reply_text(
            "✅ **Saved to memory!**\n"
            "I'll remember this information.",
            parse_mode="Markdown"
        )
    
    else:
        await update.message.reply_text(str(output))

def main():
    """Start the bot"""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()