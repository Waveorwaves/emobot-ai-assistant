"""
Telegram integration for the emobot assistant.
"""
import os
import logging
import tempfile
from typing import Dict, Any

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from emobot.core.config import TELEGRAM_TOKEN, logger
from emobot.core.assistant_agent import AssistantAgent
from emobot.services.speech_service import SpeechService

class TelegramBot:
    """Telegram bot interface for the emobot assistant."""
    
    def __init__(self, token: str = None):
        """Initialize the Telegram bot."""
        self.token = token or TELEGRAM_TOKEN
        if not self.token:
            raise ValueError("Telegram bot token not provided")
        
        self.assistants: Dict[str, AssistantAgent] = {}  # user_id -> AssistantAgent
        self.speech_service = SpeechService()
        
        # Check if ffmpeg is installed (required for voice messages)
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("ffmpeg not found. Voice messages may not work properly.")
            logger.warning("Please install ffmpeg: https://ffmpeg.org/download.html")
    
    def _get_assistant(self, user_id: str) -> AssistantAgent:
        """Get or create an assistant agent for a user."""
        if user_id not in self.assistants:
            self.assistants[user_id] = AssistantAgent(user_id)
        return self.assistants[user_id]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user_id = str(update.effective_user.id)
        assistant = self._get_assistant(user_id)
        
        # Build message data with user info
        message_data = {
            "user": update.effective_user.to_dict(),
            "chat": update.effective_chat.to_dict() if update.effective_chat else {},
        }
        
        response = await assistant.process_message("/start", message_data)
        await update.message.reply_text(response)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        user_id = str(update.effective_user.id)
        assistant = self._get_assistant(user_id)
        
        response = await assistant.process_message("/help", {})
        await update.message.reply_text(response)
    
    async def time_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /time command."""
        user_id = str(update.effective_user.id)
        assistant = self._get_assistant(user_id)
        
        response = await assistant.process_message("/time", {})
        await update.message.reply_text(response)
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any command."""
        user_id = str(update.effective_user.id)
        assistant = self._get_assistant(user_id)
        
        message_text = update.message.text
        message_data = {
            "user": update.effective_user.to_dict(),
            "chat": update.effective_chat.to_dict() if update.effective_chat else {},
            "context": context.args
        }
        
        response = await assistant.process_message(message_text, message_data)
        await update.message.reply_text(response)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = str(update.effective_user.id)
        assistant = self._get_assistant(user_id)
        
        message_text = update.message.text
        message_data = {
            "user": update.effective_user.to_dict(),
            "chat": update.effective_chat.to_dict() if update.effective_chat else {},
        }
        
        response = await assistant.process_message(message_text, message_data)
        await update.message.reply_text(response)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages."""
        user_id = str(update.effective_user.id)
        assistant = self._get_assistant(user_id)
        
        # Let user know we're processing
        processing_message = await update.message.reply_text("🎤 Processing your voice message...")
        
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        # Download the voice message
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_ogg:
            await file.download_to_drive(temp_ogg.name)
            temp_ogg_path = temp_ogg.name
        
        temp_wav_path = None
        try:
            # Convert OGG to WAV for speech recognition
            temp_wav_path = self.speech_service.convert_ogg_to_wav(temp_ogg_path)
                        
            # Transcribe the audio
            try:
                text = self.speech_service.speech_to_text(temp_wav_path)
                if not text or not text.strip():
                    raise ValueError("Transcription returned empty text")
                    
                logger.info(f"Successfully transcribed voice to: {text}")
                
                # Edit the processing message to show what was heard
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=processing_message.message_id,
                    text=f"🎤 I heard: \"{text}\""
                )
                
                # Process the transcribed text
                message_data = {
                    "user": update.effective_user.to_dict(),
                    "chat": update.effective_chat.to_dict() if update.effective_chat else {},
                    "voice": True,
                    "transcribed_text": text,
                }
                
                # Check if the transcribed text is a command
                if text.strip().startswith('/'):
                    # Handle commands specially
                    command_parts = text.strip().split()
                    command = command_parts[0].lower()
                    
                    if command == "/start":
                        await self.start_command(update, context)
                    elif command == "/help":
                        await self.help_command(update, context)
                    elif command == "/time":
                        await self.time_command(update, context)
                    else:
                        # Other commands
                        response = await assistant.process_message(text, message_data)
                        await update.message.reply_text(response)
                else:
                    # Regular message
                    response = await assistant.process_message(text, message_data)
                    await update.message.reply_text(response)
                    
            except Exception as e:
                logger.error(f"Error during transcription: {e}")
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=processing_message.message_id,
                    text="❌ Sorry, I couldn't understand what you said."
                )
                await update.message.reply_text(
                    "Please try speaking more clearly or recording in a quieter environment."
                )
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            logger.error(f"Error details: {type(e).__name__}")
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Traceback: {tb}")
            # Log the file paths to help debugging
            logger.error(f"Voice file path: {temp_ogg_path}")
            if 'temp_wav_path' in locals():
                logger.error(f"WAV file path: {temp_wav_path}")
            
            # Update the processing message
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=processing_message.message_id,
                    text="❌ Voice processing failed."
                )
            except:
                # In case the message cannot be edited
                pass
                
            await update.message.reply_text("Sorry, I had trouble processing your voice message. Please try again or type your request.")
        
        finally:
            # Clean up temporary files
            if os.path.exists(temp_ogg_path):
                os.unlink(temp_ogg_path)
            if temp_wav_path and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)

    # Add this new method to handle command text from voice
    async def handle_command_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, command_text: str):
        """Handle command text extracted from voice."""
        user_id = str(update.effective_user.id)
        assistant = self._get_assistant(user_id)
        
        # Extract command and arguments
        parts = command_text.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle specific commands
        if command == "/start":
            await self.start_command(update, context)
        elif command == "/help":
            await self.help_command(update, context)
        elif command == "/time":
            await self.time_command(update, context)
        else:
            # For other commands
            message_data = {
                "user": update.effective_user.to_dict(),
                "chat": update.effective_chat.to_dict() if update.effective_chat else {},
                "context": args
            }
            
            response = await assistant.process_message(command_text, message_data)
            await update.message.reply_text(response)
    
    def run(self):
        """Start the bot."""
        # Create the Application
        application = Application.builder().token(self.token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("time", self.time_command))
        
        # Add general command handler (for all other commands)
        command_filter = filters.COMMAND & ~filters.Command(["start", "help", "time"])
        application.add_handler(MessageHandler(command_filter, self.handle_command))
        
        # Add message handler for regular messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add voice message handler
        application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        
        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)