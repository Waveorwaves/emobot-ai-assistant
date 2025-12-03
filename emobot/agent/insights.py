import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class InsightsManager:
    """
    Manages proactive insights generation and handling
    """
    def __init__(self, agent=None):
        self.agent = agent
        self.demo_mode = False

    def set_demo_mode(self, enabled: bool):
        self.demo_mode = enabled

    def analyze_insights(self) -> List[Dict[str, Any]]:
        """
        Generate insights based on current state.
        In demo mode, returns scripted insights.
        """
        if self.demo_mode:
            return self._get_demo_insights()
        
        # Real logic would go here (analyzing emails, calendar, todos)
        # For now, return empty or basic insights
        return []

    def _get_demo_insights(self) -> List[Dict[str, Any]]:
        """Return hardcoded insights for the demo scenario"""
        return [
            {
                "id": "insight_1",
                "type": "urgent",
                "title": "Microsoft interview confirmation",
                "description": "I found an unread email from Microsoft AI confirming an interview on Friday at 10:00 AM, but your calendar has no prep time.",
                "suggestion": "Scheduled friday 10am for interview and reply to email.",
                "priority": "high",
                "content": "Email from Microsoft AI HR: Interview confirmed for Friday 10:00 AM.",
                "sender_email": "hr@microsoft.com" # Mock
            },
            {
                "id": "insight_2",
                "type": "warning",
                "title": "You have an upcoming interview but no prep time scheduled",
                "description": "You have an interview with Microsoft AI Asia on Friday at 10:00 AM, confirmed by HR. There is no dedicated prep time scheduled before the interview in your calendar.",
                "suggestion": "Block 1 hour tomorrow evening and 1 hour the day after for interview preparation",
                "priority": "high",
                "content": "You have an interview with Microsoft AI Asia on Friday at 10:00 AM, confirmed by HR. There is no dedicated prep time scheduled before the interview in your calendar.",
                "sender_email": "chenhao@uchicago.edu" # Mock
            },
            {
                "id": "insight_3",
                "type": "optimization",
                "title": "Emobot polishing tasks are fragmented",
                "description": "You have 3 scattered tasks related to Emobot polishing.",
                "suggestion": "Combine them into one 'Emobot polishing sprint' this weekend.",
                "priority": "medium",
                "content": "Tasks: Refine slides, Clean README, Record demo.",
                "sender_email": ""
            }
        ]

    def generate_reply(self, recipient: str, context: str, suggestion: str) -> Dict[str, str]:
        """
        Generate an email reply based on context and suggestion.
        In demo mode, returns scripted replies for specific recipients.
        """
        if self.demo_mode:
            # Check recipient to decide which scripted reply to return
            if "chenhao" in recipient.lower() or "tan" in recipient.lower():
                return {
                    "to": recipient,
                    "subject": "Brief update on Emobot draft",
                    "body": """Dear Professor Tan,

I wanted to let you know that I'm currently working on the updated draft of my Emobot project. I have scheduled focused time later this week to finalize it and plan to send you the new version by Thursday evening.

Thank you for your patience, and I appreciate your guidance on this project.

Best regards,
Yifei"""
                }
            elif "microsoft" in recipient.lower():
                 return {
                    "to": recipient,
                    "subject": "Re: Interview Confirmation",
                    "body": """Dear Hiring Manager,

Thank you for confirming the interview time. I look forward to speaking with you on Friday at 10:00 AM.

Best regards,
Yifei"""
                }

        # If not demo mode or no match, use the agent to generate (if available)
        if self.agent:
            prompt = f"""
            Draft a reply email to {recipient}.
            Context: {context}
            Suggestion: {suggestion}
            
            Return ONLY the JSON with 'subject' and 'body'.
            """
            try:
                # This is a simplification, actual implementation would use the agent's run method
                # and parse the result. For now, return a generic placeholder if agent is not fully hooked up here.
                return {
                    "to": recipient,
                    "subject": "Reply",
                    "body": "This is a generated draft based on the insight."
                }
            except Exception as e:
                print(f"Error generating reply: {e}")
        
        return {
            "to": recipient,
            "subject": "Reply",
            "body": "Could not generate reply."
        }
