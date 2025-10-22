# React/Vue前端与Emobot集成指南

## 🎯 概述

本指南帮助你将现有的React或Vue.js前端应用与Emobot后端集成，实现：
- 聊天功能集成到主页面
- 其他页面通过API获取Agent数据
- 实时数据更新
- 完整的状态管理

## 🏗️ 架构设计

```
React/Vue Frontend (Port 3000)
├── /dashboard      → 仪表板 (Agent状态、分析数据)
├── /chat          → 聊天页面 (主要Emobot交互)
├── /analytics     → 数据分析 (Agent性能、用户模式)
├── /tools         → 工具管理 (查看和执行工具)
└── /settings      → 设置页面 (Agent配置)
                    ↕ HTTP/WebSocket
Enhanced Flask Backend (Port 8000)
├── /api/chat/*    → 聊天相关API
├── /api/agent/*   → Agent状态管理
├── /api/data/*    → 数据分析API
├── /api/tools/*   → 工具管理API
└── /api/ws        → WebSocket实时通信
```

## 🚀 快速开始

### 1. 启动增强版后端

```bash
# 安装额外依赖
pip install flask-socketio

# 启动增强版后端
python enhanced_web_app.py --model gemini-2.0-flash --port 8000
```

### 2. 前端配置

#### React项目配置

```javascript
// src/config/api.js
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000',
  WS_URL: 'ws://127.0.0.1:8000',
  ENDPOINTS: {
    // 聊天相关
    CHAT_MESSAGE: '/api/chat/message',
    CHAT_HISTORY: '/api/chat/history',
    CHAT_SESSIONS: '/api/chat/sessions',
    
    // Agent状态
    AGENT_STATUS: '/api/agent/status',
    AGENT_MEMORY_CLEAR: '/api/agent/memory/clear',
    AGENT_REFLECTION: '/api/agent/reflection',
    
    // 数据分析
    ANALYTICS: '/api/data/analytics',
    EXPORT_DATA: '/api/data/export',
    
    // 工具管理
    TOOLS_LIST: '/api/tools/list',
    TOOLS_EXECUTE: '/api/tools/execute',
    
    // 系统
    HEALTH: '/api/health',
    CONFIG: '/api/config'
  }
};
```

#### Vue项目配置

```javascript
// src/config/api.js
export default {
  baseURL: 'http://127.0.0.1:8000',
  wsURL: 'ws://127.0.0.1:8000',
  endpoints: {
    chat: {
      message: '/api/chat/message',
      history: '/api/chat/history',
      sessions: '/api/chat/sessions'
    },
    agent: {
      status: '/api/agent/status',
      memoryClear: '/api/agent/memory/clear',
      reflection: '/api/agent/reflection'
    },
    data: {
      analytics: '/api/data/analytics',
      export: '/api/data/export'
    },
    tools: {
      list: '/api/tools/list',
      execute: '/api/tools/execute'
    }
  }
};
```

## 📱 页面集成示例

### 1. 聊天页面集成 (React)

```jsx
// src/components/ChatPage.jsx
import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import { API_CONFIG } from '../config/api';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const socketRef = useRef(null);

  useEffect(() => {
    // 建立WebSocket连接
    socketRef.current = io(API_CONFIG.BASE_URL);
    
    socketRef.current.on('connect', () => {
      console.log('Connected to Emobot server');
      socketRef.current.emit('join_session', { session_id: sessionId });
    });

    socketRef.current.on('new_message', (data) => {
      if (data.session_id === sessionId && data.type === 'bot') {
        setMessages(prev => [...prev, {
          type: 'bot',
          content: data.message,
          timestamp: new Date().toISOString()
        }]);
      }
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, [sessionId]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT_MESSAGE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setMessages(prev => [...prev, {
          type: 'bot',
          content: data.response,
          timestamp: new Date().toISOString(),
          reasoning_steps: data.reasoning_steps
        }]);
      } else {
        setMessages(prev => [...prev, {
          type: 'bot',
          content: `Error: ${data.error}`,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        type: 'bot',
        content: 'Sorry, I could not connect to the server.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
      setInputMessage('');
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1>🤖 Emobot Chat</h1>
      </div>
      
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="message-content">
              {msg.content}
            </div>
            <div className="message-time">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot loading">
            <div className="loading-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
      </div>
      
      <div className="chat-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
```

### 2. 仪表板页面集成 (Vue)

```vue
<!-- src/components/Dashboard.vue -->
<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>📊 Emobot Dashboard</h1>
      <div class="status-indicator" :class="agentStatus.status">
        {{ agentStatus.status }}
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Agent状态卡片 -->
      <div class="card agent-status">
        <h3>🤖 Agent Status</h3>
        <div class="status-details">
          <p><strong>Model:</strong> {{ agentStatus.model_id }}</p>
          <p><strong>Active Sessions:</strong> {{ agentStatus.active_sessions }}</p>
          <p><strong>Memory Entries:</strong> {{ agentStatus.memory_stats?.short_term_size || 0 }}</p>
          <p><strong>Success Rate:</strong> {{ agentStatus.execution_stats?.success_rate || 0 }}%</p>
        </div>
        <button @click="clearMemory" class="btn-secondary">Clear Memory</button>
      </div>

      <!-- 分析数据卡片 -->
      <div class="card analytics">
        <h3>📈 Analytics</h3>
        <div class="analytics-data">
          <div class="metric">
            <span class="metric-value">{{ analytics.overview?.total_interactions || 0 }}</span>
            <span class="metric-label">Total Interactions</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ analytics.overview?.total_tool_calls || 0 }}</span>
            <span class="metric-label">Tool Calls</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ analytics.tools?.most_used || 'None' }}</span>
            <span class="metric-label">Most Used Tool</span>
          </div>
        </div>
      </div>

      <!-- 工具状态卡片 -->
      <div class="card tools-status">
        <h3>🔧 Tools</h3>
        <div class="tools-list">
          <div v-for="tool in tools" :key="tool.name" class="tool-item">
            <span class="tool-name">{{ tool.name }}</span>
            <span class="tool-usage">{{ tool.usage_stats?.calls || 0 }} calls</span>
            <button @click="executeTool(tool.name)" class="btn-small">Execute</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiConfig from '../config/api';

export default {
  name: 'Dashboard',
  data() {
    return {
      agentStatus: {},
      analytics: {},
      tools: [],
      refreshInterval: null
    };
  },
  
  async mounted() {
    await this.loadDashboardData();
    this.startAutoRefresh();
  },
  
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  
  methods: {
    async loadDashboardData() {
      try {
        // 并行加载所有数据
        const [statusRes, analyticsRes, toolsRes] = await Promise.all([
          fetch(`${apiConfig.baseURL}${apiConfig.endpoints.agent.status}`),
          fetch(`${apiConfig.baseURL}${apiConfig.endpoints.data.analytics}`),
          fetch(`${apiConfig.baseURL}${apiConfig.endpoints.tools.list}`)
        ]);

        if (statusRes.ok) {
          this.agentStatus = await statusRes.json();
        }
        
        if (analyticsRes.ok) {
          const analyticsData = await analyticsRes.json();
          this.analytics = analyticsData.analytics || {};
        }
        
        if (toolsRes.ok) {
          const toolsData = await toolsRes.json();
          this.tools = toolsData.tools || [];
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      }
    },

    async clearMemory() {
      try {
        const response = await fetch(`${apiConfig.baseURL}${apiConfig.endpoints.agent.memoryClear}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: 'short_term' })
        });
        
        if (response.ok) {
          this.$toast.success('Memory cleared successfully');
          await this.loadDashboardData();
        }
      } catch (error) {
        console.error('Error clearing memory:', error);
        this.$toast.error('Failed to clear memory');
      }
    },

    async executeTool(toolName) {
      try {
        const response = await fetch(`${apiConfig.baseURL}${apiConfig.endpoints.tools.execute}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            tool_name: toolName,
            parameters: {}
          })
        });
        
        if (response.ok) {
          const result = await response.json();
          this.$toast.success(`Tool ${toolName} executed successfully`);
          console.log('Tool result:', result);
        }
      } catch (error) {
        console.error('Error executing tool:', error);
        this.$toast.error(`Failed to execute ${toolName}`);
      }
    },

    startAutoRefresh() {
      this.refreshInterval = setInterval(() => {
        this.loadDashboardData();
      }, 30000); // 每30秒刷新一次
    }
  }
};
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.status-indicator {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  text-transform: uppercase;
}

.status-indicator.active {
  background: #4CAF50;
  color: white;
}

.status-indicator.error {
  background: #f44336;
  color: white;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card h3 {
  margin-bottom: 15px;
  color: #333;
}

.status-details p {
  margin: 8px 0;
}

.analytics-data {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.metric {
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
}

.metric-label {
  font-size: 12px;
  color: #666;
}

.tool-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.btn-secondary, .btn-small {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #667eea;
  color: white;
}

.btn-small {
  background: #f0f0f0;
  color: #333;
  padding: 4px 8px;
  font-size: 12px;
}
</style>
```

### 3. API客户端封装

```javascript
// src/services/EmobotAPI.js
import { API_CONFIG } from '../config/api';

class EmobotAPI {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // 聊天相关
  async sendMessage(message, sessionId = 'default') {
    return this.request(API_CONFIG.ENDPOINTS.CHAT_MESSAGE, {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId })
    });
  }

  async getChatHistory(sessionId) {
    return this.request(`${API_CONFIG.ENDPOINTS.CHAT_HISTORY}/${sessionId}`);
  }

  async getChatSessions() {
    return this.request(API_CONFIG.ENDPOINTS.CHAT_SESSIONS);
  }

  // Agent状态
  async getAgentStatus() {
    return this.request(API_CONFIG.ENDPOINTS.AGENT_STATUS);
  }

  async clearAgentMemory(type = 'short_term') {
    return this.request(API_CONFIG.ENDPOINTS.AGENT_MEMORY_CLEAR, {
      method: 'POST',
      body: JSON.stringify({ type })
    });
  }

  async triggerReflection() {
    return this.request(API_CONFIG.ENDPOINTS.AGENT_REFLECTION, {
      method: 'POST'
    });
  }

  // 数据分析
  async getAnalytics() {
    return this.request(API_CONFIG.ENDPOINTS.ANALYTICS);
  }

  async exportData(type = 'all') {
    return this.request(`${API_CONFIG.ENDPOINTS.EXPORT_DATA}?type=${type}`);
  }

  // 工具管理
  async getTools() {
    return this.request(API_CONFIG.ENDPOINTS.TOOLS_LIST);
  }

  async executeTool(toolName, parameters = {}) {
    return this.request(API_CONFIG.ENDPOINTS.TOOLS_EXECUTE, {
      method: 'POST',
      body: JSON.stringify({ tool_name: toolName, parameters })
    });
  }

  // 系统
  async healthCheck() {
    return this.request(API_CONFIG.ENDPOINTS.HEALTH);
  }

  async getConfig() {
    return this.request(API_CONFIG.ENDPOINTS.CONFIG);
  }
}

export default new EmobotAPI();
```

## 🔄 实时数据更新

### WebSocket集成 (React Hook)

```javascript
// src/hooks/useEmobotWebSocket.js
import { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';
import { API_CONFIG } from '../config/api';

export const useEmobotWebSocket = (sessionId = 'default') => {
  const [isConnected, setIsConnected] = useState(false);
  const [agentStatus, setAgentStatus] = useState(null);
  const [messages, setMessages] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    // 建立连接
    socketRef.current = io(API_CONFIG.BASE_URL);

    socketRef.current.on('connect', () => {
      setIsConnected(true);
      socketRef.current.emit('join_session', { session_id: sessionId });
    });

    socketRef.current.on('disconnect', () => {
      setIsConnected(false);
    });

    socketRef.current.on('new_message', (data) => {
      if (data.session_id === sessionId) {
        setMessages(prev => [...prev, data]);
      }
    });

    socketRef.current.on('agent_status', (status) => {
      setAgentStatus(status);
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, [sessionId]);

  const requestAgentStatus = () => {
    if (socketRef.current) {
      socketRef.current.emit('agent_status_request');
    }
  };

  const joinSession = (newSessionId) => {
    if (socketRef.current) {
      socketRef.current.emit('join_session', { session_id: newSessionId });
    }
  };

  return {
    isConnected,
    agentStatus,
    messages,
    requestAgentStatus,
    joinSession
  };
};
```

## 📦 依赖安装

### 后端依赖

```bash
pip install flask-socketio
```

### 前端依赖

#### React
```bash
npm install socket.io-client axios
```

#### Vue
```bash
npm install socket.io-client axios
```

## 🚀 部署建议

### 开发环境
```bash
# 后端
python enhanced_web_app.py --debug --port 8000

# 前端 (React)
npm start

# 前端 (Vue)
npm run serve
```

### 生产环境
```bash
# 后端
gunicorn -k eventlet -w 1 enhanced_web_app:app --bind 0.0.0.0:8000

# 前端构建
npm run build
```

## 🔧 高级功能

### 1. 状态管理集成 (Redux/Vuex)

### 2. 错误处理和重试机制

### 3. 缓存策略

### 4. 性能优化

### 5. 安全考虑

详细实现请参考项目中的示例代码。

## 📞 支持

如有问题，请查看：
- API文档：`http://127.0.0.1:8000/api/health`
- WebSocket事件列表
- 错误代码参考
