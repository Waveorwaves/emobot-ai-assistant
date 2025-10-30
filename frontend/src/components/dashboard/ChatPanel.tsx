import React, { useState, useRef, useEffect } from 'react';
import { Send, Maximize2, MoreHorizontal } from 'lucide-react';
import { ChatPanelProps } from '../../types/dashboard';

const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onSendMessage,
  onExpandChat,
  maxVisibleMessages = 5
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim()) {
      setIsTyping(true);
      onSendMessage(inputValue.trim());
      setInputValue('');
      
      // Simulate typing indicator
      setTimeout(() => {
        setIsTyping(false);
      }, 2000);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const visibleMessages = messages.slice(-maxVisibleMessages);
  const hasMoreMessages = messages.length > maxVisibleMessages;

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  return (
    <div className="bg-[#453f3b] rounded-lg p-6 h-[300px] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Quick Chat</h3>
        <div className="flex space-x-2">
          {hasMoreMessages && (
            <button
              onClick={onExpandChat}
              className="p-1 text-gray-400 hover:text-white transition-colors"
              title={`${messages.length - maxVisibleMessages} more messages`}
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onExpandChat}
            className="p-1 text-gray-400 hover:text-white transition-colors"
            title="Expand to full chat"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4 min-h-0">
        {hasMoreMessages && (
          <div className="text-center">
            <button
              onClick={onExpandChat}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              +{messages.length - maxVisibleMessages} more messages
            </button>
          </div>
        )}

        {visibleMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-400 text-sm">No messages yet. Start a conversation!</p>
          </div>
        ) : (
          visibleMessages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`
                  max-w-[80%] px-3 py-2 rounded-lg text-sm
                  ${message.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-[#1e1e1e] text-gray-100 border border-gray-600'
                  }
                `}
              >
                <p className="break-words">{message.text}</p>
                <p className={`
                  text-xs mt-1 opacity-70
                  ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-400'}
                `}>
                  {formatTimestamp(message.timestamp)}
                </p>
              </div>
            </div>
          ))
        )}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-[#1e1e1e] border border-gray-600 px-3 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex items-center space-x-2">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className="flex-1 px-3 py-2 bg-[#1e1e1e] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          disabled={isTyping}
        />
        <button
          onClick={handleSend}
          disabled={!inputValue.trim() || isTyping}
          className={`
            p-2 rounded-lg transition-all duration-200
            ${inputValue.trim() && !isTyping
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;