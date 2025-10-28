"""
Web Application for Emobot
Provides HTTP API and simple web interface
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, render_template_string

# Try to import CORS, make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️  flask-cors not installed. CORS will not be enabled.")
    print("   Install with: pip install flask-cors")
import threading
import time

from agent.reasoning import ReasoningModule
from agent.reasoning_wrapper import ReasoningWrapper
from agent.actions import ActionExecutor
from tools.mcp_server.server import MCPToolServer
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Enable CORS if available
if CORS_AVAILABLE:
    CORS(app)  # Enable CORS for frontend access
    print("✅ CORS enabled for cross-origin requests")

# Global variables
reasoning_module = None
reasoning_wrapper = None
mcp_server_thread = None
server_url = "http://127.0.0.1:8080"

# Enhanced HTML template with multiple pages
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Emobot - AI Assistant</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .app-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 1200px;
            height: 700px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 20px 20px 0 0;
            text-align: center;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        
        /* Navigation */
        .nav-container {
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
            padding: 0;
        }
        .nav-tabs {
            display: flex;
            list-style: none;
        }
        .nav-tab {
            flex: 1;
            text-align: center;
        }
        .nav-tab button {
            width: 100%;
            padding: 15px 20px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        .nav-tab button:hover {
            background: #e9ecef;
            color: #333;
        }
        .nav-tab button.active {
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }
        
        /* Content Area */
        .content-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .page {
            display: none;
            flex: 1;
            flex-direction: column;
            overflow: hidden;
        }
        .page.active {
            display: flex;
        }
        
        /* Chat Page Styles */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f7f7f7;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user { justify-content: flex-end; }
        .message.bot { justify-content: flex-start; }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
        }
        .message.bot .message-content {
            background: white;
            color: #333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        .input-form {
            display: flex;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        #messageInput:focus {
            border-color: #667eea;
        }
        #sendButton {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        #sendButton:hover {
            transform: scale(1.05);
        }
        #sendButton:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            padding: 12px 16px;
            background: white;
            border-radius: 18px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .loading.active { display: block; }
        .loading-dots {
            display: flex;
            gap: 5px;
        }
        .loading-dots span {
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        /* Calendar Page Styles */
        .calendar-container {
            flex: 1;
            padding: 20px;
            background: #f7f7f7;
            overflow-y: auto;
        }
        .calendar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .calendar-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        .refresh-btn {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .events-list {
            display: grid;
            gap: 15px;
        }
        .event-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }
        .event-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        .event-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .event-time {
            font-size: 14px;
            color: #667eea;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .event-description {
            font-size: 14px;
            color: #666;
            line-height: 1.4;
        }
        .no-events {
            text-align: center;
            padding: 40px;
            color: #666;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .loading-calendar {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        .error-message {
            background: #ffe6e6;
            color: #d63031;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #d63031;
        }
        
        /* Confirmation message styles */
        .confirmation-pending .message-content {
            background: #fff3cd !important;
            color: #856404 !important;
            border: 1px solid #ffeaa7 !important;
            border-left: 4px solid #fdcb6e !important;
        }
        
        .confirmation-message {
            font-weight: 600;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        /* Email Page Styles */
        .email-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #f7f7f7;
            overflow: hidden;
        }
        
        .email-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .email-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .email-actions {
            display: flex;
            gap: 10px;
        }
        
        .action-btn {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s;
        }
        
        .action-btn:hover {
            background: #5a6fd8;
        }
        
        .email-content {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        .email-sidebar {
            width: 200px;
            background: white;
            border-right: 1px solid #e0e0e0;
            padding: 15px;
            overflow-y: auto;
        }
        
        .sidebar-section {
            margin-bottom: 20px;
        }
        
        .sidebar-section h4 {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .folder-list, .label-list {
            list-style: none;
            padding: 0;
        }
        
        .folder-list li, .label-list li {
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 6px;
            margin-bottom: 2px;
            font-size: 14px;
            transition: background 0.2s;
        }
        
        .folder-list li:hover, .label-list li:hover {
            background: #f0f0f0;
        }
        
        .folder-list li.active {
            background: #667eea;
            color: white;
        }
        
        .email-main {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .email-list {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
        }
        
        .email-item {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .email-item:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .email-item.unread {
            border-left: 4px solid #667eea;
            font-weight: 600;
        }
        
        .email-sender {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .email-subject {
            color: #555;
            margin-bottom: 5px;
        }
        
        .email-snippet {
            color: #777;
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .email-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: #999;
        }
        
        .loading-email {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 0;
            border-radius: 10px;
            width: 80%;
            max-width: 600px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .modal-header h3 {
            margin: 0;
            color: #333;
        }
        
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #000;
        }
        
        .modal-body {
            padding: 20px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .contact-btn {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .form-group {
            position: relative;
        }
        
        .form-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }
        
        .send-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .draft-btn {
            background: #ffc107;
            color: #333;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .cancel-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        
        /* Todo Page Styles */
        .todo-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #f7f7f7;
            overflow: hidden;
        }
        
        .todo-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .todo-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .todo-actions {
            display: flex;
            gap: 10px;
        }
        
        .todo-filters {
            display: flex;
            gap: 10px;
            padding: 15px 20px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .filter-btn {
            padding: 8px 16px;
            background: #f0f0f0;
            color: #666;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .filter-btn:hover {
            background: #e0e0e0;
        }
        
        .filter-btn.active {
            background: #667eea;
            color: white;
        }
        
        .todo-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .todo-list {
            display: grid;
            gap: 15px;
        }
        
        .todo-item {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid #667eea;
        }
        
        .todo-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        
        .todo-item.priority-low {
            border-left-color: #28a745;
        }
        
        .todo-item.priority-medium {
            border-left-color: #ffc107;
        }
        
        .todo-item.priority-high {
            border-left-color: #fd7e14;
        }
        
        .todo-item.priority-urgent {
            border-left-color: #dc3545;
        }
        
        .todo-item.completed {
            opacity: 0.7;
        }
        
        .todo-item.completed .todo-item-title {
            text-decoration: line-through;
            color: #999;
        }
        
        .todo-item-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .todo-item-title-section {
            flex: 1;
        }
        
        .todo-item-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .todo-item-meta {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            font-size: 12px;
            color: #666;
        }
        
        .todo-badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }
        
        .badge-priority {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .badge-priority.low {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .badge-priority.medium {
            background: #fff3e0;
            color: #f57c00;
        }
        
        .badge-priority.high {
            background: #ffe0b2;
            color: #e65100;
        }
        
        .badge-priority.urgent {
            background: #ffebee;
            color: #c62828;
        }
        
        .badge-category {
            background: #f3e5f5;
            color: #7b1fa2;
        }
        
        .badge-status {
            background: #e0e0e0;
            color: #424242;
        }
        
        .badge-status.completed {
            background: #c8e6c9;
            color: #2e7d32;
        }
        
        .badge-status.in_progress {
            background: #fff9c4;
            color: #f57f17;
        }
        
        .todo-item-description {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        
        .todo-item-tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }
        
        .todo-tag {
            padding: 2px 8px;
            background: #e3f2fd;
            color: #1976d2;
            border-radius: 12px;
            font-size: 11px;
        }
        
        .todo-item-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #f0f0f0;
        }
        
        .todo-item-date {
            font-size: 12px;
            color: #999;
        }
        
        .todo-item-date.overdue {
            color: #dc3545;
            font-weight: 600;
        }
        
        .todo-item-actions {
            display: flex;
            gap: 5px;
        }
        
        .todo-action-btn {
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }
        
        .todo-action-btn.complete {
            background: #28a745;
            color: white;
        }
        
        .todo-action-btn.complete:hover {
            background: #218838;
        }
        
        .todo-action-btn.edit {
            background: #667eea;
            color: white;
        }
        
        .todo-action-btn.edit:hover {
            background: #5a6fd8;
        }
        
        .todo-action-btn.delete {
            background: #dc3545;
            color: white;
        }
        
        .todo-action-btn.delete:hover {
            background: #c82333;
        }
        
        .loading-todo {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        
        .no-todos {
            text-align: center;
            padding: 40px;
            color: #666;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <h1>🤖 Emobot</h1>
            <p>Your Intelligent AI Assistant</p>
        </div>
        
        <!-- Navigation -->
        <div class="nav-container">
            <ul class="nav-tabs">
                <li class="nav-tab">
                    <button onclick="switchPage('chat')" class="nav-btn active" data-page="chat">
                        💬 Chat
                    </button>
                </li>
                <li class="nav-tab">
                    <button onclick="switchPage('calendar')" class="nav-btn" data-page="calendar">
                        📅 Calendar
                    </button>
                </li>
                <li class="nav-tab">
                    <button onclick="switchPage('email')" class="nav-btn" data-page="email">
                        📧 Email
                    </button>
                </li>
                <li class="nav-tab">
                    <button onclick="switchPage('todo')" class="nav-btn" data-page="todo">
                        ✅ Todo
                    </button>
                </li>
            </ul>
        </div>
        
        <!-- Content Area -->
        <div class="content-area">
            <!-- Chat Page -->
            <div id="chatPage" class="page active">
                <div class="chat-container" id="chatContainer">
                    <div class="message bot">
                        <div class="message-content">
                            Hello! I'm Emobot, your AI assistant. I can help you search the web, manage emails, create tasks, and more. How can I help you today?
                        </div>
                    </div>
                </div>
                <div class="input-container">
                    <form class="input-form" id="chatForm">
                        <input 
                            type="text" 
                            id="messageInput" 
                            placeholder="Type your message here..."
                            autocomplete="off"
                            required
                        >
                        <button type="submit" id="sendButton">Send</button>
                    </form>
                </div>
            </div>
            
            <!-- Calendar Page -->
            <div id="calendarPage" class="page">
                <div class="calendar-container">
                    <div class="calendar-header">
                        <div class="calendar-title">📅 Your Calendar Events</div>
                        <button class="refresh-btn" onclick="loadCalendarEvents()">🔄 Refresh</button>
                    </div>
                    <div id="calendarContent">
                        <div class="loading-calendar">Loading calendar events...</div>
                    </div>
                </div>
            </div>
            
            <!-- Email Page -->
            <div id="emailPage" class="page">
                <div class="email-container">
                    <div class="email-header">
                        <div class="email-title">📧 Email Management</div>
                        <div class="email-actions">
                            <button class="action-btn" onclick="loadInbox()">📥 Inbox</button>
                            <button class="action-btn" onclick="loadContacts()">👥 Contacts</button>
                            <button class="action-btn" onclick="showComposeModal()">✉️ Compose</button>
                            <button class="refresh-btn" onclick="refreshEmailData()">🔄 Refresh</button>
                        </div>
                    </div>
                    <div class="email-content">
                        <div class="email-sidebar">
                            <div class="sidebar-section">
                                <h4>📁 Folders</h4>
                                <ul id="folderList" class="folder-list">
                                    <li onclick="loadInbox()" class="active">📥 Inbox</li>
                                    <li onclick="loadSent()">📤 Sent</li>
                                    <li onclick="loadDrafts()">📝 Drafts</li>
                                    <li onclick="loadTrash()">🗑️ Trash</li>
                                </ul>
                            </div>
                            <div class="sidebar-section">
                                <h4>🏷️ Labels</h4>
                                <ul id="labelList" class="label-list">
                                    <!-- Labels will be loaded here -->
                                </ul>
                            </div>
                        </div>
                        <div class="email-main">
                            <div id="emailList" class="email-list">
                                <div class="loading-email">Loading emails...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Compose Email Modal -->
            <div id="composeModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>✉️ Compose Email</h3>
                        <span class="close" onclick="closeComposeModal()">&times;</span>
                    </div>
                    <div class="modal-body">
                        <form id="composeForm">
                            <div class="form-group">
                                <label>To:</label>
                                <input type="email" id="composeTo" required>
                                <button type="button" onclick="showContactPicker()" class="contact-btn">👥</button>
                            </div>
                            <div class="form-group">
                                <label>Subject:</label>
                                <input type="text" id="composeSubject" required>
                            </div>
                            <div class="form-group">
                                <label>Message:</label>
                                <textarea id="composeBody" rows="10" required></textarea>
                            </div>
                            <div class="form-actions">
                                <button type="submit" class="send-btn">📤 Send</button>
                                <button type="button" onclick="saveDraft()" class="draft-btn">📝 Save Draft</button>
                                <button type="button" onclick="closeComposeModal()" class="cancel-btn">❌ Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            
            <!-- Todo Page -->
            <div id="todoPage" class="page">
                <div class="todo-container">
                    <div class="todo-header">
                        <div class="todo-title">✅ Todo Management</div>
                        <div class="todo-actions">
                            <button class="action-btn" onclick="showAddTodoModal()">➕ Add Task</button>
                            <button class="refresh-btn" onclick="loadTodoList()">🔄 Refresh</button>
                        </div>
                    </div>
                    
                    <div class="todo-filters">
                        <button class="filter-btn active" onclick="filterTodos('all')" data-filter="all">All</button>
                        <button class="filter-btn" onclick="filterTodos('pending')" data-filter="pending">Pending</button>
                        <button class="filter-btn" onclick="filterTodos('in_progress')" data-filter="in_progress">In Progress</button>
                        <button class="filter-btn" onclick="filterTodos('completed')" data-filter="completed">Completed</button>
                    </div>
                    
                    <div id="todoContent" class="todo-content">
                        <div class="loading-todo">Loading tasks...</div>
                    </div>
                </div>
            </div>
            
            <!-- Add/Edit Todo Modal -->
            <div id="todoModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 id="todoModalTitle">➕ Add New Task</h3>
                        <span class="close" onclick="closeTodoModal()">&times;</span>
                    </div>
                    <div class="modal-body">
                        <form id="todoForm">
                            <input type="hidden" id="todoId" value="">
                            <div class="form-group">
                                <label>Task Title *</label>
                                <input type="text" id="todoTitle" required placeholder="Enter task title">
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea id="todoDescription" rows="3" placeholder="Enter task description (optional)"></textarea>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Priority</label>
                                    <select id="todoPriority">
                                        <option value="low">Low</option>
                                        <option value="medium" selected>Medium</option>
                                        <option value="high">High</option>
                                        <option value="urgent">Urgent</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Category</label>
                                    <select id="todoCategory">
                                        <option value="work">Work</option>
                                        <option value="personal" selected>Personal</option>
                                        <option value="study">Study</option>
                                        <option value="health">Health</option>
                                        <option value="shopping">Shopping</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Due Date</label>
                                <input type="date" id="todoDueDate">
                            </div>
                            <div class="form-group">
                                <label>Tags (comma separated)</label>
                                <input type="text" id="todoTags" placeholder="e.g., urgent, important">
                            </div>
                            <div class="form-actions">
                                <button type="submit" class="send-btn">💾 Save Task</button>
                                <button type="button" onclick="closeTodoModal()" class="cancel-btn">❌ Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Page switching functionality
        function switchPage(pageName) {
            // Hide all pages
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // Remove active class from all nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected page
            document.getElementById(pageName + 'Page').classList.add('active');
            
            // Add active class to selected nav button
            document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
            
            // Load page-specific content
            if (pageName === 'calendar') {
                loadCalendarEvents();
            } else if (pageName === 'email') {
                loadEmailPage();
            } else if (pageName === 'todo') {
                loadTodoList();
            }
        }
        
        // Calendar functionality
        async function loadCalendarEvents() {
            const calendarContent = document.getElementById('calendarContent');
            calendarContent.innerHTML = '<div class="loading-calendar">Loading calendar events...</div>';
            
            try {
                const response = await fetch('/api/calendar/events');
                const data = await response.json();
                
                if (data.success && data.events && data.events.length > 0) {
                    displayCalendarEvents(data.events);
                } else {
                    calendarContent.innerHTML = `
                        <div class="no-events">
                            <h3>📅 No events found</h3>
                            <p>You don't have any calendar events at the moment.</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading calendar events:', error);
                calendarContent.innerHTML = `
                    <div class="error-message">
                        ❌ Failed to load calendar events: ${error.message}
                    </div>
                `;
            }
        }
        
        function displayCalendarEvents(events) {
            const calendarContent = document.getElementById('calendarContent');
            
            const eventsHtml = events.map(event => {
                const eventTime = event.time || event.start_time || event.datetime || 'No time specified';
                const eventTitle = event.title || event.summary || 'Untitled Event';
                const eventDescription = event.description || event.details || '';
                
                return `
                    <div class="event-card">
                        <div class="event-title">${escapeHtml(eventTitle)}</div>
                        <div class="event-time">
                            🕒 ${escapeHtml(eventTime)}
                        </div>
                        ${eventDescription ? `<div class="event-description">${escapeHtml(eventDescription)}</div>` : ''}
                    </div>
                `;
            }).join('');
            
            calendarContent.innerHTML = `<div class="events-list">${eventsHtml}</div>`;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Chat functionality (existing code)
        const chatContainer = document.getElementById('chatContainer');
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        let loadingElement = null;

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showLoading() {
            loadingElement = document.createElement('div');
            loadingElement.className = 'message bot';
            loadingElement.innerHTML = `
                <div class="loading active">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            chatContainer.appendChild(loadingElement);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function hideLoading() {
            if (loadingElement) {
                loadingElement.remove();
                loadingElement = null;
            }
        }

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, true);
            messageInput.value = '';
            
            // Disable input
            sendButton.disabled = true;
            messageInput.disabled = true;
            showLoading();

            try {
                // Send to API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                
                hideLoading();
                
                if (data.success) {
                    addMessage(data.response, false);
                    
                    // Check if there's a pending confirmation
                    if (data.has_pending_confirmation && data.pending_confirmations && data.pending_confirmations.length > 0) {
                        // Add a visual indicator for pending confirmation
                        const confirmationDiv = document.createElement('div');
                        confirmationDiv.className = 'message bot confirmation-pending';
                        confirmationDiv.innerHTML = `
                            <div class="message-content confirmation-message">
                                ⏳ Waiting for your confirmation. Please type 'yes' or 'y' to proceed, 'no' or 'n' to cancel.
                            </div>
                        `;
                        chatContainer.appendChild(confirmationDiv);
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }
                } else {
                    addMessage('Sorry, I encountered an error: ' + data.error, false);
                }
            } catch (error) {
                hideLoading();
                addMessage('Sorry, I could not connect to the server.', false);
                console.error('Error:', error);
            } finally {
                // Re-enable input
                sendButton.disabled = false;
                messageInput.disabled = false;
                messageInput.focus();
            }
        });

        // Focus input on load
        messageInput.focus();
        
        // Email functionality
        async function loadEmailPage() {
            await loadInbox();
            await loadLabels();
        }
        
        async function loadInbox() {
            updateFolderSelection('inbox');
            await loadEmailsByQuery('in:inbox');
        }
        
        async function loadSent() {
            updateFolderSelection('sent');
            await loadEmailsByQuery('in:sent');
        }
        
        async function loadDrafts() {
            updateFolderSelection('drafts');
            await loadEmailsByQuery('in:draft');
        }
        
        async function loadTrash() {
            updateFolderSelection('trash');
            await loadEmailsByQuery('in:trash');
        }
        
        function updateFolderSelection(folderType) {
            // Remove active class from all folder items
            document.querySelectorAll('.folder-list li').forEach(li => li.classList.remove('active'));
            
            // Add active class to selected folder
            const folderMap = {
                'inbox': 0,
                'sent': 1,
                'drafts': 2,
                'trash': 3
            };
            
            const folderItems = document.querySelectorAll('.folder-list li');
            if (folderItems[folderMap[folderType]]) {
                folderItems[folderMap[folderType]].classList.add('active');
            }
        }
        
        async function loadEmailsByQuery(query = null) {
            const emailList = document.getElementById('emailList');
            emailList.innerHTML = '<div class="loading-email">Loading emails...</div>';
            
            try {
                let url = '/api/email/list';
                if (query) {
                    // Add query parameter to URL
                    url = `/api/email/list?query=${encodeURIComponent(query)}`;
                }
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (data.success && data.emails && data.emails.length > 0) {
                    displayEmails(data.emails);
                } else {
                    emailList.innerHTML = `
                        <div class="no-events">
                            <h3>📭 No emails found</h3>
                            <p>${data.error || 'Your mailbox is empty or there was an error loading emails.'}</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading emails:', error);
                emailList.innerHTML = `
                    <div class="error-message">
                        ❌ Failed to load emails: ${error.message}
                    </div>
                `;
            }
        }
        
        function displayEmails(emails) {
            const emailList = document.getElementById('emailList');
            
            const emailsHtml = emails.map(email => {
                const isUnread = !email.is_read;
                const sender = email.sender || 'Unknown Sender';
                const subject = email.subject || 'No Subject';
                const snippet = email.snippet || email.body || '';
                const date = email.date || '';
                
                return `
                    <div class="email-item ${isUnread ? 'unread' : ''}" onclick="openEmail('${email.id}')">
                        <div class="email-sender">${escapeHtml(sender)}</div>
                        <div class="email-subject">${escapeHtml(subject)}</div>
                        <div class="email-snippet">${escapeHtml(snippet.substring(0, 100))}${snippet.length > 100 ? '...' : ''}</div>
                        <div class="email-meta">
                            <span>${date}</span>
                            <span>${isUnread ? '🔵 Unread' : '✅ Read'}</span>
                        </div>
                    </div>
                `;
            }).join('');
            
            emailList.innerHTML = emailsHtml;
        }
        
        async function loadLabels() {
            try {
                const response = await fetch('/api/email/labels');
                const data = await response.json();
                
                if (data.success && data.labels) {
                    const labelList = document.getElementById('labelList');
                    const labelsHtml = data.labels.map(label => {
                        if (label.type === 'user') { // Only show user-created labels
                            return `<li onclick="loadLabelEmails('${label.id}')">${label.name}</li>`;
                        }
                        return '';
                    }).join('');
                    labelList.innerHTML = labelsHtml;
                }
            } catch (error) {
                console.error('Error loading labels:', error);
            }
        }
        
        async function loadContacts() {
            try {
                const response = await fetch('/api/email/contacts');
                const data = await response.json();
                
                if (data.success && data.contacts) {
                    console.log('Contacts loaded:', data.contacts);
                    // Could show contacts in a modal or sidebar
                }
            } catch (error) {
                console.error('Error loading contacts:', error);
            }
        }
        
        function showComposeModal() {
            document.getElementById('composeModal').style.display = 'block';
        }
        
        function closeComposeModal() {
            document.getElementById('composeModal').style.display = 'none';
            document.getElementById('composeForm').reset();
        }
        
        async function refreshEmailData() {
            if (document.getElementById('emailPage').classList.contains('active')) {
                await loadEmailPage();
            }
        }
        
        // Compose form handler
        document.getElementById('composeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const to = document.getElementById('composeTo').value;
            const subject = document.getElementById('composeSubject').value;
            const body = document.getElementById('composeBody').value;
            
            try {
                const response = await fetch('/api/email/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        to: to,
                        subject: subject,
                        body: body
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Email sent successfully!');
                    closeComposeModal();
                } else {
                    alert('Failed to send email: ' + data.error);
                }
            } catch (error) {
                console.error('Error sending email:', error);
                alert('Failed to send email: ' + error.message);
            }
        });
        
        async function saveDraft() {
            const to = document.getElementById('composeTo').value;
            const subject = document.getElementById('composeSubject').value;
            const body = document.getElementById('composeBody').value;
            
            try {
                const response = await fetch('/api/email/draft', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        to: to,
                        subject: subject,
                        body: body
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Draft saved successfully!');
                } else {
                    alert('Failed to save draft: ' + data.error);
                }
            } catch (error) {
                console.error('Error saving draft:', error);
                alert('Failed to save draft: ' + error.message);
            }
        }
        
        function openEmail(emailId) {
            // This could open email details in a modal or navigate to detail view
            console.log('Opening email:', emailId);
            // For now, just mark as read
            markEmailAsRead(emailId);
        }
        
        async function markEmailAsRead(emailId) {
            try {
                const response = await fetch('/api/email/mark-read', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message_id: emailId
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    // Refresh email list to show updated read status
                    loadInbox();
                }
            } catch (error) {
                console.error('Error marking email as read:', error);
            }
        }
        
        // Load calendar events when page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Don't auto-load calendar on page load to avoid unnecessary API calls
            // It will load when user clicks the calendar tab
        });
        
        // ============================================================================
        // Todo Functionality
        // ============================================================================
        
        let currentFilter = 'all';
        let allTodos = [];
        
        async function loadTodoList() {
            const todoContent = document.getElementById('todoContent');
            todoContent.innerHTML = '<div class="loading-todo">Loading tasks...</div>';
            
            try {
                const response = await fetch('/api/todo/list');
                const data = await response.json();
                
                if (data.success && data.tasks) {
                    allTodos = data.tasks;
                    displayTodos(allTodos);
                } else {
                    todoContent.innerHTML = `
                        <div class="no-todos">
                            <h3>📝 No tasks found</h3>
                            <p>Click "Add Task" to create your first todo item.</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading todos:', error);
                todoContent.innerHTML = `
                    <div class="error-message">
                        ❌ Failed to load tasks: ${error.message}
                    </div>
                `;
            }
        }
        
        function displayTodos(todos) {
            const todoContent = document.getElementById('todoContent');
            
            if (!todos || todos.length === 0) {
                todoContent.innerHTML = `
                    <div class="no-todos">
                        <h3>📝 No tasks found</h3>
                        <p>Click "Add Task" to create your first todo item.</p>
                    </div>
                `;
                return;
            }
            
            const todosHtml = todos.map(todo => {
                const priority = todo.priority || 'medium';
                const status = todo.status || 'pending';
                const category = todo.category || 'other';
                const isCompleted = status === 'completed';
                const isOverdue = todo.overdue || false;
                
                let statusText = status.replace('_', ' ');
                statusText = statusText.charAt(0).toUpperCase() + statusText.slice(1);
                
                return `
                    <div class="todo-item priority-${priority} ${isCompleted ? 'completed' : ''}" data-status="${status}">
                        <div class="todo-item-header">
                            <div class="todo-item-title-section">
                                <div class="todo-item-title">${escapeHtml(todo.title)}</div>
                                <div class="todo-item-meta">
                                    <span class="todo-badge badge-priority ${priority}">${priority.toUpperCase()}</span>
                                    <span class="todo-badge badge-category">${category}</span>
                                    <span class="todo-badge badge-status ${status}">${statusText}</span>
                                </div>
                            </div>
                        </div>
                        ${todo.description ? `<div class="todo-item-description">${escapeHtml(todo.description)}</div>` : ''}
                        ${todo.tags && todo.tags.length > 0 ? `
                            <div class="todo-item-tags">
                                ${todo.tags.map(tag => `<span class="todo-tag">${escapeHtml(tag)}</span>`).join('')}
                            </div>
                        ` : ''}
                        <div class="todo-item-footer">
                            <div class="todo-item-date ${isOverdue ? 'overdue' : ''}">
                                ${todo.due_date ? `📅 Due: ${todo.due_date}${isOverdue ? ' (Overdue!)' : ''}` : 'No due date'}
                            </div>
                            <div class="todo-item-actions">
                                ${!isCompleted ? `<button class="todo-action-btn complete" onclick="markTodoComplete('${todo.id}')">✓ Complete</button>` : ''}
                                <button class="todo-action-btn edit" onclick="editTodo('${todo.id}')">✏️ Edit</button>
                                <button class="todo-action-btn delete" onclick="deleteTodo('${todo.id}')">🗑️ Delete</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            
            todoContent.innerHTML = `<div class="todo-list">${todosHtml}</div>`;
        }
        
        function filterTodos(filter) {
            currentFilter = filter;
            
            // Update active filter button
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
            
            // Filter todos
            let filteredTodos = allTodos;
            if (filter !== 'all') {
                filteredTodos = allTodos.filter(todo => todo.status === filter);
            }
            
            displayTodos(filteredTodos);
        }
        
        function showAddTodoModal() {
            document.getElementById('todoModalTitle').textContent = '➕ Add New Task';
            document.getElementById('todoForm').reset();
            document.getElementById('todoId').value = '';
            document.getElementById('todoModal').style.display = 'block';
        }
        
        function closeTodoModal() {
            document.getElementById('todoModal').style.display = 'none';
        }
        
        function editTodo(todoId) {
            const todo = allTodos.find(t => t.id === todoId);
            if (!todo) return;
            
            document.getElementById('todoModalTitle').textContent = '✏️ Edit Task';
            document.getElementById('todoId').value = todo.id;
            document.getElementById('todoTitle').value = todo.title;
            document.getElementById('todoDescription').value = todo.description || '';
            document.getElementById('todoPriority').value = todo.priority || 'medium';
            document.getElementById('todoCategory').value = todo.category || 'personal';
            document.getElementById('todoDueDate').value = todo.due_date || '';
            document.getElementById('todoTags').value = todo.tags ? todo.tags.join(', ') : '';
            
            document.getElementById('todoModal').style.display = 'block';
        }
        
        async function markTodoComplete(todoId) {
            try {
                const response = await fetch(`/api/todo/update/${todoId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        status: 'completed'
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    loadTodoList();
                } else {
                    alert('Failed to mark task as complete: ' + data.error);
                }
            } catch (error) {
                console.error('Error marking todo complete:', error);
                alert('Failed to mark task as complete');
            }
        }
        
        async function deleteTodo(todoId) {
            if (!confirm('Are you sure you want to delete this task?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/todo/delete/${todoId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    loadTodoList();
                } else {
                    alert('Failed to delete task: ' + data.error);
                }
            } catch (error) {
                console.error('Error deleting todo:', error);
                alert('Failed to delete task');
            }
        }
        
        // Handle todo form submission
        document.getElementById('todoForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const todoId = document.getElementById('todoId').value;
            const title = document.getElementById('todoTitle').value.trim();
            const description = document.getElementById('todoDescription').value.trim();
            const priority = document.getElementById('todoPriority').value;
            const category = document.getElementById('todoCategory').value;
            const dueDate = document.getElementById('todoDueDate').value;
            const tagsInput = document.getElementById('todoTags').value.trim();
            const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];
            
            const todoData = {
                title,
                description,
                priority,
                category,
                due_date: dueDate,
                tags
            };
            
            try {
                let response;
                if (todoId) {
                    // Update existing todo
                    response = await fetch(`/api/todo/update/${todoId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(todoData)
                    });
                } else {
                    // Add new todo
                    response = await fetch('/api/todo/add', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(todoData)
                    });
                }
                
                const data = await response.json();
                
                if (data.success) {
                    closeTodoModal();
                    loadTodoList();
                } else {
                    alert('Failed to save task: ' + data.error);
                }
            } catch (error) {
                console.error('Error saving todo:', error);
                alert('Failed to save task');
            }
        });
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const todoModal = document.getElementById('todoModal');
            if (event.target === todoModal) {
                closeTodoModal();
            }
        };
    </script>
</body>
</html>
"""

def start_mcp_server():
    """Start MCP server in background thread"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        config_path = "configs/mcp.yaml"
        server = MCPToolServer(config_path)
        
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        server_config = config.get("server", {})
        
        print(f"✅ MCP server initialized with {len(server.tools)} tools")
        
        server.app.run(
            host=server_config.get("host", "127.0.0.1"),
            port=server_config.get("port", 8080),
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ MCP server error: {e}")

def initialize_agent(model_id="gemini-2.5-flash"):
    """Initialize the reasoning module"""
    global reasoning_module, reasoning_wrapper
    
    try:
        print(f"🤖 Initializing agent with model: {model_id}")
        reasoning_module = ReasoningModule(
            model_id=model_id,
            server_url=server_url,
            use_local_model=False
        )
        reasoning_wrapper = ReasoningWrapper(reasoning_module)
        print("✅ Agent initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/query', methods=['POST'])
def query():
    """Handle query requests (frontend compatible)"""
    try:
        data = request.json
        query_text = data.get('query', '').strip()
        session_id = data.get('session_id', 'default')
        model_id = data.get('model_id', 'gemini-2.5-flash')
        
        if not query_text:
            return jsonify({'success': False, 'error': 'Empty query'}), 400
        
        if not reasoning_wrapper:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Process query through reasoning wrapper (captures steps)
        result = reasoning_wrapper.process_query_with_steps(query_text)
        
        # Add session and model info
        result['session_id'] = session_id
        result['model_id'] = model_id
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Query error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'response': f'Error: {str(e)}',
            'error': str(e),
            'reasoning_steps': [
                {
                    'step': 1,
                    'type': 'error',
                    'message': str(e)
                }
            ]
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with confirmation support"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Empty message'}), 400
        
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Check if there's a pending confirmation (like terminal version)
        if reasoning_module.has_pending_confirmation():
            logging.debug("Processing confirmation response...")
            response = reasoning_module.handle_confirmation_response(message)
        else:
            # Process normal query
            response = reasoning_module.process_query(message)
        
        # Check if there's now a pending confirmation after processing
        has_pending = reasoning_module.has_pending_confirmation()
        pending_confirmations = []
        if has_pending:
            pending_confirmations = reasoning_module.get_pending_confirmation_requests()
        
        return jsonify({
            'success': True,
            'response': response,
            'has_pending_confirmation': has_pending,
            'pending_confirmations': pending_confirmations
        })
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get available tools"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        tools = reasoning_module.action_executor.get_available_tools()
        return jsonify({
            'success': True,
            'tools': tools
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'agent_initialized': reasoning_module is not None,
        'mcp_server': server_url
    })

@app.route('/api/confirmations', methods=['GET'])
def get_pending_confirmations():
    """Get pending confirmation requests"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        has_pending = reasoning_module.has_pending_confirmation()
        pending_confirmations = []
        if has_pending:
            pending_confirmations = reasoning_module.get_pending_confirmation_requests()
        
        return jsonify({
            'success': True,
            'has_pending_confirmation': has_pending,
            'pending_confirmations': pending_confirmations
        })
    except Exception as e:
        logging.error(f"Get confirmations error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/confirmations/cancel', methods=['POST'])
def cancel_confirmations():
    """Cancel all pending confirmations"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Cancel all pending confirmations
        pending = reasoning_module.get_pending_confirmation_requests()
        cancelled_count = 0
        
        for req in pending:
            reasoning_module.cancel_confirmation_request(req['id'])
            cancelled_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Cancelled {cancelled_count} pending confirmations'
        })
    except Exception as e:
        logging.error(f"Cancel confirmations error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Calendar API Endpoints
@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    """Get calendar events"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the calendar tool with list_events operation
        result = reasoning_module.action_executor.execute_action('calendar', {'operation': 'list_events'})
        
        # Extract events from the result
        if isinstance(result, dict) and result.get('status') == 'success':
            events = result.get('events', [])
        else:
            events = []
            
        return jsonify({
            'success': True,
            'events': events
        })
    except Exception as e:
        logging.error(f"Calendar events error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calendar/events', methods=['POST'])
def create_calendar_event():
    """Create calendar event"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        title = data.get('title')
        time = data.get('time')
        duration = data.get('duration', '1 hour')
        description = data.get('description', '')
        
        if not title or not time:
            return jsonify({'success': False, 'error': 'Title and time required'}), 400
        
        # Use the calendar tool with create_event operation
        result = reasoning_module.action_executor.execute_action('calendar', {
            'operation': 'create_event',
            'title': title,
            'start_time': time,
            'description': description
        })
        
        return jsonify({
            'success': True,
            'message': 'Event created',
            'result': result
        })
    except Exception as e:
        logging.error(f"Create event error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Email API Endpoints
@app.route('/api/email/list', methods=['GET'])
def list_emails():
    """List emails"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Get query parameter for filtering (e.g., 'in:sent', 'in:draft')
        search_query = request.args.get('query', '')
        
        if search_query:
            # Use search_emails operation for specific queries
            result = reasoning_module.action_executor.execute_action('email', {
                'operation': 'search_emails',
                'search_query': search_query,
                'max_results': 20
            })
        else:
            # Default to inbox
            result = reasoning_module.action_executor.execute_action('email', {
                'operation': 'read_inbox',
                'max_results': 20
            })
        
        if result and result.get('status') == 'success':
            emails = result.get('emails', result.get('result', []))
            return jsonify({
                'success': True,
                'emails': emails if isinstance(emails, list) else []
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error_message', 'Failed to fetch emails'),
                'emails': []
            })
    except Exception as e:
        logging.error(f"List emails error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/send', methods=['POST'])
def send_email():
    """Send email"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        
        if not to or not subject or not body:
            return jsonify({'success': False, 'error': 'To, subject, and body required'}), 400
        
        # Use the email tool with send operation
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'send_email',
            'recipient': to,
            'subject': subject,
            'body': body
        })
        
        return jsonify({
            'success': True,
            'message': 'Email sent',
            'result': result
        })
    except Exception as e:
        logging.error(f"Send email error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/read/<email_id>', methods=['GET'])
def read_email(email_id):
    """Read specific email"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the email tool with read operation
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'read_inbox',
            'message_id': email_id
        })
        
        return jsonify({
            'success': True,
            'email': result
        })
    except Exception as e:
        logging.error(f"Read email error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/contacts', methods=['GET'])
def list_contacts():
    """List contacts"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        result = reasoning_module.action_executor.execute_action('email', {'operation': 'get_contacts', 'max_results': 100})
        
        return jsonify({
            'success': True,
            'contacts': result.get('result', []) if result.get('status') == 'success' else [],
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Contacts list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/email/labels', methods=['GET'])
def list_labels():
    """List email labels"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        result = reasoning_module.action_executor.execute_action('email', {'operation': 'get_labels'})
        
        return jsonify({
            'success': True,
            'labels': result.get('result', []) if result.get('status') == 'success' else [],
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Labels list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/email/draft', methods=['POST'])
def create_draft():
    """Create email draft"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        
        if not all([to, subject, body]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'create_draft',
            'recipient': to,
            'subject': subject,
            'body': body
        })
        
        return jsonify({
            'success': result.get('status') == 'success',
            'result': result.get('result'),
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Draft creation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/email/mark-read', methods=['POST'])
def mark_email_read():
    """Mark email as read"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        message_id = data.get('message_id')
        
        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID required'}), 400
        
        result = reasoning_module.action_executor.execute_action('email', {
            'operation': 'mark_read',
            'message_id': message_id
        })
        
        return jsonify({
            'success': result.get('status') == 'success',
            'result': result.get('result'),
            'error': result.get('error_message') if result.get('status') != 'success' else None
        })
        
    except Exception as e:
        logging.error(f"Mark read error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Todo API Endpoints
@app.route('/api/todo/list', methods=['GET'])
def list_todos():
    """List todo tasks"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the todo_list tool with view_list operation
        result = reasoning_module.action_executor.execute_action('todo_list', {'operation': 'view_list'})
        
        # Extract tasks from result
        tasks = []
        if isinstance(result, dict):
            if result.get('status') == 'success':
                tasks = result.get('tasks', [])
            else:
                return jsonify({'success': False, 'error': result.get('message', 'Unknown error')}), 500
        
        return jsonify({
            'success': True,
            'tasks': tasks
        })
    except Exception as e:
        logging.error(f"List todos error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/todo/add', methods=['POST'])
def add_todo():
    """Add todo task"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        title = data.get('title')
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        category = data.get('category', 'personal')
        due_date = data.get('due_date')
        tags = data.get('tags', [])
        
        if not title:
            return jsonify({'success': False, 'error': 'Title required'}), 400
        
        # Use the todo_list tool with add_task operation
        params = {
            'operation': 'add_task',
            'title': title,
            'description': description,
            'priority': priority,
            'category': category,
            'tags': tags
        }
        
        if due_date:
            params['due_date'] = due_date
        
        result = reasoning_module.action_executor.execute_action('todo_list', params)
        
        if isinstance(result, dict) and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Task added successfully',
                'task': result.get('task')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Failed to add task')
            }), 500
    except Exception as e:
        logging.error(f"Add todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/todo/update/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update todo task"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        data = request.json
        
        # Build update parameters
        params = {
            'operation': 'update_task',
            'task_id': todo_id
        }
        
        # Add optional fields
        if 'title' in data:
            params['title'] = data['title']
        if 'description' in data:
            params['description'] = data['description']
        if 'priority' in data:
            params['priority'] = data['priority']
        if 'category' in data:
            params['category'] = data['category']
        if 'status' in data:
            params['status'] = data['status']
        if 'due_date' in data:
            params['due_date'] = data['due_date']
        if 'tags' in data:
            params['tags'] = data['tags']
        
        # Use the todo_list tool with update_task operation
        result = reasoning_module.action_executor.execute_action('todo_list', params)
        
        if isinstance(result, dict) and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Task updated successfully',
                'task': result.get('task')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Failed to update task')
            }), 500
    except Exception as e:
        logging.error(f"Update todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/todo/delete/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete todo task"""
    try:
        if not reasoning_module:
            return jsonify({'success': False, 'error': 'Agent not initialized'}), 500
        
        # Use the todo_list tool with delete_task operation
        result = reasoning_module.action_executor.execute_action('todo_list', {
            'operation': 'delete_task',
            'task_id': todo_id
        })
        
        if isinstance(result, dict) and result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Failed to delete task')
            }), 500
    except Exception as e:
        logging.error(f"Delete todo error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Emobot Web Application")
    parser.add_argument('--model', type=str, default='gemini-2.5-flash', help='Model to use')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000, avoid 5000 due to macOS ControlCenter conflict)')
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 Starting Emobot Web Application")
    print("="*60)
    
    # Start MCP server in background
    print("📡 Starting MCP server...")
    global mcp_server_thread
    mcp_server_thread = threading.Thread(target=start_mcp_server, daemon=True)
    mcp_server_thread.start()
    
    # Wait for MCP server to start
    time.sleep(3)
    
    # Initialize agent
    if not initialize_agent(args.model):
        print("❌ Failed to start application")
        sys.exit(1)
    
    print("\n" + "="*60)
    print(f"✅ Emobot Web App is running!")
    print(f"🌐 Open your browser and go to:")
    print(f"   http://{args.host}:{args.port}")
    print("="*60 + "\n")
    
    # Start Flask web server
    app.run(
        host=args.host,
        port=args.port,
        debug=False,
        threaded=True
    )

if __name__ == '__main__':
    main()
