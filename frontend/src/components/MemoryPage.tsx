import React, { useState } from 'react';
import { Search, Edit3, Trash2, Save, X, Brain, MessageSquare, User } from 'lucide-react';
import Sidebar from './ui/Sidebar';
import ChatBox from './ui/ChatBox';

interface MemoryItem {
  id: string;
  type: 'preference' | 'fact' | 'context';
  title: string;
  content: string;
  createdAt: Date;
  lastUpdated: Date;
}

interface MemoryPageProps {
  onNavigate?: (page: string) => void;
}

const MemoryPage: React.FC<MemoryPageProps> = ({ onNavigate }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('memory');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingItem, setEditingItem] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState('');

  // Sample memory data
  const [memoryItems, setMemoryItems] = useState<MemoryItem[]>([
    {
      id: '1',
      type: 'preference',
      title: 'Communication Style',
      content: 'Prefers direct, concise responses. Likes technical details but not lengthy explanations.',
      createdAt: new Date('2024-01-15'),
      lastUpdated: new Date('2024-01-20')
    },
    {
      id: '2',
      type: 'fact',
      title: 'Professional Background',
      content: 'Software engineer working on full-stack development. Experienced with React, TypeScript, and Node.js.',
      createdAt: new Date('2024-01-10'),
      lastUpdated: new Date('2024-01-15')
    },
    {
      id: '3',
      type: 'context',
      title: 'Current Project',
      content: 'Building an AI assistant frontend with calendar, email, and todo integrations. Working on dashboard redesign.',
      createdAt: new Date('2024-01-25'),
      lastUpdated: new Date('2024-01-25')
    },
    {
      id: '4',
      type: 'preference',
      title: 'Work Schedule',
      content: 'Usually works between 9 AM - 6 PM PST. Prefers morning meetings and focused afternoon work.',
      createdAt: new Date('2024-01-12'),
      lastUpdated: new Date('2024-01-18')
    }
  ]);

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

  const handleEditItem = (item: MemoryItem) => {
    setEditingItem(item.id);
    setEditingContent(item.content);
  };

  const handleSaveEdit = (id: string) => {
    setMemoryItems(prev => prev.map(item => 
      item.id === id 
        ? { ...item, content: editingContent, lastUpdated: new Date() }
        : item
    ));
    setEditingItem(null);
    setEditingContent('');
  };

  const handleCancelEdit = () => {
    setEditingItem(null);
    setEditingContent('');
  };

  const handleDeleteItem = (id: string) => {
    if (confirm('Are you sure you want to delete this memory item?')) {
      setMemoryItems(prev => prev.filter(item => item.id !== id));
    }
  };

  const filteredItems = memoryItems.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'preference': return <User className="w-4 h-4" />;
      case 'fact': return <Brain className="w-4 h-4" />;
      case 'context': return <MessageSquare className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'preference': return 'text-blue-400 bg-blue-400/10';
      case 'fact': return 'text-green-400 bg-green-400/10';
      case 'context': return 'text-purple-400 bg-purple-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
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
        {/* Page Header */}
        <div className="p-6 border-b border-[#453f3b]/30">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-white text-2xl font-semibold mb-2">Memory</h1>
                <p className="text-gray-400">Manage how EmoBot remembers and understands you</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search memories..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-[#453f3b] border border-[#453f3b]/50 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Memory Items */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {filteredItems.length === 0 ? (
              <div className="text-center py-12">
                <Brain className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <h3 className="text-gray-400 text-lg mb-2">No memories found</h3>
                <p className="text-gray-500">
                  {searchQuery ? 'Try adjusting your search terms.' : 'Start chatting to build your memory profile.'}
                </p>
              </div>
            ) : (
              filteredItems.map((item) => (
                <div key={item.id} className="bg-[#453f3b] rounded-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getTypeColor(item.type)}`}>
                        {getTypeIcon(item.type)}
                      </div>
                      <div>
                        <h3 className="text-white font-medium">{item.title}</h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`text-xs px-2 py-1 rounded-full capitalize ${getTypeColor(item.type)}`}>
                            {item.type}
                          </span>
                          <span className="text-gray-400 text-xs">
                            Updated {item.lastUpdated.toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {editingItem === item.id ? (
                        <>
                          <button
                            onClick={() => handleSaveEdit(item.id)}
                            className="p-2 text-green-400 hover:text-green-300 transition-colors"
                            title="Save changes"
                          >
                            <Save className="w-4 h-4" />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="p-2 text-gray-400 hover:text-gray-300 transition-colors"
                            title="Cancel editing"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => handleEditItem(item)}
                            className="p-2 text-gray-400 hover:text-white transition-colors"
                            title="Edit memory"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteItem(item.id)}
                            className="p-2 text-red-400 hover:text-red-300 transition-colors"
                            title="Delete memory"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="text-gray-300">
                    {editingItem === item.id ? (
                      <textarea
                        value={editingContent}
                        onChange={(e) => setEditingContent(e.target.value)}
                        className="w-full h-24 p-3 bg-[#1e1e1e] border border-[#453f3b]/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                        placeholder="Edit memory content..."
                      />
                    ) : (
                      <p className="leading-relaxed">{item.content}</p>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <ChatBox
        placeholder="Tell me something about yourself..."
        onSendMessage={(message) => console.log('Memory chat:', message)}
        onOpenFullChat={() => onNavigate && onNavigate('main')}
        sidebarCollapsed={isCollapsed}
      />
    </div>
  );
};

export default MemoryPage;