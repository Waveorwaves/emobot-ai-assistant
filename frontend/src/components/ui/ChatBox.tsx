import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { useData } from '../../context/DataContext';

interface ChatBoxProps {
  className?: string;
  placeholder?: string;
  onSendMessage?: (message: string) => void;
  onOpenFullChat?: () => void;
  sidebarCollapsed?: boolean;
}

const ChatBox: React.FC<ChatBoxProps> = ({
  className = "",
  placeholder,
  onSendMessage,
  onOpenFullChat,
  sidebarCollapsed = false
}) => {
  const { emobotName, addChatMessage } = useData();
  const defaultPlaceholder = `Ask ${emobotName} anything...`;
  const finalPlaceholder = placeholder || defaultPlaceholder;
  const [message, setMessage] = useState('');

  const handleSendMessage = async () => {
    const trimmed = message.trim();
    if (!trimmed) return;

    setMessage('');

    try {
      await addChatMessage({
        content: trimmed,
        sender: 'user'
      });
    } catch (error) {
      console.error('Failed to send message', error);
    }

    if (onSendMessage) {
      onSendMessage(trimmed);
    }

    if (onOpenFullChat) {
      onOpenFullChat();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`fixed bottom-0 ${sidebarCollapsed ? 'left-20' : 'left-64'} right-0 glass-panel border-t border-primary-500/30 px-4 py-3 transition-all duration-300 ${className}`}>
      <div className="max-w-6xl mx-auto flex items-center gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={finalPlaceholder}
            className="w-full h-12 px-4 pr-12 bg-black/50 border border-primary-500/60 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          {message.trim() && (
            <button
              onClick={handleSendMessage}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-primary-400 hover:text-primary-300 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>

        <button
          onClick={onOpenFullChat}
          className="btn-neon-flow text-white px-4 py-2 rounded-lg flex items-center space-x-2 font-display font-semibold uppercase tracking-wide text-xs whitespace-nowrap"
        >
          Open Full Chat
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
