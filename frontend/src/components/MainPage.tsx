import React, { useState } from 'react';
import { Send, MessageSquare } from 'lucide-react';
import Sidebar from './ui/Sidebar';
import Avatar from './ui/Avatar';
import { useData } from '../context/DataContext';
import InlineReasoningDisplay from './InlineReasoningDisplay';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface MainPageProps {
  initialMessages?: Message[];
  onNavigate?: (page: string) => void;
}

const MainPage: React.FC<MainPageProps> = ({ initialMessages = [], onNavigate }) => {
  const { emobotAvatar, emobotName, chatMessages, addChatMessage } = useData();
  const [inputValue, setInputValue] = useState('');
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('chat');

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

  const handleSendMessage = async () => {
    const trimmed = inputValue.trim();
    if (!trimmed) {
      return;
    }

    setInputValue('');

    try {
      await addChatMessage({
        content: trimmed,
        sender: 'user'
      });
    } catch (error) {
      console.error('Failed to send message', error);
    }
  };


  return (
    <div className="h-screen bg-black overflow-hidden flex">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-64'} transition-all duration-300 flex flex-col h-screen flex-1 relative`}>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col relative z-0">
          {/* Chat Header */}
          <div className="p-6 text-center">
            <h1 className="font-display font-bold tracking-tight text-2xl text-white">CHAT</h1>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto px-6 pb-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
            {chatMessages.length === 0 ? (
              /* Welcome Screen - shown when no messages */
              <div className="flex flex-col items-center justify-center h-full">
                {/* Bot Avatar */}
                <div className="mb-8 relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
                  <Avatar
                    src={emobotAvatar}
                    alt={emobotName}
                    size="2xl"
                    className="relative shadow-2xl border-4 border-primary-500/60"
                  />
                </div>

                {/* Emobot Label */}
                <h1 className="font-display font-bold tracking-tight text-white text-2xl mb-2">
                  {emobotName}
                </h1>

                <div className="h-1 w-20 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full mb-10"></div>

                {/* Welcome Message */}
                <h2 className="font-display font-bold tracking-tight text-white/90 text-4xl text-center mb-4 max-w-2xl drop-shadow-lg">
                  Wassup! Ready to Start Your Day!
                </h2>
              </div>
            ) : (
              /* Messages List - shown when messages exist */
              <div className="space-y-6 max-w-4xl mx-auto py-4">
                {chatMessages.map(message => (
                  <div key={message.id} className="space-y-2">
                    {/* Message bubble with avatar */}
                    <div
                      className={`flex items-start gap-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {/* Show EmoBot avatar for bot messages */}
                      {message.sender === 'bot' && (
                        <Avatar
                          src={emobotAvatar}
                          alt={emobotName}
                          size="sm"
                          className="flex-shrink-0 mt-1 shadow-lg"
                        />
                      )}

                      {/* Response text */}
                      <div
                        className={`px-6 py-4 rounded-2xl font-sans text-base leading-relaxed max-w-xs lg:max-w-md backdrop-blur-md shadow-lg ${message.sender === 'user'
                          ? 'bg-gradient-to-br from-primary-600 to-primary-500 text-white rounded-tr-none border border-primary-500/60'
                          : 'glass-panel text-white/90 rounded-tl-none'
                          }`}
                      >
                        {message.content}
                      </div>
                    </div>

                    {/* Show reasoning steps below as a separate section for bot messages */}
                    {message.sender === 'bot' && message.reasoningSteps && message.reasoningSteps.length > 0 && (
                      <div className="flex items-start gap-4">
                        {/* Empty space for avatar alignment */}
                        <div className="w-8 flex-shrink-0"></div>
                        {/* Reasoning section with same max-width as message */}
                        <div className="max-w-xs lg:max-w-md">
                          <InlineReasoningDisplay steps={message.reasoningSteps} />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* Bottom Chat Bar */}
        <div className="px-6 py-6 relative z-10">
          <div className="glass-panel rounded-2xl p-2 flex items-center gap-3 shadow-2xl">
            <div className="pl-3">
              <MessageSquare className="w-6 h-6 text-primary-400 flex-shrink-0" />
            </div>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Type your message..."
              className="flex-1 h-12 bg-transparent border-none font-sans text-base text-white placeholder-white/40 focus:outline-none focus:ring-0"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim()}
              className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 hover:from-primary-400 hover:to-accent-400 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all duration-200 flex items-center justify-center flex-shrink-0 shadow-lg hover:shadow-primary-500/25"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={() => onNavigate && onNavigate('dashboard')}
              className="px-4 h-12 glass-button font-display font-semibold uppercase tracking-wide text-white/90 hover:text-white rounded-xl whitespace-nowrap flex-shrink-0"
            >
              Minimize Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
