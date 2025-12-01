import React, { useState, useEffect } from 'react';
import { Brain, Search, Filter, Calendar, Clock, MapPin, Tag, ChevronRight, Trash2, Edit3, Plus, X, Save, User, Loader2, Sparkles } from 'lucide-react';
import Sidebar from './ui/Sidebar';
import ChatBox from './ui/ChatBox';
import axios from 'axios';

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

  // Memory data - starts empty, will be populated from backend
  const [memoryItems, setMemoryItems] = useState<MemoryItem[]>([]);

  // Profile and analysis state
  const [userProfile, setUserProfile] = useState<string>('');
  const [aiAnalysis, setAiAnalysis] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isEditingAnalysis, setIsEditingAnalysis] = useState(false);
  const [editingAnalysisContent, setEditingAnalysisContent] = useState('');
  const [memoryStats, setMemoryStats] = useState<{
    total_memories: number;
    recent_memories: number;
    analysis_date: string;
  } | null>(null);

  // Load user profile and AI analysis from localStorage on mount
  useEffect(() => {
    try {
      const savedProfile = localStorage.getItem('user_profile');
      if (savedProfile) {
        const profile = JSON.parse(savedProfile);
        setUserProfile(profile.description || '');
      }

      const savedAnalysis = localStorage.getItem('ai_analysis');
      if (savedAnalysis) {
        const analysis = JSON.parse(savedAnalysis);
        setAiAnalysis(analysis.content || '');
        setMemoryStats(analysis.stats || null);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  }, []);

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
    } catch { }
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

  const handleAnalyzeMemory = async () => {
    setIsAnalyzing(true);
    try {
      const response = await axios.post('http://localhost:8000/api/memory/analyze');

      if (response.data.success) {
        const analysisContent = response.data.analysis;
        const stats = response.data.stats;

        setAiAnalysis(analysisContent);
        setMemoryStats(stats);

        // Save analysis to localStorage
        const analysisData = {
          content: analysisContent,
          stats: stats,
          lastUpdated: new Date().toISOString()
        };
        localStorage.setItem('ai_analysis', JSON.stringify(analysisData));

        // Auto-fill profile if empty
        if (!userProfile && response.data.profile_suggestions?.description) {
          setUserProfile(response.data.profile_suggestions.description);
        }
      } else {
        alert('Failed to analyze memory: ' + (response.data.error || 'Unknown error'));
      }
    } catch (error: any) {
      console.error('Error analyzing memory:', error);
      alert('Failed to analyze memory: ' + (error.message || 'Network error'));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveProfile = () => {
    try {
      const profile = {
        description: userProfile,
        lastUpdated: new Date().toISOString()
      };
      localStorage.setItem('user_profile', JSON.stringify(profile));

      // Also save analysis if it exists
      if (aiAnalysis) {
        const analysisData = {
          content: aiAnalysis,
          stats: memoryStats,
          lastUpdated: new Date().toISOString()
        };
        localStorage.setItem('ai_analysis', JSON.stringify(analysisData));
      }

      alert('Profile and analysis saved successfully!');
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Failed to save profile');
    }
  };

  const handleEditAnalysis = () => {
    setIsEditingAnalysis(true);
    setEditingAnalysisContent(aiAnalysis);
  };

  const handleSaveAnalysis = () => {
    setAiAnalysis(editingAnalysisContent);
    setIsEditingAnalysis(false);

    // Save to localStorage
    try {
      const analysisData = {
        content: editingAnalysisContent,
        stats: memoryStats,
        lastUpdated: new Date().toISOString()
      };
      localStorage.setItem('ai_analysis', JSON.stringify(analysisData));
    } catch (error) {
      console.error('Error saving analysis:', error);
    }
  };

  const handleCancelAnalysisEdit = () => {
    setIsEditingAnalysis(false);
    setEditingAnalysisContent('');
  };

  const filteredItems = memoryItems.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'preference': return <Brain className="w-4 h-4" />; // Changed from User to Brain
      case 'fact': return <Brain className="w-4 h-4" />;
      case 'context': return <Brain className="w-4 h-4" />; // Changed from MessageSquare to Brain
      default: return <Brain className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'preference': return 'text-primary-400 bg-primary-400/10 border border-primary-400/20';
      case 'fact': return 'text-accent-400 bg-accent-400/10 border border-accent-400/20';
      case 'context': return 'text-purple-400 bg-purple-400/10';
      default: return 'text-gray-400 bg-white/5 border border-primary-500/60';
    }
  };

  return (
    <div className="h-screen bg-black text-white font-sans selection:bg-primary-500/30">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-72'} transition-all duration-300 flex flex-col h-screen pb-20`}>
        {/* Header */}
        <div className="p-6 border-b border-primary-500/60">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-500/10 border border-primary-500/60 rounded-lg shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                <Brain className="w-6 h-6 text-primary-400" />
              </div>
              <div>
                <h1 className="text-white text-2xl font-display font-bold tracking-tight">Memory</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search memories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-black/50 border border-primary-500/60 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 w-64"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Memory Items */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-6xl mx-auto space-y-6">
            {/* User Profile Section */}
            <div className="glass-panel border border-primary-500/60 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-primary-500/10 text-primary-400 border border-primary-500/60">
                    <User className="w-5 h-5" />
                  </div>
                  <h2 className="text-white text-xl font-display font-bold tracking-wide">User Profile</h2>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleAnalyzeMemory}
                    disabled={isAnalyzing}
                    className="flex items-center space-x-2 px-4 py-2 bg-accent-500 hover:bg-accent-600 disabled:bg-gray-600 text-white rounded-lg transition-colors shadow-[0_0_15px_rgba(236,72,153,0.3)]"
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>Analyze</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleSaveProfile}
                    className="flex items-center space-x-2 px-4 py-2 btn-neon-flow text-white rounded-lg transition-colors shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                  >
                    <Save className="w-4 h-4" />
                    <span>Save</span>
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-2">
                    Describe yourself (background, interests, goals, preferences):
                  </label>
                  <textarea
                    value={userProfile}
                    onChange={(e) => setUserProfile(e.target.value)}
                    className="w-full h-48 p-3 bg-black/50 border border-primary-500/60 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                    placeholder="Example: I'm a software developer with 5 years of experience in Python and AI. I'm interested in machine learning and automation. Currently working on building an AI assistant. I prefer concise technical explanations and practical examples."
                  />
                </div>

                {memoryStats && (
                  <div className="flex items-center space-x-6 text-sm text-gray-400">
                    <div>
                      <span className="font-bold text-primary-400">{memoryStats.total_memories}</span> total memories
                    </div>
                    <div>
                      <span className="font-bold text-accent-400">{memoryStats.recent_memories}</span> recent memories
                    </div>
                    <div>
                      Last analyzed: {new Date(memoryStats.analysis_date).toLocaleDateString()}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* AI Analysis Section */}
            {aiAnalysis && (
              <div className="glass-panel border border-primary-500/60 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-accent-500/10 text-accent-400 border border-primary-500/60">
                      <Brain className="w-5 h-5" />
                    </div>
                    <h2 className="text-white text-xl font-display font-bold tracking-wide">AI Analysis</h2>
                  </div>

                  <div className="flex items-center space-x-2">
                    {isEditingAnalysis ? (
                      <>
                        <button
                          onClick={handleSaveAnalysis}
                          className="p-2 text-primary-400 hover:text-primary-300 transition-colors"
                          title="Save changes"
                        >
                          <Save className="w-4 h-4" />
                        </button>
                        <button
                          onClick={handleCancelAnalysisEdit}
                          className="p-2 text-gray-400 hover:text-gray-300 transition-colors"
                          title="Cancel editing"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={handleEditAnalysis}
                        className="p-2 text-gray-400 hover:text-white transition-colors"
                        title="Edit analysis"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                <div className="bg-black/50 rounded-lg p-4 border-l-4 border-accent-500">
                  {isEditingAnalysis ? (
                    <textarea
                      value={editingAnalysisContent}
                      onChange={(e) => setEditingAnalysisContent(e.target.value)}
                      className="w-full h-64 p-3 bg-black/50 border border-primary-500/60 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent-500 resize-none"
                      placeholder="Edit AI analysis..."
                    />
                  ) : (
                    <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{aiAnalysis}</p>
                  )}
                </div>

                <div className="mt-4 p-3 bg-primary-500/10 border border-primary-500/60 rounded-lg">
                  <p className="text-primary-300 text-sm">
                    💡 Tip: You can edit both the profile and analysis. Click Save to persist your changes.
                  </p>
                </div>
              </div>
            )}

            {/* Memory Items List */}
            {filteredItems.length === 0 && !aiAnalysis ? (
              <div className="text-center py-12">
                <Brain className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <h3 className="text-gray-400 text-lg mb-2">No memories found</h3>
                <p className="text-gray-500">
                  {searchQuery ? 'Try adjusting your search terms.' : 'Start chatting to build your memory profile.'}
                </p>
              </div>
            ) : (
              filteredItems.map((item) => (
                <div key={item.id} className="glass-panel border border-primary-500/60 rounded-lg p-6 hover:border-primary-500/40 transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getTypeColor(item.type)}`}>
                        {getTypeIcon(item.type)}
                      </div>
                      <div>
                        <h3 className="text-white font-display font-bold tracking-wide">{item.title}</h3>
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
                            className="p-2 text-primary-400 hover:text-primary-300 transition-colors"
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
                            className="p-2 text-accent-400 hover:text-accent-300 transition-colors"
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
                        className="w-full h-24 p-3 bg-black/50 border border-primary-500/60 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
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