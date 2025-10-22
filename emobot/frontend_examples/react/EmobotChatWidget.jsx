/**
 * Emobot Chat Widget - React Component
 * 可以嵌入到任何React页面的聊天组件
 */

import React, { useState, useEffect, useRef } from 'react';
import './EmobotChatWidget.css';

const EmobotChatWidget = ({ 
  apiBaseUrl = 'http://127.0.0.1:8000',
  sessionId = null,
  onMessageSent = null,
  onMessageReceived = null,
  className = '',
  minimized = false 
}) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(minimized);
  const [currentSessionId] = useState(sessionId || `session_${Date.now()}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // 添加欢迎消息
    setMessages([{
      type: 'bot',
      content: 'Hello! I\'m Emobot, your AI assistant. How can I help you today?',
      timestamp: new Date().toISOString()
    }]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    
    // 调用回调
    if (onMessageSent) {
      onMessageSent(userMessage);
    }

    setIsLoading(true);
    const messageToSend = inputMessage;
    setInputMessage('');

    try {
      const response = await fetch(`${apiBaseUrl}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageToSend,
          session_id: currentSessionId
        })
      });

      const data = await response.json();
      
      const botMessage = {
        type: 'bot',
        content: data.success ? data.response : `Error: ${data.error}`,
        timestamp: new Date().toISOString(),
        reasoning_steps: data.reasoning_steps || []
      };

      setMessages(prev => [...prev, botMessage]);
      
      // 调用回调
      if (onMessageReceived) {
        onMessageReceived(botMessage);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'bot',
        content: 'Sorry, I could not connect to the server. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`emobot-chat-widget ${className} ${isMinimized ? 'minimized' : ''}`}>
      {/* 聊天头部 */}
      <div className="chat-header" onClick={toggleMinimize}>
        <div className="header-content">
          <div className="bot-avatar">🤖</div>
          <div className="header-text">
            <h3>Emobot</h3>
            <span className="status">Online</span>
          </div>
        </div>
        <button className="minimize-btn">
          {isMinimized ? '▲' : '▼'}
        </button>
      </div>

      {/* 聊天内容 */}
      {!isMinimized && (
        <>
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                <div className="message-content">
                  {message.content}
                </div>
                <div className="message-time">
                  {formatTime(message.timestamp)}
                </div>
                {message.reasoning_steps && message.reasoning_steps.length > 0 && (
                  <details className="reasoning-steps">
                    <summary>View reasoning steps</summary>
                    <div className="steps-content">
                      {message.reasoning_steps.map((step, stepIndex) => (
                        <div key={stepIndex} className={`step step-${step.type}`}>
                          <strong>Step {step.step}:</strong> {step.message}
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="message bot loading">
                <div className="loading-indicator">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="loading-text">Thinking...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="chat-input">
            <div className="input-container">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
                disabled={isLoading}
                rows="1"
                className="message-input"
              />
              <button 
                onClick={sendMessage} 
                disabled={isLoading || !inputMessage.trim()}
                className="send-button"
              >
                {isLoading ? '⏳' : '📤'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default EmobotChatWidget;
