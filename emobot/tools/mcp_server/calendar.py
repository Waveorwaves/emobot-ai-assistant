#!/usr/bin/env python3
"""
Calendar Tool for Emobot
Supports calendar management and email-calendar integration
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .tool_base import MCPToolBase

class CalendarTool(MCPToolBase):
    """Calendar management tool with email integration"""
    
    def __init__(self):
        super().__init__()
        self.name = "calendar"
        self.description = "Manage calendar events and integrate with email"
        self.calendar_file = "agent_memory/calendar_events.json"
        self._load_calendar()
    
    def _load_calendar(self):
        """Load calendar events from file"""
        try:
            import os
            if os.path.exists(self.calendar_file):
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
            else:
                self.events = []
        except Exception as e:
            print(f"Error loading calendar: {e}")
            self.events = []
    
    def _save_calendar(self):
        """Save calendar events to file"""
        try:
            import os
            os.makedirs(os.path.dirname(self.calendar_file), exist_ok=True)
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving calendar: {e}")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["create_event", "list_events", "delete_event", "parse_email_for_event", "send_invitation"],
                        "description": "Calendar operation to perform"
                    },
                    "title": {
                        "type": "string",
                        "description": "Event title"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Event start time (ISO format or natural language)"
                    },
                    "end_time": {
                        "type": "string", 
                        "description": "Event end time (ISO format or natural language)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses"
                    },
                    "email_content": {
                        "type": "string",
                        "description": "Email content to parse for event information"
                    }
                },
                "required": ["operation"]
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute calendar operation"""
        operation = kwargs.get("operation")
        
        try:
            if operation == "create_event":
                return self._create_event(kwargs)
            elif operation == "list_events":
                return self._list_events(kwargs)
            elif operation == "delete_event":
                return self._delete_event(kwargs)
            elif operation == "parse_email_for_event":
                return self._parse_email_for_event(kwargs)
            elif operation == "send_invitation":
                return self._send_invitation(kwargs)
            else:
                return {"status": "error", "error_message": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"status": "error", "error_message": str(e)}
    
    def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        title = params.get("title", "Untitled Event")
        start_time = params.get("start_time")
        end_time = params.get("end_time")
        location = params.get("location", "")
        description = params.get("description", "")
        attendees = params.get("attendees", [])
        
        # Parse time strings
        start_dt = self._parse_time(start_time)
        if not start_dt:
            return {"status": "error", "error_message": "Invalid start time format"}
        
        end_dt = self._parse_time(end_time) if end_time else start_dt + timedelta(hours=1)
        
        event = {
            "id": f"event_{len(self.events) + 1}",
            "title": title,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "location": location,
            "description": description,
            "attendees": attendees,
            "created_at": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        self.events.append(event)
        self._save_calendar()
        
        return {
            "status": "success",
            "result": f"Event '{title}' created successfully",
            "event": event
        }
    
    def _list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List calendar events"""
        # Filter by date range if specified
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        
        if start_date and end_date:
            start_dt = self._parse_time(start_date)
            end_dt = self._parse_time(end_date)
            filtered_events = [
                event for event in self.events
                if start_dt <= self._parse_time(event["start_time"]) <= end_dt
            ]
        else:
            filtered_events = self.events
        
        return {
            "status": "success",
            "result": f"Found {len(filtered_events)} events",
            "events": filtered_events
        }
    
    def _delete_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a calendar event"""
        event_id = params.get("event_id")
        if not event_id:
            return {"status": "error", "error_message": "Event ID required"}
        
        for i, event in enumerate(self.events):
            if event["id"] == event_id:
                deleted_event = self.events.pop(i)
                self._save_calendar()
                return {
                    "status": "success",
                    "result": f"Event '{deleted_event['title']}' deleted successfully"
                }
        
        return {"status": "error", "error_message": "Event not found"}
    
    def _parse_email_for_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse email content to extract event information"""
        email_content = params.get("email_content", "")
        if not email_content:
            return {"status": "error", "error_message": "Email content required"}
        
        # Extract event information using regex patterns
        event_info = self._extract_event_from_text(email_content)
        
        if event_info:
            return {
                "status": "success",
                "result": "Event information extracted from email",
                "event_info": event_info
            }
        else:
            return {
                "status": "success",
                "result": "No clear event information found in email",
                "event_info": None
            }
    
    def _send_invitation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send calendar invitation email"""
        event_id = params.get("event_id")
        if not event_id:
            return {"status": "error", "error_message": "Event ID required"}
        
        # Find the event
        event = None
        for e in self.events:
            if e["id"] == event_id:
                event = e
                break
        
        if not event:
            return {"status": "error", "error_message": "Event not found"}
        
        # Generate invitation email content
        invitation_content = self._generate_invitation_email(event)
        
        return {
            "status": "success",
            "result": "Invitation email content generated",
            "invitation": invitation_content,
            "event": event
        }
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time string to datetime object"""
        if not time_str:
            return None
        
        # Try ISO format first
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try natural language parsing
        now = datetime.now()
        base_date = now.date()
        
        # Handle day references
        time_str_lower = time_str.lower()
        if "today" in time_str_lower:
            base_date = now.date()
        elif "tomorrow" in time_str_lower:
            base_date = (now + timedelta(days=1)).date()
        elif "sunday" in time_str_lower:
            # Find next Sunday
            days_ahead = 6 - now.weekday()  # Sunday is 6
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        elif "monday" in time_str_lower:
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        elif "tuesday" in time_str_lower:
            days_ahead = 1 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        elif "wednesday" in time_str_lower:
            days_ahead = 2 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        elif "thursday" in time_str_lower:
            days_ahead = 3 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        elif "friday" in time_str_lower:
            days_ahead = 4 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        elif "saturday" in time_str_lower:
            days_ahead = 5 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        
        # Extract time with improved patterns
        time_patterns = [
            r"(\d{1,2}):(\d{2})\s*(am|pm)",  # 6:00 pm
            r"(\d{1,2})\s*(am|pm)",          # 6 pm
            r"(\d{1,2}):(\d{2})",            # 18:00
            r"(\d{1,2})\s*pm",               # 6pm
            r"(\d{1,2})\s*am"                # 6am
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, time_str_lower)
            if match:
                try:
                    if len(match.groups()) >= 3 and match.group(3):  # HH:MM AM/PM
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                        ampm = match.group(3)
                        if ampm == "pm" and hour != 12:
                            hour += 12
                        elif ampm == "am" and hour == 12:
                            hour = 0
                    elif len(match.groups()) >= 2 and match.group(2) and match.group(2) in ['am', 'pm']:  # HH AM/PM
                        hour = int(match.group(1))
                        minute = 0
                        ampm = match.group(2)
                        if ampm == "pm" and hour != 12:
                            hour += 12
                        elif ampm == "am" and hour == 12:
                            hour = 0
                    elif len(match.groups()) >= 2 and match.group(2).isdigit():  # HH:MM
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                    else:  # Just hour
                        hour = int(match.group(1))
                        minute = 0
                        # Assume PM for hours 1-11, AM for 12
                        if "pm" in time_str_lower and hour != 12:
                            hour += 12
                        elif "am" in time_str_lower and hour == 12:
                            hour = 0
                    
                    # Validate hour and minute
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        return datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute))
                except (ValueError, IndexError):
                    continue
        
        # If no time found, default to current time
        return datetime.combine(base_date, now.time())
    
    def _extract_event_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract event information from text"""
        # Common event patterns
        patterns = {
            "meeting": r"(?:meeting|call|appointment|interview)\s+(?:with|at|on)?\s*([^,\n]+)",
            "time": r"(?:at|on|from)\s+([^,\n]+?)(?:\s+to\s+([^,\n]+))?",
            "location": r"(?:at|in|location:?)\s+([^,\n]+)",
            "date": r"(?:on|date:?)\s+([^,\n]+)",
            "duration": r"(?:for|duration:?)\s+([^,\n]+)"
        }
        
        event_info = {}
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "time" and len(match.groups()) > 1:
                    event_info["start_time"] = match.group(1).strip()
                    if match.group(2):
                        event_info["end_time"] = match.group(2).strip()
                else:
                    event_info[key] = match.group(1).strip()
        
        # Try to extract title from the beginning
        lines = text.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            if line.strip() and not line.strip().startswith(('Hi', 'Hello', 'Dear')):
                event_info["title"] = line.strip()
                break
        
        return event_info if event_info else None
    
    def _generate_invitation_email(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Generate invitation email content"""
        start_time = datetime.fromisoformat(event["start_time"])
        end_time = datetime.fromisoformat(event["end_time"])
        
        subject = f"Calendar Invitation: {event['title']}"
        
        body = f"""Hi there,

You are invited to: {event['title']}

When: {start_time.strftime('%A, %B %d, %Y at %I:%M %p')} - {end_time.strftime('%I:%M %p')}
Where: {event.get('location', 'TBD')}

Description: {event.get('description', 'No description provided')}

Please let me know if you can attend.

Best regards,
Emobot
"""
        
        return {
            "subject": subject,
            "body": body,
            "recipients": event.get("attendees", [])
        }
