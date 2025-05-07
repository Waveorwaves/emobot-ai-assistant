# emobot/agents/email_agent.py
import re
from typing import Dict, Any
from emobot.services.email_service import EmailService
from emobot.core.config import logger

class EmailAgent:
    """Agent for handling email-related tasks."""

    def __init__(self):
        """Initialize the EmailAgent."""
        self.email_service = EmailService()
        if not self.email_service.configured:
            logger.warning("EmailService not configured. EmailAgent may not function correctly.")

    async def process(self, message_text: str, message_data: Dict[str, Any]) -> str:
        """
        Process an email-related request.
        Args:
            message_text: The user's message.
            message_data: Additional data associated with the message.
        Returns:
            A string response to the user.
        """
        if not self.email_service.configured:
            return "Sorry, the mail service is not currently configured and I cannot process your mail request."

        message_lower = message_text.lower()

        # Try to parse send email command
        # Modified regex to be more flexible with "send me an email to" and "content" keyword
        send_match = re.search(r"send (?:me an )?email to (.*?) subject (.*?) (?:body|content) (.*)", message_lower, re.IGNORECASE)
        if send_match:
            to_address = send_match.group(1).strip()
            subject = send_match.group(2).strip()
            body = send_match.group(3).strip()
            
            # For simplicity, we'll use the body as HTML. You might want to create a plain text version too.
            success = await self.email_service.send_email(to_address, subject, body_html=body)
            if success:
                return f"Email successfully sent to {to_address}."
            else:
                return "Sorry, there was a problem sending your message."

        # Try to parse read unread emails command
        # Explicitly check for "check my unread emails" first for robustness
        if "check my unread emails" in message_lower or \
           "read unread emails" in message_lower or \
           "check my emails" in message_lower or \
           "check email" in message_lower:
            unread_emails = await self.email_service.read_unread_emails(max_results=3) # Limit to 3 for brevity
            if not unread_emails:
                return "You have no unread messages."
            
            response_parts = ["Here are your most recent unread messages:"]
            for email in unread_emails:
                response_parts.append(f"\n- Sender: {email['from']}\n  Subject: {email['subject']}\n  Abstract: {email['snippet'][:100]}...") # Show first 100 chars of snippet
            return "\n".join(response_parts)

        return "Sorry, I don't quite understand your email request. You can try saying:\n" \
               "- \"Send me an email to [email address] Subject [subject content] Content [email body]\"\n" \
               "- \"Check my unread emails\"\n" \
               "- \"Read my emails\""