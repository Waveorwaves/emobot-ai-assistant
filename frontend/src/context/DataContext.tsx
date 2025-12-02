import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { reasoningApi, calendarApi, emailApi, todoApi } from '../utils/api';

// Types
export interface CalendarEvent {
  id: string;
  title: string;
  time: string;
  duration: string;
  type: 'meeting' | 'task' | 'reminder' | 'personal';
  description?: string;
  date?: string; // ISO date string for the event date
}

export interface Email {
  id: string;
  sender: string;
  senderEmail: string;
  subject: string;
  preview: string;
  content?: string;
  timestamp: string;
  internalDate?: string;
  read: boolean;
  starred: boolean;
  important: boolean;
  attachments?: number;
  attachmentFiles?: File[];
  folder?: 'inbox' | 'sent' | 'drafts' | 'trash' | 'archive';
  tags?: string[];
}

export interface TodoItem {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  category: string;
  createdAt: string;
  starred: boolean;
  projectId?: string;
  parentId?: string; // For subtasks
  isProject?: boolean;
  subtasks?: string[]; // Array of subtask IDs
}

export interface ReasoningStep {
  step: number;
  type: string;
  action: string;
  reasoning: string;
  confidence: number;
  timestamp?: string;
  tool_name?: string;
  parameters?: any;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  reasoningSteps?: ReasoningStep[];
}

// Helper function to format date in local timezone
const formatDateLocal = (date: Date) => {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const generateMessageId = () =>
  `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

// No initial mock data - all data comes from backend

// Context
interface DataContextType {
  // Calendar
  todayEvents: CalendarEvent[];
  upcomingEvents: CalendarEvent[];
  allEvents: CalendarEvent[];
  setTodayEvents: (events: CalendarEvent[]) => void;
  setUpcomingEvents: (events: CalendarEvent[]) => void;
  addEvent: (event: Omit<CalendarEvent, 'id'>) => void;
  updateEvent: (event: CalendarEvent) => void;
  deleteEvent: (eventId: string) => void;
  getEventsForDate: (date: Date) => CalendarEvent[];
  detectConflicts: (events: CalendarEvent[]) => { eventId: string; conflictsWith: string[] }[];

  // Email
  emails: Email[];
  setEmails: (emails: Email[]) => void;
  markEmailAsRead: (emailId: string) => void;
  toggleEmailStar: (emailId: string) => void;
  toggleEmailImportant: (emailId: string) => void;
  deleteEmail: (emailId: string) => void;
  archiveEmail: (emailId: string) => void;
  restoreEmail: (emailId: string) => void;
  addEmail: (email: Omit<Email, 'id'>) => void;
  addTagToEmail: (emailId: string, tag: string) => void;
  removeTagFromEmail: (emailId: string, tag: string) => void;

  // Todos
  todos: TodoItem[];
  setTodos: (todos: TodoItem[]) => void;
  toggleTodoComplete: (todoId: string) => void;
  toggleTodoStar: (todoId: string) => void;
  addTodo: (todo: Omit<TodoItem, 'id'>) => void;
  updateTodo: (todoId: string, updates: Partial<TodoItem>) => void;
  deleteTodo: (todoId: string) => void;
  addSubtask: (projectId: string, subtask: Omit<TodoItem, 'id'>) => void;
  getSubtasks: (projectId: string) => TodoItem[];

  // Avatar/Profile
  userAvatar: string;
  setUserAvatar: (url: string) => void;
  userName: string;
  setUserName: (name: string) => void;
  emobotAvatar: string;
  setEmobotAvatar: (url: string) => void;
  emobotName: string;
  setEmobotName: (name: string) => void;

  // Chat Messages
  chatMessages: ChatMessage[];
  addChatMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => Promise<void>;
  clearChatMessages: () => void;

  // Dashboard Summaries
  getCalendarSummary: () => {
    todayEvents: number;
    upcomingEvents: number;
    nextEvent: string;
  };
  getEmailSummary: () => {
    unreadEmails: number;
    totalEmails: number;
    recentSender: string;
    priority: number;
  };
  getTodoSummary: () => {
    totalTasks: number;
    completedTasks: number;
    pendingTasks: number;
    completionRate: number;
  };

  // UI Actions
  emailComposeModal: {
    isOpen: boolean;
    to: string;
    subject: string;
    body: string;
  };
  setEmailComposeModal: (modal: { isOpen: boolean; to: string; subject: string; body: string }) => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Start with empty arrays - data will be loaded from backend
  const [allEvents, setAllEvents] = useState<CalendarEvent[]>([]);
  const [emails, setEmails] = useState<Email[]>([]);
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [sessionId] = useState<string>(() => `web-${Math.random().toString(36).slice(2, 10)}`);

  // UI Action State
  const [emailComposeModal, setEmailComposeModal] = useState({
    isOpen: false,
    to: '',
    subject: '',
    body: ''
  });

  // User profile state
  const [userAvatar, setUserAvatarState] = useState<string>(() => {
    try {
      return localStorage.getItem('userAvatar') || '';
    } catch {
      return '';
    }
  });

  const [userName, setUserNameState] = useState<string>(() => {
    try {
      return localStorage.getItem('userName') || 'User';
    } catch {
      return 'User';
    }
  });

  // EmoBot avatar state
  const [emobotAvatar, setEmobotAvatarState] = useState<string>(() => {
    try {
      return localStorage.getItem('emobotAvatar') || '/emobot-cat-avatar.png';
    } catch {
      return '/emobot-cat-avatar.png';
    }
  });

  const [emobotName, setEmobotNameState] = useState<string>(() => {
    try {
      return localStorage.getItem('emobotName') || 'EmoBot';
    } catch {
      return 'EmoBot';
    }
  });

  // Sync with backend on mount
  useEffect(() => {
    syncWithBackend();
  }, []);

  const syncWithBackend = async () => {
    try {
      // Fetch calendar events from backend
      const calendarResponse = await calendarApi.getEvents();
      if (calendarResponse.success && calendarResponse.events) {
        // Transform backend events to match frontend format
        const transformedEvents = calendarResponse.events.map((event: any) => {
          // Extract date from various possible formats
          let eventDate = event.date;

          // If no date field, try to extract from start_time or start
          if (!eventDate) {
            const startTime = event.start_time || event.start || event.datetime;
            if (startTime) {
              // If it's an ISO datetime string, extract the date part
              if (typeof startTime === 'string' && startTime.includes('T')) {
                eventDate = startTime.split('T')[0];
              } else if (typeof startTime === 'string' && startTime.match(/^\d{4}-\d{2}-\d{2}/)) {
                eventDate = startTime.substring(0, 10);
              }
            }
          }

          // Extract time from start_time
          let eventTime = event.time || '00:00';
          if (!event.time) {
            const startTime = event.start_time || event.start || event.datetime;
            if (startTime && typeof startTime === 'string') {
              // Extract time from ISO datetime or time string
              if (startTime.includes('T')) {
                const timePart = startTime.split('T')[1];
                eventTime = timePart ? timePart.substring(0, 5) : '00:00';
              } else if (startTime.match(/^\d{2}:\d{2}/)) {
                eventTime = startTime.substring(0, 5);
              }
            }
          }

          return {
            id: event.id || Date.now().toString(),
            title: event.title || event.summary || 'Untitled Event',
            time: eventTime,
            duration: event.duration || '1 hour',
            type: event.type || 'meeting',
            description: event.description || event.details || '',
            date: eventDate || formatDateLocal(new Date())
          };
        });
        setAllEvents(transformedEvents);
      }
    } catch (error) {
      console.log('Calendar sync failed, using local data:', error);
    }

    try {
      // Fetch inbox emails first, then sent emails sequentially to avoid overwhelming the server
      const allEmails: any[] = [];

      // Fetch inbox emails
      try {
        const emailResponse = await emailApi.listEmails();
        if (emailResponse.success && emailResponse.emails) {
          allEmails.push(...emailResponse.emails);
        }
      } catch (error) {
        console.log('Inbox email fetch failed:', error);
      }

      // Fetch sent emails separately
      try {
        const sentEmailResponse = await emailApi.listSentEmails();
        if (sentEmailResponse.success && sentEmailResponse.emails) {
          allEmails.push(...sentEmailResponse.emails);
        }
      } catch (error) {
        console.log('Sent email fetch failed:', error);
      }

      if (allEmails.length > 0) {
        // Transform backend email format to frontend format
        const transformedEmails = allEmails.map((email: any) => {
          // Parse sender from "Name <email@example.com>" format
          const fromField = email.from || email.sender || '';
          let senderName = fromField;
          let senderEmail = '';

          // Extract name and email from "Name <email>" format
          const emailMatch = fromField.match(/^(.+?)\s*<(.+?)>$/);
          if (emailMatch) {
            senderName = emailMatch[1].trim();
            senderEmail = emailMatch[2].trim();
          } else if (fromField.includes('@')) {
            senderEmail = fromField;
            senderName = fromField.split('@')[0];
          }

          // Parse date to readable format
          let timestamp = email.timestamp || email.date || '';
          if (email.date && !email.timestamp) {
            // Convert Gmail date format to relative time
            try {
              const emailDate = new Date(email.date);
              const now = new Date();
              const diffMs = now.getTime() - emailDate.getTime();
              const diffMins = Math.floor(diffMs / 60000);
              const diffHours = Math.floor(diffMs / 3600000);
              const diffDays = Math.floor(diffMs / 86400000);

              if (diffMins < 60) {
                timestamp = `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
              } else if (diffHours < 24) {
                timestamp = `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
              } else if (diffDays < 7) {
                timestamp = `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
              } else {
                timestamp = emailDate.toLocaleDateString();
              }
            } catch (e) {
              timestamp = email.date;
            }
          }

          return {
            id: email.id || Date.now().toString(),
            sender: senderName || 'Unknown Sender',
            senderEmail: senderEmail || '',
            subject: email.subject || '(No Subject)',
            preview: email.snippet || email.preview || '',
            content: email.body || email.content || '',
            timestamp: timestamp,
            read: email.is_read !== undefined ? email.is_read : email.read !== false,
            starred: email.starred || false,
            important: email.important || false,
            folder: email.folder || 'inbox',
            tags: email.tags || []
          };
        });

        // Sort by internal date if available, otherwise by timestamp
        transformedEmails.sort((a: any, b: any) => {
          const aDate = a.internalDate || new Date(a.timestamp).getTime();
          const bDate = b.internalDate || new Date(b.timestamp).getTime();
          return Number(bDate) - Number(aDate);
        });

        setEmails(transformedEmails);
      }
    } catch (error) {
      console.log('Email sync failed, using local data:', error);
    }

    try {
      // Fetch todos from backend
      const todoResponse = await todoApi.listTodos();
      if (todoResponse.success && (todoResponse.tasks || todoResponse.todos)) {
        // Backend returns 'tasks', not 'todos'
        const backendTasks = todoResponse.tasks || todoResponse.todos;
        const transformedTasks = backendTasks.map((task: any) => ({
          ...task,
          dueDate: task.due_date || task.dueDate // Handle both snake_case and camelCase
        }));
        setTodos(transformedTasks);
      }
    } catch (error) {
      console.log('Todo sync failed, using local data:', error);
    }
  };

  const setUserAvatar = (url: string) => {
    setUserAvatarState(url);
    try {
      localStorage.setItem('userAvatar', url);
    } catch (error) {
      console.error('Failed to save user avatar to localStorage', error);
    }
  };

  const setUserName = (name: string) => {
    setUserNameState(name);
    try {
      localStorage.setItem('userName', name);
    } catch (error) {
      console.error('Failed to save user name to localStorage', error);
    }
  };

  const setEmobotAvatar = (url: string) => {
    setEmobotAvatarState(url);
    try {
      localStorage.setItem('emobotAvatar', url);
    } catch (error) {
      console.error('Failed to save emobot avatar to localStorage', error);
    }
  };

  const setEmobotName = (name: string) => {
    setEmobotNameState(name);
    try {
      localStorage.setItem('emobotName', name);
    } catch (error) {
      console.error('Failed to save emobot name to localStorage', error);
    }
  };

  // Derived state for today's events and upcoming events
  const todayEvents = allEvents.filter(event => {
    const today = formatDateLocal(new Date());
    return event.date === today;
  });

  const upcomingEvents = allEvents.filter(event => {
    const today = formatDateLocal(new Date());
    return event.date && event.date > today;
  }).slice(0, 5); // Limit to next 5 events

  const setTodayEvents = (events: CalendarEvent[]) => {
    const today = formatDateLocal(new Date());
    const otherEvents = allEvents.filter(event => event.date !== today);
    setAllEvents([...otherEvents, ...events]);
  };

  const setUpcomingEvents = (events: CalendarEvent[]) => {
    const today = formatDateLocal(new Date());
    const todayAndPastEvents = allEvents.filter(event => !event.date || event.date <= today);
    setAllEvents([...todayAndPastEvents, ...events]);
  };

  const markEmailAsRead = (emailId: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId ? { ...email, read: true } : email
    ));
  };

  const toggleEmailStar = (emailId: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId ? { ...email, starred: !email.starred } : email
    ));
  };

  const toggleEmailImportant = (emailId: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId ? { ...email, important: !email.important } : email
    ));
  };

  const deleteEmail = (emailId: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId ? { ...email, folder: 'trash' } : email
    ));
  };

  const archiveEmail = (emailId: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId ? { ...email, folder: 'archive' } : email
    ));
  };

  const restoreEmail = (emailId: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId ? { ...email, folder: 'inbox' } : email
    ));
  };

  const addEmail = async (email: Omit<Email, 'id'>) => {
    const newEmail: Email = {
      ...email,
      id: Date.now().toString(),
      timestamp: 'Just now',
      read: true, // Sent emails are marked as read
    };

    // Optimistically update UI
    setEmails(prev => [newEmail, ...prev]);

    // Sync with backend if it's being sent
    if (email.folder === 'sent' || !email.folder) {
      try {
        await emailApi.sendEmail({
          to: email.senderEmail,
          subject: email.subject,
          body: email.content || email.preview
        });
      } catch (error) {
        console.error('Failed to send email via backend:', error);
      }
    }
  };

  const addTagToEmail = (emailId: string, tag: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId
        ? { ...email, tags: [...(email.tags || []), tag].filter((t, index, arr) => arr.indexOf(t) === index) }
        : email
    ));
  };

  const removeTagFromEmail = (emailId: string, tag: string) => {
    setEmails(prev => prev.map(email =>
      email.id === emailId
        ? { ...email, tags: (email.tags || []).filter(t => t !== tag) }
        : email
    ));
  };

  const toggleTodoComplete = (todoId: string) => {
    setTodos(prev => prev.map(todo =>
      todo.id === todoId ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const toggleTodoStar = (todoId: string) => {
    setTodos(prev => prev.map(todo =>
      todo.id === todoId ? { ...todo, starred: !todo.starred } : todo
    ));
  };

  const addTodo = async (todo: Omit<TodoItem, 'id'>) => {
    const newTodo = { ...todo, id: Date.now().toString() };

    // Optimistically update UI
    setTodos(prev => [...prev, newTodo]);

    // Sync with backend
    try {
      const response = await todoApi.addTodo({
        title: todo.title,
        description: todo.description,
        priority: todo.priority,
        category: todo.category,
        due_date: todo.dueDate
      });

      if (response.success) {
        // Refresh todos from backend to get the actual stored todo
        const todoResponse = await todoApi.listTodos();
        if (todoResponse.success && todoResponse.tasks) {
          const backendTasks = todoResponse.tasks;
          const transformedTasks = backendTasks.map((task: any) => ({
            ...task,
            dueDate: task.due_date || task.dueDate
          }));
          setTodos(transformedTasks);
        }
      }
    } catch (error) {
      console.error('Failed to sync todo with backend:', error);
      // Keep the optimistic update if backend fails
    }
  };

  const updateTodo = (todoId: string, updates: Partial<TodoItem>) => {
    setTodos(prev => prev.map(todo =>
      todo.id === todoId ? { ...todo, ...updates } : todo
    ));
  };

  const deleteTodo = (todoId: string) => {
    setTodos(prev => prev.filter(todo => todo.id !== todoId));
  };

  const addSubtask = (projectId: string, subtask: Omit<TodoItem, 'id'>) => {
    const newSubtask = {
      ...subtask,
      id: Date.now().toString(),
      parentId: projectId,
      isProject: false
    };

    setTodos(prev => {
      // Add the subtask
      const updatedTodos = [...prev, newSubtask];

      // Update the project to include this subtask ID
      return updatedTodos.map(todo =>
        todo.id === projectId
          ? { ...todo, subtasks: [...(todo.subtasks || []), newSubtask.id] }
          : todo
      );
    });
  };

  const getSubtasks = (projectId: string) => {
    const project = todos.find(todo => todo.id === projectId);
    if (!project || !project.subtasks) return [];

    return todos.filter(todo => project.subtasks?.includes(todo.id));
  };

  // Calendar CRUD operations
  const addEvent = async (event: Omit<CalendarEvent, 'id'>) => {
    const newEvent: CalendarEvent = {
      ...event,
      id: Date.now().toString(),
      date: event.date || formatDateLocal(new Date())
    };

    // Optimistically update UI
    setAllEvents(prev => [...prev, newEvent]);

    // Sync with backend
    try {
      const response = await calendarApi.createEvent({
        title: event.title,
        time: event.time,
        duration: event.duration,
        description: event.description
      });

      if (response.success) {
        // Refresh events from backend to get the actual Google Calendar event
        const calendarResponse = await calendarApi.getEvents();
        if (calendarResponse.success && calendarResponse.events) {
          const transformedEvents = calendarResponse.events.map((evt: any) => {
            // Extract date from various possible formats
            let eventDate = evt.date;

            if (!eventDate) {
              const startTime = evt.start_time || evt.start || evt.datetime;
              if (startTime) {
                if (typeof startTime === 'string' && startTime.includes('T')) {
                  eventDate = startTime.split('T')[0];
                } else if (typeof startTime === 'string' && startTime.match(/^\d{4}-\d{2}-\d{2}/)) {
                  eventDate = startTime.substring(0, 10);
                }
              }
            }

            // Extract time from start_time
            let eventTime = evt.time || '00:00';
            if (!evt.time) {
              const startTime = evt.start_time || evt.start || evt.datetime;
              if (startTime && typeof startTime === 'string') {
                if (startTime.includes('T')) {
                  const timePart = startTime.split('T')[1];
                  eventTime = timePart ? timePart.substring(0, 5) : '00:00';
                } else if (startTime.match(/^\d{2}:\d{2}/)) {
                  eventTime = startTime.substring(0, 5);
                }
              }
            }

            return {
              id: evt.id || Date.now().toString(),
              title: evt.title || evt.summary || 'Untitled Event',
              time: eventTime,
              duration: evt.duration || '1 hour',
              type: evt.type || 'meeting',
              description: evt.description || evt.details || '',
              date: eventDate || formatDateLocal(new Date())
            };
          });
          setAllEvents(transformedEvents);
        }
      }
    } catch (error) {
      console.error('Failed to sync event with backend:', error);
      // Keep the optimistic update if backend fails
    }
  };

  const updateEvent = (updatedEvent: CalendarEvent) => {
    setAllEvents(prev => prev.map(event =>
      event.id === updatedEvent.id ? updatedEvent : event
    ));
  };

  const deleteEvent = (eventId: string) => {
    setAllEvents(prev => prev.filter(event => event.id !== eventId));
  };

  const getEventsForDate = (date: Date) => {
    const dateString = formatDateLocal(date);
    return allEvents.filter(event => event.date === dateString);
  };

  // Helper function to convert time string to minutes since midnight
  const timeToMinutes = (timeStr: string): number => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
  };

  // Helper function to convert duration to minutes
  const durationToMinutes = (durationStr: string): number => {
    if (durationStr.includes('hour')) {
      const hours = parseFloat(durationStr);
      return hours * 60;
    } else if (durationStr.includes('min')) {
      return parseInt(durationStr);
    } else if (durationStr === 'All day') {
      return 24 * 60; // All day = 1440 minutes
    }
    return 60; // Default to 1 hour
  };

  // Detect time conflicts between events
  const detectConflicts = (events: CalendarEvent[]) => {
    const conflicts: { eventId: string; conflictsWith: string[] }[] = [];

    for (let i = 0; i < events.length; i++) {
      const event1 = events[i];
      const start1 = timeToMinutes(event1.time);
      const end1 = start1 + durationToMinutes(event1.duration);

      const conflictsWith: string[] = [];

      for (let j = 0; j < events.length; j++) {
        if (i === j) continue;

        const event2 = events[j];
        const start2 = timeToMinutes(event2.time);
        const end2 = start2 + durationToMinutes(event2.duration);

        // Check if events overlap
        if (start1 < end2 && start2 < end1) {
          conflictsWith.push(event2.id);
        }
      }

      if (conflictsWith.length > 0) {
        conflicts.push({
          eventId: event1.id,
          conflictsWith
        });
      }
    }

    return conflicts;
  };

  const getCalendarSummary = () => {
    const nextEvent = todayEvents.length > 0
      ? `${todayEvents[0].title} at ${todayEvents[0].time}`
      : upcomingEvents.length > 0
        ? `${upcomingEvents[0].title} ${upcomingEvents[0].time}`
        : 'No upcoming events';

    return {
      todayEvents: todayEvents.length,
      upcomingEvents: upcomingEvents.length,
      nextEvent
    };
  };

  const getEmailSummary = () => {
    const unreadEmails = emails.filter(email => !email.read).length;
    const priorityEmails = emails.filter(email => email.important).length;
    const recentUnread = emails.find(email => !email.read);

    return {
      unreadEmails,
      totalEmails: emails.length,
      recentSender: recentUnread?.sender || 'No unread emails',
      priority: priorityEmails
    };
  };

  const getTodoSummary = () => {
    const completedTasks = todos.filter(todo => todo.completed).length;
    const totalTasks = todos.length;
    const pendingTasks = totalTasks - completedTasks;
    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    return {
      totalTasks,
      completedTasks,
      pendingTasks,
      completionRate
    };
  };

  // Chat message functions
  const addChatMessage = async (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: generateMessageId(),
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, newMessage]);

    if (message.sender !== 'user') {
      return;
    }

    const pendingId = generateMessageId();
    const pendingMessage: ChatMessage = {
      id: pendingId,
      content: 'Thinking...',
      sender: 'bot',
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, pendingMessage]);

    try {
      const response = await reasoningApi.submitRequest({
        user_request: message.content,
        session_id: sessionId,
        context_data: {
          source: 'web_chat',
          timestamp: new Date().toISOString()
        }
      });

      console.log('🔍 Full API Response:', JSON.stringify(response, null, 2));

      // Extract reasoning steps and final answer
      const reasoningSteps: ReasoningStep[] = (response.raw_response?.reasoning_steps || []).map((step: any) => ({
        ...step,
        type: step.type || 'action'
      }));
      let botText = response.raw_response?.response || 'No response received.';

      // Handle UI Actions
      if (response.raw_response?.ui_action) {
        const uiAction = response.raw_response.ui_action;
        if (uiAction.type === 'open_email_draft') {
          setEmailComposeModal({
            isOpen: true,
            to: uiAction.data.recipient || '',
            subject: uiAction.data.subject || '',
            body: uiAction.data.body || ''
          });
        }
      }

      // Extract clean, concise answer from verbose response
      // Remove all the reasoning markers and metadata
      let cleanText = botText;

      // Remove common reasoning patterns
      // DISABLED: Causing issues with demo responses containing markdown
      /*
      cleanText = cleanText.replace(/\*\*Thought\*\*:.*?(?=\*\*|$)/gs, '');
      cleanText = cleanText.replace(/\*\*Action\*\*:.*?(?=\*\*|$)/gs, '');
      cleanText = cleanText.replace(/\*\*Observation\*\*:.*?(?=\*\*|$)/gs, '');
      cleanText = cleanText.replace(/\*\*Summary:\*\*.*?(?=\*\*|$)/gs, '');
      cleanText = cleanText.replace(/\*\*Key Points:\*\*.*?(?=\*\*|$)/gs, '');
      cleanText = cleanText.replace(/\*\*Sources for More Details:\*\*.*?$/gs, '');

      // Look for "Final Answer:" pattern
      const finalAnswerMatch = cleanText.match(/(?:\*\*)?Final Answer(?:\*\*)?:\s*(.+?)(?:\n\n|$)/s);
      if (finalAnswerMatch) {
        cleanText = finalAnswerMatch[1].trim();
      }
      */

      // Clean up extra whitespace and newlines
      cleanText = cleanText.replace(/\n{3,}/g, '\n\n').trim();

      // If still too long or contains metadata, extract first meaningful paragraph
      // DISABLED: This was too aggressive and truncated valid structured responses (e.g. demo scenarios)
      /*
      if (cleanText.length > 500 || cleanText.includes('**') || cleanText.includes('💡')) {
        const sentences = cleanText.split(/[.!?]+/).filter(s => s.trim().length > 20);
        // Take first 2-3 sentences that don't contain metadata markers
        const goodSentences = sentences.filter(s =>
          !s.includes('**') &&
          !s.includes('💡') &&
          !s.includes('[Search Information]') &&
          !s.includes('http')
        ).slice(0, 3);

        if (goodSentences.length > 0) {
          cleanText = goodSentences.join('. ').trim() + '.';
        }
      }
      */

      botText = cleanText || botText; // Fallback to original if cleaning failed

      console.log('📬 Bot response:', botText);
      console.log('🧠 Reasoning steps:', reasoningSteps.length);

      setChatMessages(prev =>
        prev.map(chat =>
          chat.id === pendingId
            ? {
              ...chat,
              content: botText,
              timestamp: new Date(),
              reasoningSteps: reasoningSteps
            }
            : chat
        )
      );

      // Refresh data (todos, calendar, emails) to reflect any actions taken by the agent
      await syncWithBackend();
    } catch (error) {
      console.error('Failed to fetch bot response', error);
      setChatMessages(prev =>
        prev.map(chat =>
          chat.id === pendingId
            ? {
              ...chat,
              content: 'Sorry, something went wrong. Please try again in a moment.'
            }
            : chat
        )
      );
    }
  };

  const clearChatMessages = () => {
    setChatMessages([]);
  };

  const value: DataContextType = {
    // Calendar
    todayEvents,
    upcomingEvents,
    allEvents,
    setTodayEvents,
    setUpcomingEvents,
    addEvent,
    updateEvent,
    deleteEvent,
    getEventsForDate,
    detectConflicts,

    // Email
    emails,
    setEmails,
    markEmailAsRead,
    toggleEmailStar,
    toggleEmailImportant,
    deleteEmail,
    archiveEmail,
    restoreEmail,
    addEmail,
    addTagToEmail,
    removeTagFromEmail,

    // Todos
    todos,
    setTodos,
    toggleTodoComplete,
    toggleTodoStar,
    addTodo,
    updateTodo,
    deleteTodo,
    addSubtask,
    getSubtasks,

    // Avatar/Profile
    userAvatar,
    setUserAvatar,
    userName,
    setUserName,
    emobotAvatar,
    setEmobotAvatar,
    emobotName,
    setEmobotName,

    // Chat Messages
    chatMessages,
    addChatMessage,
    clearChatMessages,

    // Summaries
    getCalendarSummary,
    getEmailSummary,
    getTodoSummary,

    // UI Actions
    emailComposeModal,
    setEmailComposeModal
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};
