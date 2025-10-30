import React, { useState } from 'react';
import { Calendar, Mail, CheckSquare, Clock, MessageSquare, User, Bot, Filter, Download, Eye } from 'lucide-react';
import Sidebar from './ui/Sidebar';
import ChatBox from './ui/ChatBox';

interface HistoryItem {
  id: string;
  type: 'chat' | 'task' | 'email' | 'calendar';
  title: string;
  description: string;
  timestamp: string;
  details?: any;
  status?: 'success' | 'error' | 'pending';
}

interface HistoryPageProps {
  onNavigate?: (page: string) => void;
}

const HistoryPage: React.FC<HistoryPageProps> = ({ onNavigate }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('history');
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null);


  const historyFilters = [
    { id: 'all', label: 'All Activity', count: 45 },
    { id: 'chat', label: 'Conversations', count: 23 },
    { id: 'task', label: 'Tasks', count: 12 },
    { id: 'email', label: 'Email Activity', count: 8 },
    { id: 'calendar', label: 'Calendar Events', count: 7 },
  ];

  const historyItems: HistoryItem[] = [
    {
      id: '1',
      type: 'chat',
      title: 'Dashboard Component Question',
      description: 'Asked about implementing real-time updates in dashboard panels',
      timestamp: '2 hours ago',
      status: 'success',
      details: {
        messages: [
          { sender: 'user', text: 'How do I implement real-time updates in dashboard panels?' },
          { sender: 'bot', text: 'You can use useEffect with setInterval for periodic updates, or WebSocket connections for live data streaming...' }
        ]
      }
    },
    {
      id: '2',
      type: 'task',
      title: 'Task Completed: Update LinkedIn Profile',
      description: 'Successfully updated LinkedIn profile with recent projects',
      timestamp: '4 hours ago',
      status: 'success',
      details: {
        taskName: 'Update LinkedIn Profile',
        completedAt: '4 hours ago',
        category: 'personal'
      }
    },
    {
      id: '3',
      type: 'email',
      title: 'Email Processed: Project Update',
      description: 'Responded to John Smith about Q4 project goals',
      timestamp: '6 hours ago',
      status: 'success',
      details: {
        from: 'john.smith@company.com',
        subject: 'Project Update - Q4 Goals',
        action: 'replied'
      }
    },
    {
      id: '4',
      type: 'calendar',
      title: 'Meeting Scheduled: Team Standup',
      description: 'Added daily standup meeting to calendar',
      timestamp: '1 day ago',
      status: 'success',
      details: {
        eventTitle: 'Team Standup',
        time: '09:00 AM',
        attendees: ['John', 'Sarah', 'Mike']
      }
    },
    {
      id: '5',
      type: 'chat',
      title: 'Email Integration Help',
      description: 'Discussed email API integration and authentication methods',
      timestamp: '1 day ago',
      status: 'success',
      details: {
        messages: [
          { sender: 'user', text: 'How do I integrate email API with OAuth2?' },
          { sender: 'bot', text: 'For email integration, you\'ll need to set up OAuth2 credentials...' }
        ]
      }
    },
    {
      id: '6',
      type: 'task',
      title: 'Task Failed: Pay Credit Card Bill',
      description: 'Payment failed due to insufficient funds',
      timestamp: '2 days ago',
      status: 'error',
      details: {
        taskName: 'Pay Credit Card Bill',
        error: 'Insufficient funds',
        category: 'finance'
      }
    },
    {
      id: '7',
      type: 'email',
      title: 'Email Received: Design Review',
      description: 'New email from Sarah about design feedback',
      timestamp: '2 days ago',
      status: 'success',
      details: {
        from: 'sarah@design.co',
        subject: 'Design Review Feedback',
        action: 'received'
      }
    },
    {
      id: '8',
      type: 'chat',
      title: 'Calendar Component Discussion',
      description: 'Explored different calendar view modes and event management',
      timestamp: '3 days ago',
      status: 'success',
      details: {
        messages: [
          { sender: 'user', text: 'What are the best practices for calendar UI components?' },
          { sender: 'bot', text: 'Good calendar components should support multiple view modes...' }
        ]
      }
    }
  ];

  const handleToggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    try { 
      localStorage.setItem('sidebarCollapsed', String(next)); 
    } catch {}
  };

  const handleSidebarNavigation = (itemId: string) => {
    setActiveTab(itemId);
    if (onNavigate) {
      onNavigate(itemId);
    }
  };

  const filteredItems = historyItems.filter(item => {
    if (activeFilter === 'all') return true;
    return item.type === activeFilter;
  });

  const getTypeIcon = (type: HistoryItem['type']) => {
    switch (type) {
      case 'chat':
        return <MessageSquare className="w-4 h-4" />;
      case 'task':
        return <CheckSquare className="w-4 h-4" />;
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'calendar':
        return <Calendar className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: HistoryItem['type']) => {
    switch (type) {
      case 'chat':
        return 'bg-blue-500';
      case 'task':
        return 'bg-green-500';
      case 'email':
        return 'bg-purple-500';
      case 'calendar':
        return 'bg-orange-500';
    }
  };

  const getStatusColor = (status?: HistoryItem['status']) => {
    switch (status) {
      case 'success':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'pending':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  const renderDetailsView = () => {
    if (!selectedItem) return null;

    return (
      <div className="bg-[#453f3b] rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-white">Activity Details</h3>
          <button
            onClick={() => setSelectedItem(null)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <h4 className="text-white font-medium mb-2">{selectedItem.title}</h4>
            <p className="text-gray-300 text-sm">{selectedItem.description}</p>
          </div>

          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getTypeColor(selectedItem.type)}`} />
              <span className="text-gray-400 capitalize">{selectedItem.type}</span>
            </div>
            <span className="text-gray-400">{selectedItem.timestamp}</span>
            {selectedItem.status && (
              <span className={getStatusColor(selectedItem.status)}>
                {selectedItem.status.toUpperCase()}
              </span>
            )}
          </div>

          {selectedItem.details && (
            <div className="bg-[#1e1e1e] rounded-lg p-4 mt-4">
              <h5 className="text-white font-medium mb-3">Details</h5>
              
              {selectedItem.type === 'chat' && selectedItem.details.messages && (
                <div className="space-y-3">
                  {selectedItem.details.messages.map((msg: any, idx: number) => (
                    <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                        msg.sender === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-700 text-gray-300'
                      }`}>
                        <div className="flex items-center space-x-2 mb-1">
                          {msg.sender === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                          <span className="text-xs capitalize">{msg.sender}</span>
                        </div>
                        <p>{msg.text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {selectedItem.type === 'task' && selectedItem.details.taskName && (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Task:</span>
                    <span className="text-white">{selectedItem.details.taskName}</span>
                  </div>
                  {selectedItem.details.completedAt && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Completed:</span>
                      <span className="text-white">{selectedItem.details.completedAt}</span>
                    </div>
                  )}
                  {selectedItem.details.category && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Category:</span>
                      <span className="text-white capitalize">{selectedItem.details.category}</span>
                    </div>
                  )}
                  {selectedItem.details.error && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Error:</span>
                      <span className="text-red-400">{selectedItem.details.error}</span>
                    </div>
                  )}
                </div>
              )}

              {selectedItem.type === 'email' && selectedItem.details.from && (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">From:</span>
                    <span className="text-white">{selectedItem.details.from}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Subject:</span>
                    <span className="text-white">{selectedItem.details.subject}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Action:</span>
                    <span className="text-white capitalize">{selectedItem.details.action}</span>
                  </div>
                </div>
              )}

              {selectedItem.type === 'calendar' && selectedItem.details.eventTitle && (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Event:</span>
                    <span className="text-white">{selectedItem.details.eventTitle}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Time:</span>
                    <span className="text-white">{selectedItem.details.time}</span>
                  </div>
                  {selectedItem.details.attendees && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Attendees:</span>
                      <span className="text-white">{selectedItem.details.attendees.join(', ')}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
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
      <div className={`${isCollapsed ? 'ml-20' : 'ml-72'} transition-all duration-300 flex flex-col h-screen`}>

        {/* History Content Area */}
        <div className="flex-1 bg-[#1e1e1e] flex pb-20">
          {/* History Filters Sidebar */}
          <div className="w-64 bg-[#1e1e1e] border-r border-[#453f3b]/30 p-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-white text-lg font-medium">Activity History</h2>
              <div className="flex space-x-1">
                <button className="text-gray-400 hover:text-white p-1" title="Export History">
                  <Download className="w-4 h-4" />
                </button>
                <button className="text-gray-400 hover:text-white p-1" title="Filter Options">
                  <Filter className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            {/* Activity Stats */}
            <div className="bg-[#453f3b] rounded-lg p-4 mb-6">
              <h3 className="text-white font-medium mb-3">This Week</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Conversations</span>
                  <span className="text-blue-400">12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Tasks Completed</span>
                  <span className="text-green-400">8</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Emails Processed</span>
                  <span className="text-purple-400">15</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Events Scheduled</span>
                  <span className="text-orange-400">4</span>
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="space-y-2">
              {historyFilters.map(filter => (
                <button
                  key={filter.id}
                  onClick={() => setActiveFilter(filter.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors text-sm ${
                    activeFilter === filter.id
                      ? 'bg-[#453f3b] text-white'
                      : 'text-gray-300 hover:text-white hover:bg-[#453f3b]/50'
                  }`}
                >
                  <span>{filter.label}</span>
                  <span className="bg-gray-600 text-white text-xs px-2 py-1 rounded-full">
                    {filter.count}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* History List */}
          <div className="flex-1 flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-[#453f3b]/30">
              <div className="flex items-center justify-between">
                <h3 className="text-white text-xl font-medium">
                  {historyFilters.find(f => f.id === activeFilter)?.label} ({filteredItems.length})
                </h3>
                <div className="flex items-center space-x-2">
                  <button className="text-gray-400 hover:text-white px-3 py-1 text-sm">
                    Latest First
                  </button>
                  <button className="text-gray-400 hover:text-white px-3 py-1 text-sm">
                    Group by Date
                  </button>
                </div>
              </div>
            </div>

            {/* Activity Timeline */}
            <div className="flex-1 overflow-y-auto">
              {filteredItems.length === 0 ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <Clock className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">No activity found</p>
                  </div>
                </div>
              ) : (
                <div className="p-6 space-y-4">
                  {filteredItems.map(item => (
                    <div
                      key={item.id}
                      className="bg-[#453f3b] rounded-lg p-4 border border-gray-600 hover:border-gray-500 transition-all cursor-pointer"
                      onClick={() => setSelectedItem(item)}
                    >
                      <div className="flex items-start space-x-4">
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full ${getTypeColor(item.type)} flex items-center justify-center text-white`}>
                          {getTypeIcon(item.type)}
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-white font-medium">{item.title}</h4>
                            <div className="flex items-center space-x-2">
                              {item.status && (
                                <div className={`w-2 h-2 rounded-full ${
                                  item.status === 'success' ? 'bg-green-400' :
                                  item.status === 'error' ? 'bg-red-400' : 'bg-yellow-400'
                                }`} />
                              )}
                              <button className="text-gray-400 hover:text-white">
                                <Eye className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                          
                          <p className="text-gray-300 text-sm mb-3">{item.description}</p>
                          
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <span className="text-xs text-gray-400 capitalize">{item.type}</span>
                              {item.status && (
                                <span className={`text-xs ${getStatusColor(item.status)}`}>
                                  {item.status.toUpperCase()}
                                </span>
                              )}
                            </div>
                            <span className="text-xs text-gray-500">{item.timestamp}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Details Panel */}
          {selectedItem && (
            <div className="w-96 border-l border-[#453f3b]/30 p-6">
              {renderDetailsView()}
            </div>
          )}
        </div>

        <ChatBox
          onSendMessage={(message) => console.log('History chat:', message)}
          onOpenFullChat={() => onNavigate && onNavigate('main')}
          sidebarCollapsed={isCollapsed}
        />
      </div>
    </div>
  );
};

export default HistoryPage;