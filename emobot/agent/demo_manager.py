import logging
import time
import json
from typing import Dict, Any, Optional, List
import re
import random

class DemoManager:
    """
    Demo Manager: Handles hardcoded demo scenarios
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_scene = 0
        self.scenarios = self._load_scenarios()

    def _load_scenarios(self) -> List[Dict[str, Any]]:
        """Load hardcoded scenarios"""
        return [
            # Scene 1: Email + Calendar + To-Do
            {
                "id": "scene_1",
                "triggers": [
                    "handle the meeting request from Professor Tan",
                    "meeting request from Professor Tan",
                    "help me handle the meeting request"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to handle a meeting request from Professor Tan. I need to find the latest email from him to understand the context and requested time.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: email",
                        "reasoning": "Calling email tool to search for unread emails from Chenhao Tan.",
                        "tool_name": "email",
                        "parameters": {"operation": "search_emails", "query": "from:Chenhao Tan is:unread"}
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from email",
                        "reasoning": "Found email: 'Meeting about your Emobot project'. Body: 'Could we meet for 30 minutes sometime next Tuesday or Wednesday afternoon...'",
                        "confidence": 1.0
                    },
                    {
                        "step": 4,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "The email requests a 30-minute meeting next Tuesday or Wednesday afternoon. I need to check the user's calendar for availability during these times.",
                        "confidence": 0.9
                    },
                    {
                        "step": 5,
                        "type": "tool_call",
                        "action": "Action: calendar",
                        "reasoning": "Calling calendar tool to list events for next Tuesday and Wednesday.",
                        "tool_name": "calendar",
                        "parameters": {"operation": "list_events", "time_min": "next Tuesday 1pm", "time_max": "next Wednesday 6pm"}
                    },
                    {
                        "step": 6,
                        "type": "observation",
                        "action": "Observation from calendar",
                        "reasoning": "Tuesday: 1:00-2:00 PM Data Science class, 3:30-4:30 PM Group meeting. Wednesday: 2:00-3:00 PM Career workshop.",
                        "confidence": 1.0
                    },
                    {
                        "step": 7,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "Based on the schedule, Tuesday 2:00-2:30 PM (after class) and Wednesday 3:00-3:30 PM (after workshop) or 4:00-4:30 PM are good slots. I will propose these.",
                        "confidence": 0.95
                    }
                ],
                "response": """Sure, I’ll coordinate your email and calendar for this.

Based on your schedule and typical working habits, here are my suggestions:

**Tuesday 2:00–2:30 PM**
Right after your class, in the same general time block, so you don’t lose context.

**Wednesday 3:00–3:30 PM**
Right after the career workshop, so you can immediately connect any ideas from the workshop to the Emobot project.

**Wednesday 4:00–4:30 PM**
A bit later in the afternoon when your calendar is open and you have time to prepare.

Would you like me to draft an English reply email to Professor Tan using these options?""",
                "actions": []
            },
            # Scene 2: Draft reply email
            {
                "id": "scene_2",
                "triggers": [
                    "draft a polite English reply",
                    "draft reply email",
                    "Tuesday 2:00–2:30 PM the first choice"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to draft a reply. First choice: Tuesday 2:00-2:30 PM, Second choice: Wednesday 3:00-3:30 PM. Tone: Polite English.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: email",
                        "reasoning": "Creating a draft email to Professor Tan.",
                        "tool_name": "email",
                        "parameters": {
                            "operation": "create_draft",
                            "recipient": "chenhao@uchicago.edu",
                            "subject": "Meeting about Emobot project"
                        }
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from email",
                        "reasoning": "Draft created successfully with ID: draft_123.",
                        "confidence": 1.0
                    }
                ],
                "response": """Got it. I’ll create a draft and keep it unsent.

✅ The reply has been saved as a draft:
**“Meeting about Emobot project – reply (draft)”**

**Subject:** Meeting about Emobot project
**Body:**
Dear Professor Tan,

Thank you for your email. I would be very happy to meet and discuss the progress of my Emobot project.

My preferred time would be Tuesday 2:00–2:30 PM, but Wednesday 3:00–3:30 PM would also work well for me if that is more convenient for you.

Please let me know which time you prefer, or if there is another time that works better.

Best regards,
Yifei

Would you like to review the draft now, or keep it as is for the moment?""",
                "actions": [
                    {
                        "tool": "email",
                        "parameters": {
                            "operation": "create_draft",
                            "recipient": "chenhao@uchicago.edu",
                            "subject": "Meeting about Emobot project",
                            "body": "Dear Professor Tan,\n\nThank you for your email. I would be very happy to meet and discuss the progress of my Emobot project.\n\nMy preferred time would be Tuesday 2:00–2:30 PM, but Wednesday 3:00–3:30 PM would also work well for me if that is more convenient for you.\n\nPlease let me know which time you prefer, or if there is another time that works better.\n\nBest regards,\nYifei"
                        }
                    }
                ],
                "ui_action": {
                    "type": "open_email_draft",
                    "data": {
                        "recipient": "chenhao@uchicago.edu",
                        "subject": "Meeting about Emobot project",
                        "body": "Dear Professor Tan,\n\nThank you for your email. I would be very happy to meet and discuss the progress of my Emobot project.\n\nMy preferred time would be Tuesday 2:00–2:30 PM, but Wednesday 3:00–3:30 PM would also work well for me if that is more convenient for you.\n\nPlease let me know which time you prefer, or if there is another time that works better.\n\nBest regards,\nYifei"
                    }
                }
            },
            # Scene 3: Create follow-up To-Do
            {
                "id": "scene_3",
                "triggers": [
                    "Don’t send it yet",
                    "add a to-do",
                    "remind me to follow up"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to create a follow-up task if no reply is received within two days.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: todo_list",
                        "reasoning": "Adding a new task to the to-do list.",
                        "tool_name": "todo_list",
                        "parameters": {
                            "operation": "add_task",
                            "title": "Follow up with Prof. Tan",
                            "due_date": "In 2 days",
                            "category": "study"
                        }
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from todo_list",
                        "reasoning": "Task created successfully.",
                        "confidence": 1.0
                    }
                ],
                "response": """Okay, I’ll make sure this doesn’t fall through the cracks.

✅ The follow-up task has been created:
**Title:** Follow up with Prof. Tan about Emobot meeting
**Due:** In 2 days at 9:00 AM
**Category:** Study
**Notes:** Check if there is a reply from Professor Tan. If not, send a brief follow-up email.

I’ll remind you in two days and automatically re-check your inbox at that time.""",
                "actions": [
                    {
                        "tool": "todo_list",
                        "parameters": {
                            "operation": "add_task",
                            "title": "Follow up with Prof. Tan about Emobot meeting",
                            "description": "Check if there is a reply from Professor Tan. If not, send a brief follow-up email.",
                            "due_date": "2025-12-04T09:00:00",
                            "category": "study"
                        }
                    }
                ]
            },
            # Scene 4: Show editable profile
            {
                "id": "scene_4",
                "triggers": [
                    "show my current profile",
                    "show memory page"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to see their current profile and memory settings.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: memory",
                        "reasoning": "Retrieving user profile from memory module.",
                        "tool_name": "memory",
                        "parameters": {"operation": "get_profile"}
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from memory",
                        "reasoning": "Profile retrieved: Name=Yifei Wang, Role=MS Data Science, ...",
                        "confidence": 1.0
                    }
                ],
                "response": """Sure, here’s a summary of your editable profile:

**Name:** Yifei Wang
**Role:** MS in Applied Data Science @ UChicago
**Preferred languages:** English, Chinese

**Communication style:**
*   With professors: formal, structured, and polite
*   With family: casual, warm, sometimes with emojis
*   With unfamiliar contacts: short, polite, and previously more neutral

**Interests:** LLMs, ReAct agents, Emobot project, causal inference

You can edit any of these fields directly. This is useful because purely learning from conversation can sometimes misrepresent your actual style, so your explicit profile has higher priority.""",
                "actions": []
            },
            # Scene 5: Update profile
            {
                "id": "scene_5",
                "triggers": [
                    "update my style with unfamiliar contacts",
                    "change my communication style to friendly but still concise"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to update their communication style for unfamiliar contacts.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: memory",
                        "reasoning": "Updating profile field 'communication_style.unfamiliar'.",
                        "tool_name": "memory",
                        "parameters": {
                            "operation": "update_profile",
                            "key": "communication_style.unfamiliar",
                            "value": "friendly but still concise and professional"
                        }
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from memory",
                        "reasoning": "Profile updated successfully.",
                        "confidence": 1.0
                    }
                ],
                "response": """Profile updated.

**With unfamiliar contacts:** friendly but still concise and professional

Going forward, when I write emails to new or less familiar people, I’ll follow this updated style.""",
                "actions": [
                    {
                        "tool": "memory",
                        "parameters": {
                            "operation": "update_profile",
                            "key": "communication_style.unfamiliar",
                            "value": "friendly but still concise and professional"
                        }
                    }
                ]
            },
            # Scene 6-1: Email to professor
            {
                "id": "scene_6_1",
                "triggers": [
                    "write an English email to Professor Tan",
                    "updating him on the Emobot progress"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to write an email to Professor Tan about Emobot progress. I need to check the memory for historical email tone.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: memory",
                        "reasoning": "Searching for past emails to 'Professor Tan' to analyze tone.",
                        "tool_name": "memory",
                        "parameters": {"operation": "search_history", "query": "email to Professor Tan"}
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from memory",
                        "reasoning": "Found pattern: Formal, structured, polite. Uses 'Dear Professor Tan', 'Best regards'.",
                        "confidence": 1.0
                    },
                    {
                        "step": 4,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "I will draft the email using this formal tone.",
                        "confidence": 0.95
                    }
                ],
                "response": """I’ll first look at how you usually write to Professor Tan.

Based on your history, here is a draft that matches your usual tone:

**Subject:** Update on Emobot project progress

**Body:**
Dear Professor Tan,

I hope this message finds you well. I wanted to briefly update you on the progress of my Emobot project.

Recently, I have implemented multi-tool orchestration that connects email, calendar, and to-do lists, as well as a memory module that maintains editable user profiles and interaction history. These components now work together to support more proactive and personalized assistance.

I would be very happy to share more details and receive your feedback at our next meeting.

Best regards,
Yifei

This structure, tone, and closing are consistent with your earlier emails to him.""",
                "actions": []
            },
            # Scene 6-2: Email to Mom
            {
                "id": "scene_6_2",
                "triggers": [
                    "write an email to my mom",
                    "content should be similar"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to write a similar update email to Mom. I need to check the memory for her specific tone.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: memory",
                        "reasoning": "Searching for past emails to 'Mom'.",
                        "tool_name": "memory",
                        "parameters": {"operation": "search_history", "query": "email to Mom"}
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from memory",
                        "reasoning": "Found pattern: Casual, warm, personal. Uses emojis, reassurances.",
                        "confidence": 1.0
                    }
                ],
                "response": """Let me first check your previous emails to your mom.

Based on that, here is an English draft with a similar feeling:

**Subject:** Small update about my Emobot project 😊

**Body:**
Hi Mom,

Just wanted to share a small update with you about the Emobot project I’ve been working on. Things are getting more exciting recently.

I’ve connected Emobot with my email, calendar, and to-do list, and I also added a “memory” module so it can remember my habits and help me stay organized. It can now remind me when I need to reply to someone or prepare for something important, which actually makes my days a bit less stressful.

School is still busy, but I’m doing fine, eating and sleeping okay, so please don’t worry. I’ll tell you more about it when we video call this weekend.

Love you,
Yifei

This keeps the message friendly and reassuring, similar to how you usually write to her.""",
                "actions": []
            },
            # Scene 6-3: Email to Alex Li
            {
                "id": "scene_6_3",
                "triggers": [
                    "write an email to Alex Li",
                    "email to Alex Li",
                    "email Alex Li"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants to write to Alex Li (new contact). I will use the profile setting for 'unfamiliar contacts'.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: memory",
                        "reasoning": "Checking profile for 'unfamiliar contacts' style.",
                        "tool_name": "memory",
                        "parameters": {"operation": "get_profile", "key": "communication_style"}
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from memory",
                        "reasoning": "Style: friendly but still concise and professional.",
                        "confidence": 1.0
                    }
                ],
                "response": """I’ll follow your updated profile style for unfamiliar contacts: **friendly, but concise and professional.**

**Subject:** Quick update on Emobot and potential collaboration

**Body:**
Hi Alex,

Hope you’re doing well! I wanted to share a quick update on my Emobot project since we last spoke.

I’ve recently implemented multi-tool orchestration connecting email, calendar, and to-do lists, along with a memory module for personalized and proactive assistance. It’s now much better at turning everyday signals into concrete suggestions.

If you’re interested, I’d love to schedule a short call next week to explore potential collaboration or hear your thoughts.

Best,
Yifei

Compared to your emails to professors, this is slightly more friendly and concise, but still professional.""",
                "actions": []
            },
            # Scene 7: Explain tone consistency
            {
                "id": "scene_7",
                "triggers": [
                    "summarize the tone of these three emails",
                    "explain how each one is consistent"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User wants a summary of the tone differences and consistency with memory.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "Analyzing the three drafts against the user's profile and history.",
                        "confidence": 0.9
                    }
                ],
                "response": """Sure, here’s a quick comparison:

1️⃣ **Email to Professor Tan**
*   **Tone:** formal, structured, polite.
*   **Consistency:** Uses “Dear Professor Tan,” follows usual pattern (greeting → update → request), ends with “Best regards”.

2️⃣ **Email to your mom**
*   **Tone:** casual, warm, and personal, with emojis.
*   **Consistency:** Uses affectionate greeting, mentions daily life, reassures her, ends with “Love you”.

3️⃣ **Email to Alex Li**
*   **Tone:** friendly but concise and professional.
*   **Consistency:** Short paragraphs, straight to the point, clear call to action, matches the updated profile.

All three drafts were generated by combining your explicit profile with historical email samples stored in memory, so that each recipient sees a version of you that is consistent with how you’ve communicated with them before.""",
                "actions": []
            },
            # Scene 8: Show AI Insights
            {
                "id": "scene_8",
                "triggers": [
                    "show me today’s AI Insights",
                    "show today's AI Insights"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User requested AI Insights. I need to scan emails, calendar, and to-dos for patterns and conflicts.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: insights",
                        "reasoning": "Generating insights from cross-referencing data sources.",
                        "tool_name": "insights",
                        "parameters": {"operation": "generate_daily_insights"}
                    },
                    {
                        "step": 3,
                        "type": "observation",
                        "action": "Observation from insights",
                        "reasoning": "Found 3 insights: Interview prep missing, Emobot draft delayed, Polishing tasks fragmented.",
                        "confidence": 1.0
                    }
                ],
                "response": """Here are today’s AI Insights based on your latest emails, calendar, and to-dos:

**Insight #1 – Interview prep is missing**
📧 I found an unread email from Microsoft AI confirming an interview on Friday at 10:00 AM.
📅 Your calendar currently has no dedicated “interview prep” time before that.
✅ Suggested actions:
*   Reserve 1 hour tomorrow and 1 hour the day after for interview preparation.
*   Create a to-do to summarize your key talking points and project highlights.

**Insight #2 – Emobot draft may be delayed**
📧 Three days ago, Professor Tan asked for an updated Emobot draft; you haven’t replied yet.
📝 Your to-do “Finish Emobot draft v2” is already 2 days overdue.
✅ Suggested actions:
*   Block a 2-hour focus session this week to finish the draft.
*   Draft a short email to update him on your progress and commit to a specific sending date.

**Insight #3 – Emobot polishing tasks are fragmented**
📝 I see three scattered tasks related to Emobot:
*   “Refine Emobot architecture slide”
*   “Clean up Emobot GitHub README”
*   “Record short Emobot demo video”
📅 They are spread out and some are overdue.
✅ Suggested actions:
*   Combine them into one consolidated to-do: “Emobot polishing sprint”.
*   Reserve a continuous 3-hour block this weekend to finish them together.

You can say something like: “Accept insights 1 and 2,” and I’ll automatically execute the corresponding actions.""",
                "actions": []
            },
            # Scene 9: Accept insights
            {
                "id": "scene_9",
                "triggers": [
                    "Accept Insight 1 and Insight 2",
                    "create the suggested calendar blocks and to-dos"
                ],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "type": "thought",
                        "action": "Thinking",
                        "reasoning": "User accepted Insights 1 and 2. I need to execute the suggested actions: create calendar events, add to-dos, and draft an email.",
                        "confidence": 0.9
                    },
                    {
                        "step": 2,
                        "type": "tool_call",
                        "action": "Action: calendar",
                        "reasoning": "Creating interview prep blocks.",
                        "tool_name": "calendar",
                        "parameters": {"operation": "create_event", "title": "Interview prep"}
                    },
                    {
                        "step": 3,
                        "type": "tool_call",
                        "action": "Action: todo_list",
                        "reasoning": "Creating preparation task.",
                        "tool_name": "todo_list",
                        "parameters": {"operation": "add_task", "title": "Prepare talking points"}
                    },
                    {
                        "step": 4,
                        "type": "tool_call",
                        "action": "Action: email",
                        "reasoning": "Drafting update email to Professor Tan.",
                        "tool_name": "email",
                        "parameters": {"operation": "create_draft", "recipient": "chenhao@uchicago.edu"}
                    }
                ],
                "response": """Understood. I’ll turn Insights 1 and 2 into concrete actions.

**For Insight #1 – Interview prep**
📅 **Calendar:** Created two prep blocks (Tomorrow 7:00–8:00 PM, Day after 7:00–8:00 PM).
📝 **To-Do:** Added task "Prepare talking points for Microsoft AI Asia interview".

**For Insight #2 – Emobot draft**
📅 **Calendar:** Created focus block (Thursday 3:00–5:00 PM).
📝 **To-Do:** Updated task "Finish Emobot draft v2".
✉️ **Email:** Drafted a short update email to Professor Tan.

✅ The calendar blocks and to-dos have been created, and the email has been saved as a draft.

Would you like me to open your calendar or the draft email so you can show them on screen?""",
                "actions": [
                    {
                        "tool": "calendar",
                        "parameters": {
                            "operation": "create_event",
                            "title": "Interview prep – Microsoft AI Asia",
                            "start_time": "2025-12-03T19:00:00",
                            "description": "Prepare for Microsoft AI interview"
                        }
                    },
                    {
                        "tool": "calendar",
                        "parameters": {
                            "operation": "create_event",
                            "title": "Interview prep – mock questions",
                            "start_time": "2025-12-04T19:00:00",
                            "description": "Mock interview practice"
                        }
                    },
                    {
                        "tool": "todo_list",
                        "parameters": {
                            "operation": "add_task",
                            "title": "Prepare talking points for Microsoft AI Asia interview",
                            "due_date": "2025-12-04T22:00:00"
                        }
                    },
                    {
                        "tool": "calendar",
                        "parameters": {
                            "operation": "create_event",
                            "title": "Focus block – Emobot draft v2",
                            "start_time": "2025-12-04T15:00:00",
                            "description": "Finish Emobot draft v2"
                        }
                    },
                    {
                        "tool": "email",
                        "parameters": {
                            "operation": "create_draft",
                            "recipient": "chenhao@uchicago.edu",
                            "subject": "Brief update on Emobot draft",
                            "body": "Dear Professor Tan,\n\nI wanted to let you know that I’m currently working on the updated draft of my Emobot project. I have scheduled focused time later this week to finalize it and plan to send you the new version by Thursday evening.\n\nThank you for your patience, and I appreciate your guidance on this project.\n\nBest regards,\nYifei"
                        }
                    }
                ]
            }
        ]

    def is_demo_query(self, query: str) -> bool:
        """Check if query matches any demo scenario"""
        query_lower = query.lower()
        for scenario in self.scenarios:
            for trigger in scenario["triggers"]:
                if trigger.lower() in query_lower:
                    return True
        return False

    def execute_demo_scenario(self, query: str, reasoning_module) -> Dict[str, Any]:
        """Execute the matched demo scenario"""
        query_lower = query.lower()
        matched_scenario = None
        
        # Find matching scenario
        for scenario in self.scenarios:
            for trigger in scenario["triggers"]:
                if trigger.lower() in query_lower:
                    matched_scenario = scenario
                    break
            if matched_scenario:
                break
        
        if not matched_scenario:
            return {"response": "I'm sorry, I couldn't process that demo request."}
        
        self.logger.info(f"Executing demo scenario: {matched_scenario['id']}")
        
        # Simulate thinking time (2-4 seconds)
        sleep_time = random.uniform(2.0, 4.0)
        self.logger.info(f"Simulating thinking for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        
        # Populate reasoning steps
        if "reasoning_steps" in matched_scenario:
            reasoning_module.last_reasoning_steps = matched_scenario["reasoning_steps"]
            self.logger.info(f"Populated {len(matched_scenario['reasoning_steps'])} reasoning steps")
        
        # Execute actions if any
        for action in matched_scenario["actions"]:
            try:
                tool_name = action["tool"]
                parameters = action["parameters"]
                
                if tool_name == "memory":
                    # Handle memory updates specially if needed, or just skip as it's mocked in response
                    pass
                else:
                    self.logger.info(f"Executing demo action: {tool_name} with {parameters}")
                    reasoning_module.action_executor.execute_action(tool_name, parameters)
            except Exception as e:
                self.logger.error(f"Failed to execute demo action: {e}")
        
        result = {"response": matched_scenario["response"]}
        if "ui_action" in matched_scenario:
            result["ui_action"] = matched_scenario["ui_action"]
            
        return result
