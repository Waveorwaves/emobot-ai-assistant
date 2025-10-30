# Emobot Frontend

A React-based dashboard for an AI reasoning assistant with comprehensive demo functionality.

## Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation & Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open browser at `http://localhost:5173`

### Available Scripts
- `npm run dev` - Start development server

## Demo Features

### Dashboard Page (Default Landing)
Central hub with summary widgets showing calendar events (4 today), tasks (8/12 completed), emails (5 unread), active missions with progress bars, and integrated chat panel.

### Chat Interface
Full messaging experience with AI responses, message history, and interactive cat avatar.

### Calendar Management  
Sample schedule with 4 events, different event types (meetings, tasks, reminders), and quick action buttons for scheduling.

### Email Client
Complete email interface with 5 sample emails, folder system (Inbox, Sent, Drafts, Trash, Archive), and standard email actions (star, reply, forward).

### Todo Management
Task organization with 6 sample tasks across categories, priority levels with color coding, completion toggles, add new task form, and filtering options.

### Activity History
Comprehensive logs of 8 sample activities across system types with expandable detail views and status indicators.

### Settings Panel
Full configuration interface covering profile, notifications, privacy & security, appearance, and system settings.

### Welcome Page
Clean landing interface with interactive elements and modern design.

## Navigation

### Demo Mode
Top-right corner buttons provide instant access to all pages: Welcome, Login, Main (Chat), Dashboard, System Log, Calendar, Email, Todo, History, Settings.

### Sidebar Navigation
Collapsible menu with icon-based navigation available on main pages.

## Technical Details

### Tech Stack
- React 18.2.0 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Lucide React for icons
- Axios for API integration

### Architecture
Component-based React app with TypeScript, local state management, and API layer configured for backend integration at `localhost:8000`.

### Design
Dark theme with professional styling, responsive layouts, and accessibility considerations.

## Backend Integration Status

### Current State
- Runs independently without backend
- Uses mock data for all features
- API client configured for future connection

## Demo Data

Includes realistic sample content:
- Workplace emails and communications
- Calendar events (meetings, tasks, appointments)
- Tasks across various categories and priorities
- AI conversation examples
- Performance and usage statistics

All interactive elements are functional with sample data to demonstrate the complete user experience.

## Current Limitations

- No data persistence between sessions
- Static demo data only
- Search inputs are display-only
- No real-time backend integration

This frontend provides a complete, interactive demo of the Emobot AI assistant interface with full functionality across calendar, email, task management, and chat features.
