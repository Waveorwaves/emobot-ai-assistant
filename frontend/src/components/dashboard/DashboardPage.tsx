import React, { useState } from 'react';
import {
  Brain,
  Lightbulb,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Calendar,
  Mail,
  CheckSquare,
  TrendingUp,
  Bot,
  Sparkles,
  Target,
  Activity,
  History,
  Trash2,
  X,
  Send
} from 'lucide-react';
import Sidebar from '../ui/Sidebar';
import ChatBox from '../ui/ChatBox';
import Notification from '../ui/Notification';
import { useData } from '../../context/DataContext';

interface DashboardPageProps {
  onNavigate?: (page: string) => void;
}

interface AIInsight {
  id: string;
  type: 'urgent' | 'suggestion' | 'optimization' | 'conflict';
  title: string;
  description: string;
  action?: string;
  actionType?: 'primary' | 'secondary';
  priority: 'high' | 'medium' | 'low';
}

interface AIAction {
  id: string;
  type: 'email' | 'calendar' | 'task';
  description: string;
  count: number;
  status: 'completed' | 'in-progress' | 'pending';
}

interface ApprovalItem {
  id: string;
  type: 'reschedule' | 'priority' | 'automation';
  title: string;
  description: string;
  impact: string;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [insights, setInsights] = useState<any[]>(() => {
    try {
      const saved = localStorage.getItem('cachedInsights');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [insightsSummary, setInsightsSummary] = useState<any>(() => {
    try {
      const saved = localStorage.getItem('cachedInsightsSummary');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [insightStates, setInsightStates] = useState<Record<string, any>>(() => {
    try {
      const saved = localStorage.getItem('insightStates');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });
  const [notification, setNotification] = useState<{message: string; type: 'success' | 'error' | 'info' | 'warning'} | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [historyFilter, setHistoryFilter] = useState<string>('all');
  const [insightEmailDrafts, setInsightEmailDrafts] = useState<Record<number, any>>({});
  const [showComposeModal, setShowComposeModal] = useState(false);
  const [composeForm, setComposeForm] = useState({
    to: '',
    subject: '',
    content: ''
  });
  const [showCalendarConfirmation, setShowCalendarConfirmation] = useState(false);
  const [calendarEventData, setCalendarEventData] = useState<any>(null);
  
  // Get real data from context
  const { getCalendarSummary, getEmailSummary, getTodoSummary, todos, emails } = useData();
  
  // Real summary data
  const calendarSummary = getCalendarSummary();
  const todoSummary = getTodoSummary();
  const emailSummary = getEmailSummary();

  // AI insights and recommendations - will be populated from backend/Gemini API
  const aiInsights: AIInsight[] = [];

  const [aiActions, setAiActions] = useState<AIAction[]>([]);
  const [approvalItems, setApprovalItems] = useState<ApprovalItem[]>([]);
  const [isOptimizing, setIsOptimizing] = useState(false);

  // Helper function to create insight hash
  const getInsightHash = (insight: any) => {
    return `${insight.title}-${insight.type}`.replace(/\s+/g, '-').toLowerCase();
  };

  // Notification helper
  const showNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    setNotification({ message, type });
  };

  // Save insight states to localStorage
  const saveInsightStates = (states: Record<string, any>) => {
    try {
      localStorage.setItem('insightStates', JSON.stringify(states));
      setInsightStates(states);
    } catch (error) {
      console.error('Error saving insight states:', error);
    }
  };

  // Auto-refresh insights on page load if they're stale (older than 5 minutes)
  React.useEffect(() => {
    const checkAndRefreshInsights = () => {
      try {
        const lastRefresh = localStorage.getItem('insightsLastRefresh');
        const now = Date.now();
        const fiveMinutes = 5 * 60 * 1000;

        // If no last refresh time or it's been more than 5 minutes, refresh
        if (!lastRefresh || (now - parseInt(lastRefresh)) > fiveMinutes) {
          console.log('🔄 Insights are stale, auto-refreshing...');
          analyzeInsights();
          localStorage.setItem('insightsLastRefresh', now.toString());
        } else {
          console.log('✅ Using cached insights (still fresh)');
        }
      } catch (error) {
        console.error('Error checking insights freshness:', error);
      }
    };

    // Only run on initial mount
    checkAndRefreshInsights();

    // Also fetch schedule optimization data
    fetchScheduleData();
  }, []); // Empty dependency array = run once on mount

  // Fetch schedule optimization data
  const fetchScheduleData = async () => {
    try {
      const [actionsRes, approvalsRes] = await Promise.all([
        fetch('http://localhost:8000/api/schedule/actions'),
        fetch('http://localhost:8000/api/schedule/approvals')
      ]);

      const actionsData = await actionsRes.json();
      const approvalsData = await approvalsRes.json();

      if (actionsData.success) {
        setAiActions(actionsData.actions || []);
      }

      if (approvalsData.success) {
        setApprovalItems(approvalsData.approvals || []);
      }
    } catch (error) {
      console.error('Error fetching schedule data:', error);
    }
  };

  // Optimize schedule
  const optimizeSchedule = async () => {
    setIsOptimizing(true);
    try {
      const response = await fetch('http://localhost:8000/api/schedule/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();

      if (data.success) {
        setAiActions(data.actions || []);
        setApprovalItems(data.approvals || []);
        showNotification(`✓ Found ${data.summary.total_approvals} optimization opportunities`, 'success');
      } else {
        showNotification('Failed to optimize schedule', 'error');
      }
    } catch (error) {
      console.error('Error optimizing schedule:', error);
      showNotification('Failed to optimize schedule', 'error');
    } finally {
      setIsOptimizing(false);
    }
  };

  // Analyze insights function
  const analyzeInsights = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/insights/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      
      if (data.success) {
        // Filter out completed and snoozed insights
        const now = Date.now();
        const filteredInsights = (data.insights || []).filter((insight: any) => {
          const hash = getInsightHash(insight);
          const state = insightStates[hash];
          
          // Skip if completed
          if (state && state.status === 'completed') {
            return false;
          }
          
          // Skip if snoozed and not yet time
          if (state && state.status === 'snoozed' && state.snoozeUntil > now) {
            return false;
          }
          
          return true;
        });
        
        setInsights(filteredInsights);
        
        // Update summary with actual filtered count
        const updatedSummary = {
          ...(data.summary || {}),
          insights_count: filteredInsights.length
        };
        setInsightsSummary(updatedSummary);
        
        // Cache insights and summary to localStorage
        try {
          localStorage.setItem('cachedInsights', JSON.stringify(filteredInsights));
          localStorage.setItem('cachedInsightsSummary', JSON.stringify(updatedSummary));
          localStorage.setItem('insightsLastRefresh', Date.now().toString());
        } catch (error) {
          console.error('Error caching insights:', error);
        }
      }
    } catch (error) {
      console.error('Error analyzing insights:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Mark insight as complete
  const markInsightComplete = (index: number) => {
    const insight = insights[index];
    if (!insight) return;

    const hash = getInsightHash(insight);
    const newStates = {
      ...insightStates,
      [hash]: {
        status: 'completed',
        timestamp: Date.now(),
        completedAt: new Date().toISOString(),
        title: insight.title || 'Insight',
        content: insight.content || '',
        suggestion: insight.suggestion || ''
      }
    };

    saveInsightStates(newStates);

    // Remove from display and update cache
    const newInsights = insights.filter((_, i) => i !== index);
    setInsights(newInsights);

    // Update summary count
    if (insightsSummary) {
      const updatedSummary = {
        ...insightsSummary,
        insights_count: newInsights.length
      };
      setInsightsSummary(updatedSummary);
      try {
        localStorage.setItem('cachedInsightsSummary', JSON.stringify(updatedSummary));
      } catch (error) {
        console.error('Error updating cached summary:', error);
      }
    }

    try {
      localStorage.setItem('cachedInsights', JSON.stringify(newInsights));
    } catch (error) {
      console.error('Error updating cached insights:', error);
    }

    // Show notification
    showNotification('✓ Insight marked as complete', 'success');
  };

  // Mark insight as not useful
  const markInsightNotUseful = (index: number) => {
    const insight = insights[index];
    if (!insight) return;

    const hash = getInsightHash(insight);
    const newStates = {
      ...insightStates,
      [hash]: {
        status: 'not_useful',
        timestamp: Date.now(),
        markedAt: new Date().toISOString(),
        title: insight.title || 'Insight',
        content: insight.content || '',
        suggestion: insight.suggestion || ''
      }
    };

    saveInsightStates(newStates);

    // Remove from display and update cache
    const newInsights = insights.filter((_, i) => i !== index);
    setInsights(newInsights);

    // Update summary count
    if (insightsSummary) {
      const updatedSummary = {
        ...insightsSummary,
        insights_count: newInsights.length
      };
      setInsightsSummary(updatedSummary);
      try {
        localStorage.setItem('cachedInsightsSummary', JSON.stringify(updatedSummary));
      } catch (error) {
        console.error('Error updating cached summary:', error);
      }
    }

    try {
      localStorage.setItem('cachedInsights', JSON.stringify(newInsights));
    } catch (error) {
      console.error('Error updating cached insights:', error);
    }

    // Show notification
    showNotification('✗ Insight marked as not useful', 'info');
  };

  // Snooze insight
  const snoozeInsight = (index: number) => {
    const insight = insights[index];
    if (!insight) return;

    // Snooze for 1 hour
    const snoozeUntil = Date.now() + (60 * 60 * 1000);

    const hash = getInsightHash(insight);
    const newStates = {
      ...insightStates,
      [hash]: {
        status: 'snoozed',
        snoozeUntil: snoozeUntil,
        timestamp: Date.now(),
        snoozedAt: new Date().toISOString(),
        title: insight.title || 'Insight',
        content: insight.content || '',
        suggestion: insight.suggestion || ''
      }
    };

    saveInsightStates(newStates);

    // Remove from display and update cache
    const newInsights = insights.filter((_, i) => i !== index);
    setInsights(newInsights);

    // Update summary count
    if (insightsSummary) {
      const updatedSummary = {
        ...insightsSummary,
        insights_count: newInsights.length
      };
      setInsightsSummary(updatedSummary);
      try {
        localStorage.setItem('cachedInsightsSummary', JSON.stringify(updatedSummary));
      } catch (error) {
        console.error('Error updating cached summary:', error);
      }
    }

    try {
      localStorage.setItem('cachedInsights', JSON.stringify(newInsights));
    } catch (error) {
      console.error('Error updating cached insights:', error);
    }

    // Show notification
    showNotification('⏰ Insight snoozed for 1 hour', 'info');
  };

  // View insight history
  const viewInsightHistory = () => {
    setShowHistory(true);
  };

  // Clear insight history
  const clearInsightHistory = () => {
    if (confirm('Are you sure you want to clear all insight history?')) {
      try {
        localStorage.removeItem('insightStates');
        setInsightStates({});
        showNotification('🗑️ History cleared', 'success');
        setShowHistory(false);
      } catch (error) {
        console.error('Error clearing history:', error);
        showNotification('Failed to clear history', 'error');
      }
    }
  };

  const getInsightTypeClass = (type: string) => {
    switch (type) {
      case 'warning': return 'bg-yellow-900/20 border-yellow-500';
      case 'error': return 'bg-red-900/20 border-red-500';
      case 'success': return 'bg-green-900/20 border-green-500';
      default: return 'bg-blue-900/20 border-blue-500';
    }
  };

  const getInsightTypeIcon = (type: string) => {
    switch (type) {
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'success': return '✅';
      default: return '💡';
    }
  };

  // Helper function to clean LLM thought process from email body
  const cleanEmailBody = (body: string): string => {
    if (!body) return '';

    // Remove everything before and including "**Action**:" or similar markers
    let cleaned = body;

    // Pattern 1: Remove **Thought**: ... **Action**: sections
    cleaned = cleaned.replace(/\*\*Thought\*\*:[\s\S]*?\*\*Action\*\*:\s*/gi, '');

    // Pattern 2: Remove ```json ... ``` blocks
    cleaned = cleaned.replace(/```json[\s\S]*?```/g, '');

    // Pattern 3: Remove any remaining **Thought** or **Action** markers
    cleaned = cleaned.replace(/\*\*(?:Thought|Action)\*\*:\s*/gi, '');

    // Trim whitespace
    cleaned = cleaned.trim();

    return cleaned;
  };

  // Handle email reply with auto-draft generation
  const handleReplyEmail = async (insight: any, index: number) => {
    console.log('Handling email reply for insight:', insight);
    console.log('Full insight object:', JSON.stringify(insight, null, 2));

    try {
      // Use sender_email from insight if available, otherwise try to extract
      let recipient = insight.sender_email || '';

      // Fallback: Extract recipient email from insight content if not provided
      if (!recipient) {
        const combined = (insight.content || '') + ' ' + (insight.suggestion || '') + ' ' + (insight.title || '');
        console.log('Combined text for email extraction:', combined);

        // Try multiple patterns to extract email
        // Pattern 1: Look for "from <email>" pattern
        const fromPattern = combined.match(/from\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i);
        if (fromPattern) {
          recipient = fromPattern[1];
        }

        // Pattern 2: Look for any email address if pattern 1 fails
        if (!recipient) {
          const emailPattern = combined.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
          if (emailPattern) {
            recipient = emailPattern[1];
          }
        }

        // Pattern 3: Extract sender name and use DataContext to look up email
        if (!recipient) {
          // Try to extract sender name (e.g., "Jason Huang requesting" -> "Jason Huang")
          const namePattern = combined.match(/(?:from|received.*from|email from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i);
          if (namePattern) {
            const senderName = namePattern[1];
            console.log('Extracted sender name:', senderName);

            // Look up email in context
            const senderEmail = emails.find(email =>
              email.sender.toLowerCase().includes(senderName.toLowerCase())
            );

            if (senderEmail) {
              // Extract email from sender field (format: "Name <email@domain.com>" or just "email@domain.com")
              const emailMatch = senderEmail.sender.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
              if (emailMatch) {
                recipient = emailMatch[1];
                console.log('Found email from context:', recipient);
              }
            }
          }
        }
      }

      console.log('Extracted recipient:', recipient);

      if (!recipient) {
        showNotification('❌ Could not extract sender email from insight', 'error');
        return;
      }

      showNotification('⏳ Generating email draft...', 'info');

      // Call generate-reply API
      const response = await fetch('http://localhost:8000/api/insights/generate-reply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipient: recipient,
          context: insight.content,
          suggestion: insight.suggestion || ''
        })
      });

      const data = await response.json();
      console.log('API response:', JSON.stringify(data, null, 2));

      if (data.success) {
        // Determine recipient - use extracted email if API doesn't provide one
        const finalRecipient = recipient || data.recipient || data.to;

        // Clean the email body from thought process
        let cleanedBody = cleanEmailBody(data.body || data.content || '');

        console.log('Final recipient for draft:', finalRecipient);
        console.log('Raw body from API:', data.body);
        console.log('Cleaned email body:', cleanedBody);

        // Fallback: if body is empty after cleaning, generate a simple confirmation
        if (!cleanedBody || cleanedBody.trim().length === 0) {
          console.warn('Email body was empty after cleaning, using fallback');
          cleanedBody = `Dear ${recipient.split('@')[0]},\n\nThank you for your email. I confirm my availability for the meeting on the proposed date and time.\n\nLooking forward to it.\n\nBest regards`;
        }

        // Store draft preview in state to display in insight
        setInsightEmailDrafts(prev => ({
          ...prev,
          [index]: {
            to: finalRecipient,
            subject: data.subject || 'Re: Meeting Request',
            body: cleanedBody
          }
        }));

        // Set compose form and open modal on dashboard
        setComposeForm({
          to: finalRecipient,
          subject: data.subject || 'Re: Meeting Request',
          content: cleanedBody
        });
        setShowComposeModal(true);

        showNotification('✓ Email draft ready!', 'success');
      } else {
        console.error('Failed to generate email draft:', data.error);
        showNotification('❌ Failed to generate email: ' + (data.error || 'Unknown error'), 'error');
      }
    } catch (error) {
      console.error('Error generating email reply:', error);
      showNotification('❌ Failed to generate email: ' + error, 'error');
    }
  };

  // Handle sending email from dashboard
  const handleSendEmail = async () => {
    if (!composeForm.to.trim() || !composeForm.subject.trim() || !composeForm.content.trim()) {
      showNotification('❌ Please fill in all fields', 'error');
      return;
    }

    try {
      showNotification('⏳ Sending email...', 'info');

      const response = await fetch('http://localhost:8000/api/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to: composeForm.to,
          subject: composeForm.subject,
          body: composeForm.content
        })
      });

      const data = await response.json();

      if (data.success) {
        showNotification('✅ Email sent successfully!', 'success');
        setShowComposeModal(false);
        setComposeForm({ to: '', subject: '', content: '' });
      } else {
        showNotification('❌ Failed to send email: ' + (data.error || 'Unknown error'), 'error');
      }
    } catch (error) {
      console.error('Error sending email:', error);
      showNotification('❌ Failed to send email: ' + error, 'error');
    }
  };

  // Handle confirm button - automates email reply and calendar scheduling
  const handleConfirmAction = async (insight: any, index: number) => {
    try {
      // Step 1: Extract email recipient
      let recipient = insight.sender_email || '';

      if (!recipient) {
        const combined = (insight.content || '') + ' ' + (insight.suggestion || '') + ' ' + (insight.title || '');
        const fromPattern = combined.match(/from\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i);
        if (fromPattern) {
          recipient = fromPattern[1];
        } else {
          const emailPattern = combined.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
          if (emailPattern) {
            recipient = emailPattern[1];
          } else {
            const namePattern = combined.match(/(?:from|received.*from|email from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i);
            if (namePattern) {
              const senderName = namePattern[1];
              const senderEmail = emails.find(email =>
                email.sender.toLowerCase().includes(senderName.toLowerCase())
              );
              if (senderEmail) {
                const emailMatch = senderEmail.sender.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
                if (emailMatch) {
                  recipient = emailMatch[1];
                }
              }
            }
          }
        }
      }

      if (!recipient) {
        showNotification('❌ Could not extract sender email', 'error');
        return;
      }

      showNotification('⏳ Generating email draft...', 'info');

      // Step 2: Generate email reply
      const emailResponse = await fetch('http://localhost:8000/api/insights/generate-reply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipient: recipient,
          context: insight.content,
          suggestion: insight.suggestion || ''
        })
      });

      const emailData = await emailResponse.json();

      if (!emailData.success) {
        showNotification('❌ Failed to generate email: ' + (emailData.error || 'Unknown error'), 'error');
        return;
      }

      const finalRecipient = recipient || emailData.recipient || emailData.to;
      let cleanedBody = cleanEmailBody(emailData.body || emailData.content || '');

      if (!cleanedBody || cleanedBody.trim().length === 0) {
        cleanedBody = `Dear ${recipient.split('@')[0]},\n\nThank you for your email. I confirm my availability for the meeting on the proposed date and time.\n\nLooking forward to it.\n\nBest regards`;
      }

      // Show compose modal first
      setComposeForm({
        to: finalRecipient,
        subject: emailData.subject || 'Re: Meeting Request',
        content: cleanedBody
      });
      setShowComposeModal(true);

      // Extract calendar event info from insight
      const combined = (insight.content || '') + ' ' + (insight.suggestion || '') + ' ' + (insight.title || '');

      // Extract date - look for patterns like "November 15th", "Nov 15", etc.
      const today = new Date();
      const defaultDate = today.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
      let extractedDate = defaultDate;

      const datePattern1 = combined.match(/(?:on|for|date:?)\s+([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?)/i);
      const datePattern2 = combined.match(/([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?)/i);

      if (datePattern1 && datePattern1[1]) {
        extractedDate = datePattern1[1];
      } else if (datePattern2 && datePattern2[1]) {
        extractedDate = datePattern2[1];
      }

      // Extract time
      let extractedTime = '1:30 PM';
      const timePattern = combined.match(/(\d{1,2}:\d{2}\s*(?:AM|PM))/i);
      if (timePattern && timePattern[1]) {
        extractedTime = timePattern[1];
      }

      // Extract duration
      let extractedDuration = '1 hour';
      const durationPattern = combined.match(/(?:for|about)\s+(?:an?\s+)?(\d+)\s*(hour|minute)/i);
      if (durationPattern) {
        extractedDuration = `${durationPattern[1]} ${durationPattern[2]}`;
      }

      console.log('Extracted calendar data:', { date: extractedDate, time: extractedTime, duration: extractedDuration });

      // Store calendar event data for later
      setCalendarEventData({
        title: insight.title || 'Meeting',
        date: extractedDate,
        time: extractedTime,
        duration: extractedDuration,
        recipient: finalRecipient,
        insightIndex: index
      });

      showNotification('✓ Email draft ready!', 'success');

    } catch (error) {
      console.error('Error in confirm action:', error);
      showNotification('❌ Failed to process action: ' + error, 'error');
    }
  };

  // Handle sending email and showing calendar confirmation
  const handleSendAndSchedule = async () => {
    if (!composeForm.to.trim() || !composeForm.subject.trim() || !composeForm.content.trim()) {
      showNotification('❌ Please fill in all fields', 'error');
      return;
    }

    try {
      showNotification('⏳ Sending email...', 'info');

      const response = await fetch('http://localhost:8000/api/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to: composeForm.to,
          subject: composeForm.subject,
          body: composeForm.content
        })
      });

      const data = await response.json();

      if (data.success) {
        showNotification('✅ Email sent successfully!', 'success');
        setShowComposeModal(false);

        // Track email sent in history if we have insight data
        if (calendarEventData && calendarEventData.insightIndex !== undefined) {
          const insight = insights[calendarEventData.insightIndex];
          if (insight) {
            const hash = getInsightHash(insight);
            const newStates = {
              ...insightStates,
              [hash]: {
                ...insightStates[hash],
                status: 'email_sent',
                timestamp: Date.now(),
                emailSentAt: new Date().toISOString(),
                title: insight.title || 'Insight',
                content: insight.content || '',
                suggestion: insight.suggestion || '',
                emailTo: composeForm.to,
                emailSubject: composeForm.subject
              }
            };
            saveInsightStates(newStates);
          }
        }

        // Show calendar confirmation instead of navigating
        setShowCalendarConfirmation(true);
      } else {
        showNotification('❌ Failed to send email: ' + (data.error || 'Unknown error'), 'error');
      }
    } catch (error) {
      console.error('Error sending email:', error);
      showNotification('❌ Failed to send email: ' + error, 'error');
    }
  };

  // Handle adding event to calendar
  const handleAddToCalendar = async () => {
    if (!calendarEventData) return;

    try {
      showNotification('⏳ Adding to calendar...', 'info');

      // Parse date and time into ISO format that the backend expects
      const eventDate = calendarEventData.date; // e.g., "November 15th at 1:30 PM" or just "November 15th"
      const eventTime = calendarEventData.time; // e.g., "1:30 PM"

      // Remove ordinal suffixes (st, nd, rd, th)
      const cleanDate = eventDate.replace(/(\d+)(st|nd|rd|th)/g, '$1');

      // Parse the date string
      const year = new Date().getFullYear();
      let dateTimeStr = '';

      // Check if time is already in the date string
      if (cleanDate.includes('at') || cleanDate.match(/\d{1,2}:\d{2}/)) {
        dateTimeStr = `${cleanDate} ${year}`;
      } else {
        // Combine date and time
        dateTimeStr = `${cleanDate}, ${year} at ${eventTime}`;
      }

      console.log('Parsed datetime string:', dateTimeStr);

      // Call calendar API to add event - use start_time instead of datetime
      const payload = {
        title: calendarEventData.title,
        start_time: dateTimeStr,  // Changed from 'datetime' to 'start_time'
        duration: calendarEventData.duration,
        description: calendarEventData.recipient ? `Attendees: ${calendarEventData.recipient}` : '',
        attendees: calendarEventData.recipient ? [calendarEventData.recipient] : []
      };

      console.log('Sending calendar request:', JSON.stringify(payload, null, 2));

      const response = await fetch('http://localhost:8000/api/calendar/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.success) {
        showNotification('✅ Event added to calendar!', 'success');

        // Track calendar added in history
        if (calendarEventData && calendarEventData.insightIndex !== undefined) {
          const insight = insights[calendarEventData.insightIndex];
          if (insight) {
            const hash = getInsightHash(insight);
            const currentState = insightStates[hash] || {};
            const newStates = {
              ...insightStates,
              [hash]: {
                ...currentState,
                status: 'calendar_added',
                timestamp: Date.now(),
                calendarAddedAt: new Date().toISOString(),
                title: insight.title || 'Insight',
                content: insight.content || '',
                suggestion: insight.suggestion || '',
                eventTitle: calendarEventData.title,
                eventDate: calendarEventData.date,
                eventTime: calendarEventData.time
              }
            };
            saveInsightStates(newStates);

            // Remove from active insights
            const newInsights = insights.filter((_, i) => i !== calendarEventData.insightIndex);
            setInsights(newInsights);

            // Update summary count
            if (insightsSummary) {
              const updatedSummary = {
                ...insightsSummary,
                insights_count: newInsights.length
              };
              setInsightsSummary(updatedSummary);
              try {
                localStorage.setItem('cachedInsightsSummary', JSON.stringify(updatedSummary));
                localStorage.setItem('cachedInsights', JSON.stringify(newInsights));
              } catch (error) {
                console.error('Error updating cached data:', error);
              }
            }
          }
        }

        setShowCalendarConfirmation(false);
        setCalendarEventData(null);
        setComposeForm({ to: '', subject: '', content: '' });

        // Refresh the page or trigger a calendar refresh
        // You might want to add a callback here to refresh calendar data
      } else {
        showNotification('❌ Failed to add to calendar: ' + (data.error || 'Unknown error'), 'error');
      }
    } catch (error) {
      console.error('Error adding to calendar:', error);
      showNotification('❌ Failed to add to calendar: ' + error, 'error');
    }
  };

  // Generate smart action buttons based on insight content
  const generateSmartActions = (insight: any, index: number) => {
    const actions = [];
    const content = (insight.content || '').toLowerCase();
    const suggestion = (insight.suggestion || '').toLowerCase();
    const title = (insight.title || '').toLowerCase();
    const combined = content + ' ' + suggestion + ' ' + title;

    // Detect if this is about email reply - only if there's a sender_email or it's clearly an email-specific insight
    const isEmailInsight = insight.sender_email ||
                          title.includes('email') && (combined.includes('reply') || combined.includes('respond') || combined.includes('from'));

    // Detect if this is about scheduling/calendar
    const isSchedulingInsight = combined.includes('schedule') || combined.includes('meeting') || combined.includes('calendar') || combined.includes('reschedule');

    // If it's both an email and scheduling insight, add a Confirm button for automation
    if (isEmailInsight && isSchedulingInsight) {
      actions.push({
        label: '✅ Confirm',
        onClick: () => handleConfirmAction(insight, index),
        type: 'confirm',
        priority: true
      });
    }

    if (isEmailInsight) {
      actions.push({
        label: '📧 Reply to Email',
        onClick: () => handleReplyEmail(insight, index),
        type: 'primary'
      });
    }

    if (isSchedulingInsight) {
      actions.push({
        label: '📅 Open Calendar',
        onClick: () => {
          if (onNavigate) {
            onNavigate('calendar');
          }
        },
        type: 'primary'
      });
    }

    // Detect if this is about tasks
    if (combined.includes('task') || combined.includes('todo') || combined.includes('priority')) {
      actions.push({
        label: '✅ View Tasks',
        onClick: () => {
          if (onNavigate) {
            onNavigate('todo');
          }
        },
        type: 'primary'
      });
    }

    return actions;
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'urgent': return <AlertTriangle className="w-5 h-5 text-red-400" />;
      case 'suggestion': return <Lightbulb className="w-5 h-5 text-yellow-400" />;
      case 'optimization': return <Zap className="w-5 h-5 text-green-400" />;
      case 'conflict': return <AlertTriangle className="w-5 h-5 text-orange-400" />;
      default: return <Sparkles className="w-5 h-5 text-blue-400" />;
    }
  };

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail className="w-4 h-4" />;
      case 'calendar': return <Calendar className="w-4 h-4" />;
      case 'task': return <CheckSquare className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'in-progress': return 'text-yellow-400';
      case 'pending': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const handleSidebarNavigation = (itemId: string) => {
    setActiveTab(itemId);
    if (onNavigate) {
      onNavigate(itemId);
    }
  };

  const handleToggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    try { 
      localStorage.setItem('sidebarCollapsed', String(next)); 
    } catch {}
  };

  const handleApproveAction = async (itemId: string) => {
    console.log('Approved action:', itemId);
    try {
      const response = await fetch('http://localhost:8000/api/schedule/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ approval_id: itemId })
      });

      const data = await response.json();

      if (data.success) {
        setAiActions(data.actions || []);
        setApprovalItems(data.approvals || []);
        showNotification(data.message || '✓ Action approved', 'success');
      } else {
        showNotification('Failed to approve action', 'error');
      }
    } catch (error) {
      console.error('Error approving action:', error);
      showNotification('Failed to approve action', 'error');
    }
  };

  const handleRejectAction = async (itemId: string) => {
    console.log('Rejected action:', itemId);
    try {
      const response = await fetch('http://localhost:8000/api/schedule/reject', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ approval_id: itemId })
      });

      const data = await response.json();

      if (data.success) {
        setApprovalItems(data.approvals || []);
        showNotification('Action skipped', 'info');
      } else {
        showNotification('Failed to reject action', 'error');
      }
    } catch (error) {
      console.error('Error rejecting action:', error);
      showNotification('Failed to reject action', 'error');
    }
  };

  return (
    <div className="h-screen bg-[#1e1e1e]">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-72'} transition-all duration-300 flex flex-col h-screen pb-20`}>
        {/* Dashboard Content Area */}
        <div className="flex-1 bg-[#1e1e1e] overflow-y-auto">
          
          {/* AI Assistant Header */}
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-600 rounded-lg">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-white text-2xl font-medium">EmoBot AI Assistant</h1>
                  <p className="text-gray-400">Your personal productivity companion</p>
                </div>
              </div>
              <div className="flex flex-col items-end space-y-2">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={viewInsightHistory}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-3 rounded-lg flex items-center space-x-2 transition-colors font-medium"
                    title="View insight history"
                  >
                    <History className="w-5 h-5" />
                    <span>History</span>
                  </button>
                  <button
                    onClick={analyzeInsights}
                    disabled={isAnalyzing}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors font-medium"
                  >
                    {isAnalyzing ? (
                      <>
                        <Clock className="w-5 h-5 animate-spin" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5" />
                        <span>Analyze Now</span>
                      </>
                    )}
                  </button>
                </div>
                {(() => {
                  try {
                    const lastRefresh = localStorage.getItem('insightsLastRefresh');
                    if (lastRefresh) {
                      const minutes = Math.floor((Date.now() - parseInt(lastRefresh)) / 60000);
                      if (minutes < 1) return <span className="text-xs text-gray-400">Just now</span>;
                      if (minutes < 60) return <span className="text-xs text-gray-400">Updated {minutes}m ago</span>;
                      const hours = Math.floor(minutes / 60);
                      return <span className="text-xs text-gray-400">Updated {hours}h ago</span>;
                    }
                  } catch {}
                  return null;
                })()}
              </div>
            </div>
          </div>

          {/* AI Insights & Recommendations */}
          <div className="px-6 mb-6">
            <div className="bg-[#453f3b] rounded-lg overflow-hidden flex flex-col" style={{ maxHeight: '700px' }}>
              {/* Fixed Header with Title and Overview */}
              <div className="flex-shrink-0">
                {/* Title */}
                <div className="px-6 pt-6 pb-3">
                  <div className="flex items-center space-x-2">
                    <Brain className="w-5 h-5 text-purple-400" />
                    <h2 className="text-lg font-semibold text-white">AI Insights & Recommendations</h2>
                  </div>
                </div>

                {/* Overview Stats - Pinned */}
                <div className="px-6 pb-4">
                  <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg p-6">
                    <div className="grid grid-cols-4 gap-4">
                      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                        <div className="text-3xl font-bold text-white mb-1">
                          {insightsSummary?.unread_emails ?? emailSummary.unreadEmails}
                        </div>
                        <div className="text-sm text-white/80">Unread Emails</div>
                      </div>
                      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                        <div className="text-3xl font-bold text-white mb-1">
                          {insightsSummary?.upcoming_events ?? calendarSummary.upcomingEvents}
                        </div>
                        <div className="text-sm text-white/80">Upcoming Events</div>
                      </div>
                      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                        <div className="text-3xl font-bold text-white mb-1">
                          {insightsSummary?.pending_tasks ?? todoSummary.pendingTasks}
                        </div>
                        <div className="text-sm text-white/80">Pending Tasks</div>
                      </div>
                      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                        <div className="text-3xl font-bold text-white mb-1">
                          {insightsSummary?.insights_count ?? insights.length}
                        </div>
                        <div className="text-sm text-white/80">Insights Found</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Scrollable Content - Insights Only */}
              <div className="flex-1 overflow-y-auto px-6 pb-6">
                
                {/* Insights Content */}
                {isAnalyzing ? (
                  <div className="text-center py-12">
                    <Clock className="w-12 h-12 text-blue-400 mx-auto mb-4 animate-spin" />
                    <p className="text-gray-400">Analyzing your emails, calendar, and tasks...</p>
                  </div>
                ) : insights.length > 0 ? (
                  <div className="space-y-3">
                    {insights.map((insight, index) => (
                      <div
                        key={index}
                        className={`border-l-4 rounded-lg p-4 ${getInsightTypeClass(insight.type)}`}
                      >
                        <div className="flex items-start space-x-3 mb-3">
                          <span className="text-2xl">{getInsightTypeIcon(insight.type)}</span>
                          <div className="flex-1">
                            <h3 className="text-white font-semibold mb-2">{insight.title}</h3>
                            <p className="text-gray-300 text-sm leading-relaxed">{insight.content}</p>
                            {insight.suggestion && (
                              <div className="mt-3 bg-blue-900/30 border border-blue-600/20 rounded-lg p-3">
                                <p className="text-blue-300 text-sm">
                                  <strong className="text-blue-400">💡 Suggestion:</strong> {insight.suggestion}
                                </p>
                              </div>
                            )}
                            {/* Show email draft preview if generated */}
                            {insightEmailDrafts[index] && (
                              <div className="mt-3 bg-green-900/20 border border-green-600/20 rounded-lg p-3">
                                <p className="text-green-400 text-xs font-medium mb-2">📧 Drafted Email Preview:</p>
                                <div className="bg-black/30 rounded p-2 space-y-1">
                                  <p className="text-gray-300 text-xs"><strong>To:</strong> {insightEmailDrafts[index].to}</p>
                                  <p className="text-gray-300 text-xs"><strong>Subject:</strong> {insightEmailDrafts[index].subject}</p>
                                  <div className="mt-2 pt-2 border-t border-gray-700">
                                    <p className="text-gray-400 text-xs whitespace-pre-wrap line-clamp-3">{insightEmailDrafts[index].body}</p>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center flex-wrap gap-2 mt-3">
                          {/* Smart Action Buttons */}
                          {generateSmartActions(insight, index).map((action, actionIndex) => (
                            <button
                              key={actionIndex}
                              onClick={action.onClick}
                              className={`${
                                action.type === 'confirm'
                                  ? 'bg-green-600 hover:bg-green-700'
                                  : 'bg-blue-600 hover:bg-blue-700'
                              } text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                                action.priority ? 'ring-2 ring-green-400 ring-opacity-50' : ''
                              }`}
                            >
                              {action.label}
                            </button>
                          ))}

                          {/* Management Actions */}
                          <button
                            onClick={() => markInsightComplete(index)}
                            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                            title="Mark as completed"
                          >
                            ✓ Complete
                          </button>
                          <button
                            onClick={() => markInsightNotUseful(index)}
                            className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                            title="Mark as not useful"
                          >
                            ✗ Not Useful
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Lightbulb className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                    <h3 className="text-white font-medium mb-2">💡 Smart Insights</h3>
                    <p className="text-gray-400 text-sm">Click "Analyze Now" to get AI-powered insights about your schedule.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* AI-Generated Schedule Optimization */}
          <div className="px-6 mb-6">
            <div className="bg-[#453f3b] rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-green-400" />
                  <h2 className="text-lg font-semibold text-white">AI-Generated Schedule Optimization</h2>
                </div>
                <button
                  onClick={optimizeSchedule}
                  disabled={isOptimizing}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors text-sm font-medium"
                >
                  {isOptimizing ? (
                    <>
                      <Clock className="w-4 h-4 animate-spin" />
                      <span>Optimizing...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      <span>Optimize Schedule</span>
                    </>
                  )}
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Priority Tasks */}
                <div>
                  <h3 className="text-gray-300 font-medium mb-3">Priority Tasks</h3>
                  <div className="space-y-2">
                    {todos.filter(t => t.priority === 'high' && !t.completed).slice(0, 3).map((todo) => (
                      <div key={todo.id} className="flex items-center space-x-2 text-sm">
                        <CheckSquare className="w-4 h-4 text-red-400" />
                        <span className="text-gray-300">{todo.title}</span>
                      </div>
                    ))}
                    {todos.filter(t => t.priority === 'high' && !t.completed).length === 0 && (
                      <p className="text-gray-500 text-sm">No high priority tasks</p>
                    )}
                  </div>
                </div>

                {/* AI Actions Taken */}
                <div>
                  <h3 className="text-gray-300 font-medium mb-3">AI Actions Taken</h3>
                  <div className="space-y-2">
                    {aiActions.length > 0 ? (
                      aiActions.map((action) => (
                        <div key={action.id} className="flex items-center justify-between text-sm bg-[#1e1e1e] rounded-lg p-3">
                          <div className="flex items-center space-x-2">
                            {getActionIcon(action.type)}
                            <span className="text-gray-300">{action.description}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-blue-400 font-medium">{action.count}</span>
                            <div className={`w-2 h-2 rounded-full ${
                              action.status === 'completed' ? 'bg-green-400' :
                              action.status === 'in-progress' ? 'bg-yellow-400' : 'bg-gray-400'
                            }`} />
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <Activity className="w-10 h-10 text-gray-600 mx-auto mb-2" />
                        <p className="text-gray-500 text-sm">No actions yet</p>
                        <p className="text-gray-600 text-xs mt-1">Click "Optimize Schedule" above</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Your Approval Needed */}
                <div>
                  <h3 className="text-gray-300 font-medium mb-3">
                    Your Approval Needed
                    {approvalItems.length > 0 && (
                      <span className="ml-2 bg-yellow-600 text-white text-xs px-2 py-0.5 rounded-full">{approvalItems.length}</span>
                    )}
                  </h3>
                  <div className="space-y-3">
                    {approvalItems.length > 0 ? (
                      approvalItems.map((item) => (
                        <div key={item.id} className="bg-[#1e1e1e] rounded-lg p-3 border border-yellow-600/20">
                          <h4 className="text-white text-sm font-medium mb-1">{item.title}</h4>
                          <p className="text-gray-400 text-xs mb-2">{item.description}</p>
                          <p className="text-green-400 text-xs mb-3">{item.impact}</p>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleApproveAction(item.id)}
                              className="flex items-center space-x-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors font-medium"
                            >
                              <CheckCircle className="w-3 h-3" />
                              <span>Approve</span>
                            </button>
                            <button
                              onClick={() => handleRejectAction(item.id)}
                              className="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors font-medium"
                            >
                              Skip
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <CheckCircle className="w-10 h-10 text-gray-600 mx-auto mb-2" />
                        <p className="text-gray-500 text-sm">No approvals needed</p>
                        <p className="text-gray-600 text-xs mt-1">You're all caught up!</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Data Summary Cards */}
          <div className="px-6 pb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Calendar Summary */}
              <div className="bg-[#453f3b] rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Today's Schedule</h3>
                  <Calendar className="w-5 h-5 text-blue-400" />
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Events</span>
                    <span className="text-white font-medium">{calendarSummary.todayEvents}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Upcoming</span>
                    <span className="text-white font-medium">{calendarSummary.upcomingEvents}</span>
                  </div>
                  <div className="mt-4 p-3 bg-[#1e1e1e] rounded-lg">
                    <p className="text-sm text-blue-400">Next: {calendarSummary.nextEvent}</p>
                  </div>
                </div>
              </div>

              {/* Todo Summary */}
              <div className="bg-[#453f3b] rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Task Progress</h3>
                  <CheckSquare className="w-5 h-5 text-green-400" />
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Completed</span>
                    <span className="text-green-400 font-medium">{todoSummary.completedTasks}/{todoSummary.totalTasks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Pending</span>
                    <span className="text-yellow-400 font-medium">{todoSummary.pendingTasks}</span>
                  </div>
                  <div className="mt-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-300">AI Optimized</span>
                      <span className="text-white">{todoSummary.completionRate}%</span>
                    </div>
                    <div className="w-full bg-[#1e1e1e] rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${todoSummary.completionRate}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Email Summary */}
              <div className="bg-[#453f3b] rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Smart Inbox</h3>
                  <Mail className="w-5 h-5 text-purple-400" />
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Needs Action</span>
                    <span className="text-red-400 font-medium">{emailSummary.unreadEmails}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">AI Processed</span>
                    <span className="text-green-400 font-medium">{emailSummary.totalEmails - emailSummary.unreadEmails}</span>
                  </div>
                  <div className="mt-4 p-3 bg-[#1e1e1e] rounded-lg">
                    <p className="text-sm text-purple-400">Latest: {emailSummary.recentSender}</p>
                    {emailSummary.priority > 0 && (
                      <div className="flex items-center mt-2">
                        <AlertTriangle className="w-4 h-4 text-red-400 mr-2" />
                        <span className="text-sm text-red-400">{emailSummary.priority} priority emails</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <ChatBox
        onSendMessage={(message) => console.log('AI Dashboard chat:', message)}
        onOpenFullChat={() => onNavigate && onNavigate('main')}
        sidebarCollapsed={isCollapsed}
      />

      {/* Notification */}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}

      {/* Insight History Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1a1a] border border-gray-700 rounded-lg w-[600px] max-h-[80vh] flex flex-col">
            {/* History Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center space-x-2">
                <History className="w-5 h-5 text-blue-400" />
                <h2 className="text-lg font-medium text-white">Insight History</h2>
              </div>
              <button
                onClick={() => setShowHistory(false)}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* History Filter Tabs */}
            {Object.keys(insightStates).length > 0 && (
              <div className="flex items-center flex-wrap gap-2 px-6 pt-4 border-b border-gray-700 pb-4">
                <button
                  onClick={() => setHistoryFilter('all')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    historyFilter === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setHistoryFilter('email_sent')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    historyFilter === 'email_sent'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  📧 Email Sent
                </button>
                <button
                  onClick={() => setHistoryFilter('calendar_added')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    historyFilter === 'calendar_added'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  📅 Calendar Added
                </button>
                <button
                  onClick={() => setHistoryFilter('completed')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    historyFilter === 'completed'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  ✓ Completed
                </button>
                <button
                  onClick={() => setHistoryFilter('not_useful')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    historyFilter === 'not_useful'
                      ? 'bg-gray-500 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  ✗ Not Useful
                </button>
              </div>
            )}

            {/* History Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {Object.keys(insightStates).length === 0 ? (
                <div className="text-center py-12">
                  <History className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">No history yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {Object.entries(insightStates)
                    .filter(([, state]: [string, any]) => {
                      if (historyFilter === 'all') return true;
                      return state.status === historyFilter;
                    })
                    .sort(([, a]: [string, any], [, b]: [string, any]) => b.timestamp - a.timestamp)
                    .map(([hash, state]: [string, any]) => {
                    const statusEmoji = {
                      'email_sent': '📧',
                      'calendar_added': '📅',
                      'completed': '✓',
                      'not_useful': '✗',
                      'snoozed': '⏰'
                    }[state.status] || '•';

                    const statusColor = {
                      'email_sent': 'border-blue-600/20 bg-blue-900/20',
                      'calendar_added': 'border-purple-600/20 bg-purple-900/20',
                      'completed': 'border-green-600/20 bg-green-900/20',
                      'not_useful': 'border-gray-600/20 bg-gray-900/20',
                      'snoozed': 'border-blue-600/20 bg-blue-900/20'
                    }[state.status] || 'border-gray-600/20 bg-gray-900/20';

                    const statusLabel = {
                      'email_sent': 'EMAIL SENT',
                      'calendar_added': 'CALENDAR ADDED',
                      'completed': 'COMPLETED',
                      'not_useful': 'NOT USEFUL',
                      'snoozed': 'SNOOZED'
                    }[state.status] || state.status.replace('_', ' ').toUpperCase();

                    const date = new Date(state.timestamp).toLocaleString();

                    return (
                      <div
                        key={hash}
                        className={`border-l-3 rounded-lg p-4 ${statusColor}`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            {/* Status badge */}
                            <div className="flex items-center space-x-2 mb-2">
                              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                state.status === 'email_sent' ? 'bg-blue-500 text-white' :
                                state.status === 'calendar_added' ? 'bg-purple-600 text-white' :
                                state.status === 'completed' ? 'bg-green-600 text-white' :
                                state.status === 'not_useful' ? 'bg-gray-600 text-white' :
                                'bg-blue-600 text-white'
                              }`}>
                                {statusEmoji} {statusLabel}
                              </span>
                              <span className="text-gray-400 text-xs">{date}</span>
                            </div>

                            {/* Insight title - prominently displayed */}
                            {state.title && (
                              <h4 className="text-white font-semibold text-base mb-2">
                                {state.title}
                              </h4>
                            )}

                            {/* Insight content */}
                            {state.content && (
                              <p className="text-gray-300 text-sm leading-relaxed mb-2">
                                {state.content}
                              </p>
                            )}

                            {/* Suggestion */}
                            {state.suggestion && (
                              <div className="bg-blue-900/30 border border-blue-600/20 rounded-lg p-2 mb-2">
                                <p className="text-blue-300 text-xs">
                                  <strong className="text-blue-400">💡 Suggestion:</strong> {state.suggestion}
                                </p>
                              </div>
                            )}

                            {/* Email Sent Details */}
                            {state.status === 'email_sent' && state.emailTo && (
                              <div className="bg-blue-900/30 border border-blue-500/20 rounded-lg p-2 mb-2">
                                <p className="text-blue-300 text-xs mb-1">
                                  <strong className="text-blue-400">📧 Email Sent:</strong>
                                </p>
                                <p className="text-gray-300 text-xs">To: {state.emailTo}</p>
                                {state.emailSubject && (
                                  <p className="text-gray-300 text-xs">Subject: {state.emailSubject}</p>
                                )}
                              </div>
                            )}

                            {/* Calendar Added Details */}
                            {state.status === 'calendar_added' && state.eventTitle && (
                              <div className="bg-purple-900/30 border border-purple-500/20 rounded-lg p-2 mb-2">
                                <p className="text-purple-300 text-xs mb-1">
                                  <strong className="text-purple-400">📅 Calendar Event:</strong>
                                </p>
                                <p className="text-gray-300 text-xs">{state.eventTitle}</p>
                                {state.eventDate && state.eventTime && (
                                  <p className="text-gray-300 text-xs">{state.eventDate} at {state.eventTime}</p>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* History Footer */}
            <div className="flex items-center justify-between p-6 border-t border-gray-700">
              <button
                onClick={clearInsightHistory}
                className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
                disabled={Object.keys(insightStates).length === 0}
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear History</span>
              </button>
              <button
                onClick={() => setShowHistory(false)}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Compose Email Modal */}
      {showComposeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1a1a] border border-gray-700 rounded-lg w-[600px] max-h-[80vh] flex flex-col">
            {/* Compose Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h2 className="text-lg font-medium text-white">New Message</h2>
              <button
                onClick={() => setShowComposeModal(false)}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Compose Form */}
            <div className="flex-1 p-6 space-y-4 overflow-y-auto">
              {/* To Field */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">To</label>
                <input
                  type="email"
                  value={composeForm.to}
                  onChange={(e) => setComposeForm(prev => ({ ...prev, to: e.target.value }))}
                  placeholder="recipient@example.com"
                  className="w-full bg-[#0a0a0a] border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Subject Field */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Subject</label>
                <input
                  type="text"
                  value={composeForm.subject}
                  onChange={(e) => setComposeForm(prev => ({ ...prev, subject: e.target.value }))}
                  placeholder="Email subject"
                  className="w-full bg-[#0a0a0a] border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Content Field */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Message</label>
                <textarea
                  value={composeForm.content}
                  onChange={(e) => setComposeForm(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Write your message..."
                  rows={12}
                  className="w-full bg-[#0a0a0a] border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>
            </div>

            {/* Compose Footer */}
            <div className="flex items-center justify-between p-6 border-t border-gray-700">
              <button
                onClick={() => setShowComposeModal(false)}
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSendEmail}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors font-medium"
                >
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </button>
                {calendarEventData && (
                  <button
                    onClick={handleSendAndSchedule}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors font-medium ring-2 ring-green-400 ring-opacity-50"
                  >
                    <Calendar className="w-4 h-4" />
                    <span>Send & Schedule</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Calendar Confirmation Modal */}
      {showCalendarConfirmation && calendarEventData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1a1a] border border-gray-700 rounded-lg w-[500px] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center space-x-2">
                <Calendar className="w-5 h-5 text-green-400" />
                <h2 className="text-lg font-medium text-white">Add to Calendar</h2>
              </div>
              <button
                onClick={() => setShowCalendarConfirmation(false)}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Event Details */}
            <div className="p-6 space-y-4">
              <div className="bg-green-900/20 border border-green-600/20 rounded-lg p-4">
                <p className="text-green-400 text-sm mb-3">✅ Email sent successfully!</p>
                <p className="text-gray-300 text-sm">Would you like to add this meeting to your calendar?</p>
              </div>

              {/* Event Information */}
              <div className="bg-[#0a0a0a] border border-gray-700 rounded-lg p-4 space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-20 text-gray-400 text-sm">Title:</div>
                  <div className="text-white text-sm font-medium">{calendarEventData.title}</div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-20 text-gray-400 text-sm">Date:</div>
                  <div className="text-white text-sm">{calendarEventData.date}</div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-20 text-gray-400 text-sm">Time:</div>
                  <div className="text-white text-sm">{calendarEventData.time}</div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-20 text-gray-400 text-sm">Duration:</div>
                  <div className="text-white text-sm">{calendarEventData.duration}</div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-20 text-gray-400 text-sm">Attendees:</div>
                  <div className="text-white text-sm">{calendarEventData.recipient}</div>
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-700">
              <button
                onClick={() => {
                  setShowCalendarConfirmation(false);
                  setCalendarEventData(null);
                }}
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Skip
              </button>
              <button
                onClick={handleAddToCalendar}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors font-medium"
              >
                <Calendar className="w-4 h-4" />
                <span>Add to Calendar</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;