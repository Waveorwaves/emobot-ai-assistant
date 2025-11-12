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
    } catch {}
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
    <div className="h-screen bg-[#1e1e1e]">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-72'} transition-all duration-300 flex flex-col h-screen`}>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-[#1e1e1e]">
          {/* Chat Header */}
          <div className="p-6 text-center">
            <h1 className="text-white text-2xl font-medium">CHAT</h1>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto px-6 pb-4">
            {chatMessages.length === 0 ? (
              /* Welcome Screen - shown when no messages */
              <div className="flex flex-col items-center justify-center h-full">
                {/* Bot Avatar */}
                <div className="mb-6">
                  <Avatar
                    src={emobotAvatar}
                    alt={emobotName}
                    size="2xl"
                    className="shadow-2xl border-4 border-white/10"
                  />
                </div>

                {/* Emobot Label */}
                <h1 className="text-white text-2xl font-semibold mb-12">
                  {emobotName}
                </h1>

                {/* Welcome Message */}
                <h2 className="text-white text-3xl font-bold text-center mb-4 max-w-2xl">
                  Wassup! Ready to Start Your Day!
                </h2>
              </div>
            ) : (
              /* Messages List - shown when messages exist */
              <div className="space-y-4 max-w-4xl mx-auto">
                {chatMessages.map(message => (
                  <div key={message.id} className="space-y-2">
                    {/* Message bubble with avatar */}
                    <div
                      className={`flex items-start gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {/* Show EmoBot avatar for bot messages */}
                      {message.sender === 'bot' && (
                        <Avatar
                          src={emobotAvatar}
                          alt={emobotName}
                          size="sm"
                          className="flex-shrink-0 mt-1"
                        />
                      )}

                      {/* Response text */}
                      <div
                        className={`px-4 py-3 rounded-lg text-sm max-w-xs lg:max-w-md ${
                          message.sender === 'user'
                            ? 'bg-[#453f3b] text-white'
                            : 'bg-[#453f3b]/70 text-white'
                        }`}
                      >
                        {message.content}
                      </div>
                    </div>

                    {/* Show reasoning steps below as a separate section for bot messages */}
                    {message.sender === 'bot' && message.reasoningSteps && message.reasoningSteps.length > 0 && (
                      <div className="flex items-start gap-3">
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
        <div className="bg-[#1e1e1e] px-4 py-3 border-t border-[#453f3b]/30">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-6 h-6 text-gray-400 flex-shrink-0" />
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
              className="flex-1 h-12 px-4 bg-[#453f3b] border-none rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 text-sm"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim()}
              className="w-12 h-12 bg-[#453f3b] hover:bg-[#524d48] disabled:bg-[#3a352f] disabled:cursor-not-allowed rounded-lg transition-colors flex items-center justify-center flex-shrink-0"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={() => onNavigate && onNavigate('dashboard')}
              className="px-4 h-12 bg-[#453f3b] hover:bg-[#524d48] text-white rounded-lg transition-colors text-sm font-medium whitespace-nowrap flex-shrink-0"
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
