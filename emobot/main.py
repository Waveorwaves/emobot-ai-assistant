"""
Main entry point for the emobot personal assistant.
"""
import os
import logging
import argparse
from pathlib import Path

# Try to import dotenv for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using environment variables directly.")

# Import core modules
from emobot.core.config import logger, TELEGRAM_TOKEN, setup_logging
from emobot.integrations.telegram_bot import TelegramBot

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Emobot Personal Assistant')
    parser.add_argument('--telegram', action='store_true', help='Start the Telegram bot')
    parser.add_argument('--token', type=str, help='Telegram bot token (overrides environment variable)')
    parser.add_argument('--loglevel', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='Logging level')
    
    return parser.parse_args()

def run_telegram_bot(token=None):
    """Run the Telegram bot."""
    try:
        # Use provided token or get from environment
        bot_token = token or TELEGRAM_TOKEN
        
        if not bot_token:
            raise ValueError("Telegram bot token not provided. Set TELEGRAM_BOT_TOKEN environment variable or use --token")
        
        # Initialize and run the bot
        bot = TelegramBot(bot_token)
        logger.info("Starting Telegram bot...")
        bot.run()
        
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Setup logging with appropriate level
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    logger.info("Starting Emobot Personal Assistant...")
    
    if args.telegram:
        # Run in Telegram mode
        success = run_telegram_bot(args.token)
        if not success:
            logger.error("Telegram bot failed to start")
            return 1
    else:
        # Default to Telegram for now
        logger.info("No interface specified, defaulting to Telegram")
        success = run_telegram_bot(args.token)
        if not success:
            logger.error("Telegram bot failed to start")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())