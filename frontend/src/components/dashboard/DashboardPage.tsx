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
  Activity
} from 'lucide-react';
import Sidebar from '../ui/Sidebar';
import ChatBox from '../ui/ChatBox';
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
  
  // Get real data from context
  const { getCalendarSummary, getEmailSummary, getTodoSummary, todos, emails } = useData();
  
  // Real summary data
  const calendarSummary = getCalendarSummary();
  const todoSummary = getTodoSummary();
  const emailSummary = getEmailSummary();

  // Mock AI insights and recommendations (in real app, this would come from Gemini API)
  const aiInsights: AIInsight[] = [
    {
      id: '1',
      type: 'urgent',
      title: 'Client email needs immediate response',
      description: 'High-priority email from John Smith about project timeline requires attention',
      action: 'Reply Now',
      actionType: 'primary',
      priority: 'high'
    },
    {
      id: '2',
      type: 'suggestion',
      title: 'Optimize afternoon schedule',
      description: 'Move 3pm meeting to tomorrow to create focus block for high-priority tasks',
      action: 'Apply Changes',
      actionType: 'secondary',
      priority: 'medium'
    },
    {
      id: '3',
      type: 'optimization',
      title: 'Auto-created follow-up task',
      description: 'Created "Review contract" task based on client meeting agenda',
      action: 'View Task',
      actionType: 'secondary',
      priority: 'low'
    },
    {
      id: '4',
      type: 'conflict',
      title: 'Schedule conflict detected',
      description: 'Two meetings scheduled at 2pm today - Team standup and Client call',
      action: 'Resolve Conflict',
      actionType: 'primary',
      priority: 'high'
    }
  ];

  const aiActions: AIAction[] = [
    {
      id: '1',
      type: 'email',
      description: 'Organized emails by priority',
      count: 12,
      status: 'completed'
    },
    {
      id: '2',
      type: 'task',
      description: 'Prioritized tasks by deadline',
      count: 8,
      status: 'completed'
    },
    {
      id: '3',
      type: 'calendar',
      description: 'Blocked focus time slots',
      count: 3,
      status: 'in-progress'
    },
    {
      id: '4',
      type: 'email',
      description: 'Drafting routine responses',
      count: 5,
      status: 'in-progress'
    }
  ];

  const approvalItems: ApprovalItem[] = [
    {
      id: '1',
      type: 'reschedule',
      title: 'Reschedule 2pm meeting',
      description: 'Move "Client Strategy Call" to tomorrow 10am',
      impact: 'Resolves conflict, optimizes focus time'
    },
    {
      id: '2',
      type: 'priority',
      title: 'Re-prioritize task order',
      description: 'Move "API Bug Fix" to top of today\'s list',
      impact: 'Enables demo preparation for client meeting'
    },
    {
      id: '3',
      type: 'automation',
      title: 'Auto-respond to routine emails',
      description: 'Send template responses to 3 status update requests',
      impact: 'Saves 30 minutes, maintains communication'
    }
  ];

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

  const handleApproveAction = (itemId: string) => {
    console.log('Approved action:', itemId);
    // In real app, this would communicate with the backend
  };

  const handleRejectAction = (itemId: string) => {
    console.log('Rejected action:', itemId);
    // In real app, this would communicate with the backend
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
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-white text-2xl font-medium">EmoBot AI Assistant</h1>
                <p className="text-gray-400">Good morning! I've analyzed your schedule and found optimization opportunities.</p>
              </div>
            </div>
          </div>

          {/* AI Insights & Recommendations */}
          <div className="px-6 mb-6">
            <div className="bg-[#453f3b] rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="w-5 h-5 text-purple-400" />
                <h2 className="text-lg font-semibold text-white">AI Insights & Recommendations</h2>
              </div>
              
              <div className="space-y-3">
                {aiInsights.map((insight) => (
                  <div 
                    key={insight.id} 
                    className={`p-4 rounded-lg border-l-4 ${
                      insight.type === 'urgent' ? 'bg-red-900/20 border-red-500' :
                      insight.type === 'conflict' ? 'bg-orange-900/20 border-orange-500' :
                      insight.type === 'suggestion' ? 'bg-yellow-900/20 border-yellow-500' :
                      'bg-green-900/20 border-green-500'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        {getInsightIcon(insight.type)}
                        <div className="flex-1">
                          <h3 className="text-white font-medium mb-1">{insight.title}</h3>
                          <p className="text-gray-300 text-sm">{insight.description}</p>
                        </div>
                      </div>
                      {insight.action && (
                        <button className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          insight.actionType === 'primary' 
                            ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                            : 'bg-[#1e1e1e] hover:bg-gray-700 text-gray-300'
                        }`}>
                          {insight.action}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* AI-Generated Schedule Optimization */}
          <div className="px-6 mb-6">
            <div className="bg-[#453f3b] rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Target className="w-5 h-5 text-green-400" />
                <h2 className="text-lg font-semibold text-white">AI-Generated Schedule Optimization</h2>
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
                    {aiActions.map((action) => (
                      <div key={action.id} className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2">
                          {getActionIcon(action.type)}
                          <span className="text-gray-300">{action.description}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-blue-400">{action.count}</span>
                          <div className={`w-2 h-2 rounded-full ${
                            action.status === 'completed' ? 'bg-green-400' :
                            action.status === 'in-progress' ? 'bg-yellow-400' : 'bg-gray-400'
                          }`} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Your Approval Needed */}
                <div>
                  <h3 className="text-gray-300 font-medium mb-3">Your Approval Needed</h3>
                  <div className="space-y-3">
                    {approvalItems.map((item) => (
                      <div key={item.id} className="bg-[#1e1e1e] rounded-lg p-3">
                        <h4 className="text-white text-sm font-medium mb-1">{item.title}</h4>
                        <p className="text-gray-400 text-xs mb-2">{item.description}</p>
                        <p className="text-green-400 text-xs mb-3">{item.impact}</p>
                        <div className="flex items-center space-x-2">
                          <button 
                            onClick={() => handleApproveAction(item.id)}
                            className="flex items-center space-x-1 px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
                          >
                            <CheckCircle className="w-3 h-3" />
                            <span>Approve</span>
                          </button>
                          <button 
                            onClick={() => handleRejectAction(item.id)}
                            className="px-2 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors"
                          >
                            Skip
                          </button>
                        </div>
                      </div>
                    ))}
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
    </div>
  );
};

export default DashboardPage;