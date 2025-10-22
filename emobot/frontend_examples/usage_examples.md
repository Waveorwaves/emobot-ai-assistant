# 前端集成使用示例

## React集成示例

### 1. 在主页面中嵌入聊天组件

```jsx
// src/pages/HomePage.jsx
import React from 'react';
import EmobotChatWidget from '../components/EmobotChatWidget';

const HomePage = () => {
  const handleMessageSent = (message) => {
    console.log('User sent:', message);
    // 可以在这里添加分析代码
  };

  const handleMessageReceived = (message) => {
    console.log('Bot replied:', message);
    // 可以在这里处理机器人回复
  };

  return (
    <div className="home-page">
      <header>
        <h1>Welcome to My App</h1>
      </header>
      
      <main>
        {/* 你的主要内容 */}
        <div className="content">
          <p>This is your main application content.</p>
        </div>
      </main>
      
      {/* Emobot聊天组件 */}
      <EmobotChatWidget
        apiBaseUrl="http://127.0.0.1:8000"
        onMessageSent={handleMessageSent}
        onMessageReceived={handleMessageReceived}
        className="my-chat-widget"
      />
    </div>
  );
};

export default HomePage;
```

### 2. 在仪表板页面中显示Agent数据

```jsx
// src/pages/DashboardPage.jsx
import React, { useState, useEffect } from 'react';
import EmobotAPI from '../services/EmobotAPI';

const DashboardPage = () => {
  const [agentStatus, setAgentStatus] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [statusData, analyticsData] = await Promise.all([
        EmobotAPI.getAgentStatus(),
        EmobotAPI.getAnalytics()
      ]);
      
      setAgentStatus(statusData);
      setAnalytics(analyticsData.analytics);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-page">
      <h1>AI Assistant Dashboard</h1>
      
      {/* Agent状态卡片 */}
      <div className="status-card">
        <h2>Agent Status</h2>
        <div className="status-info">
          <p><strong>Status:</strong> {agentStatus?.status}</p>
          <p><strong>Model:</strong> {agentStatus?.model_id}</p>
          <p><strong>Active Sessions:</strong> {agentStatus?.active_sessions}</p>
          <p><strong>Success Rate:</strong> {agentStatus?.execution_stats?.success_rate}%</p>
        </div>
      </div>

      {/* 分析数据卡片 */}
      <div className="analytics-card">
        <h2>Usage Analytics</h2>
        <div className="analytics-grid">
          <div className="metric">
            <span className="metric-value">
              {analytics?.overview?.total_interactions || 0}
            </span>
            <span className="metric-label">Total Interactions</span>
          </div>
          <div className="metric">
            <span className="metric-value">
              {analytics?.overview?.total_tool_calls || 0}
            </span>
            <span className="metric-label">Tool Calls</span>
          </div>
          <div className="metric">
            <span className="metric-value">
              {analytics?.tools?.most_used || 'None'}
            </span>
            <span className="metric-label">Most Used Tool</span>
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="actions">
        <button onClick={() => EmobotAPI.clearAgentMemory()}>
          Clear Memory
        </button>
        <button onClick={() => EmobotAPI.triggerReflection()}>
          Trigger Reflection
        </button>
        <button onClick={loadDashboardData}>
          Refresh Data
        </button>
      </div>
    </div>
  );
};

export default DashboardPage;
```

### 3. 工具管理页面

```jsx
// src/pages/ToolsPage.jsx
import React, { useState, useEffect } from 'react';
import EmobotAPI from '../services/EmobotAPI';

const ToolsPage = () => {
  const [tools, setTools] = useState([]);
  const [executingTool, setExecutingTool] = useState(null);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const data = await EmobotAPI.getTools();
      setTools(data.tools || []);
    } catch (error) {
      console.error('Failed to load tools:', error);
    }
  };

  const executeTool = async (toolName) => {
    setExecutingTool(toolName);
    try {
      const result = await EmobotAPI.executeTool(toolName, {});
      console.log('Tool execution result:', result);
      alert(`Tool ${toolName} executed successfully!`);
      await loadTools(); // 刷新工具状态
    } catch (error) {
      console.error('Tool execution failed:', error);
      alert(`Failed to execute ${toolName}: ${error.message}`);
    } finally {
      setExecutingTool(null);
    }
  };

  return (
    <div className="tools-page">
      <h1>AI Tools Management</h1>
      
      <div className="tools-grid">
        {tools.map(tool => (
          <div key={tool.name} className="tool-card">
            <div className="tool-header">
              <h3>{tool.name}</h3>
              <div className="tool-stats">
                <span>{tool.usage_stats?.calls || 0} calls</span>
                <span>{tool.usage_stats?.success_rate?.toFixed(1) || 0}% success</span>
              </div>
            </div>
            
            <p className="tool-description">{tool.description}</p>
            
            <div className="tool-parameters">
              <h4>Parameters:</h4>
              <ul>
                {Object.entries(tool.parameters?.properties || {}).map(([param, info]) => (
                  <li key={param}>
                    <strong>{param}:</strong> {info.description}
                    {tool.parameters?.required?.includes(param) && <span className="required">*</span>}
                  </li>
                ))}
              </ul>
            </div>
            
            <button 
              onClick={() => executeTool(tool.name)}
              disabled={executingTool === tool.name}
              className="execute-btn"
            >
              {executingTool === tool.name ? 'Executing...' : 'Execute Tool'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ToolsPage;
```

## Vue集成示例

### 1. 在Vue应用中使用仪表板组件

```vue
<!-- src/views/Dashboard.vue -->
<template>
  <div class="dashboard-view">
    <EmobotDashboard 
      :api-base-url="apiBaseUrl"
      :auto-refresh="true"
      :refresh-interval="30000"
    />
  </div>
</template>

<script>
import EmobotDashboard from '@/components/EmobotDashboard.vue';

export default {
  name: 'DashboardView',
  components: {
    EmobotDashboard
  },
  data() {
    return {
      apiBaseUrl: process.env.VUE_APP_EMOBOT_API_URL || 'http://127.0.0.1:8000'
    };
  }
};
</script>
```

### 2. 创建聊天页面

```vue
<!-- src/views/Chat.vue -->
<template>
  <div class="chat-view">
    <div class="chat-header">
      <h1>🤖 Chat with Emobot</h1>
      <div class="chat-controls">
        <button @click="clearHistory" class="btn-secondary">Clear History</button>
        <button @click="exportHistory" class="btn-secondary">Export History</button>
      </div>
    </div>
    
    <div class="chat-container">
      <div class="messages-area" ref="messagesArea">
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          class="message"
          :class="message.type"
        >
          <div class="message-content">
            {{ message.content }}
          </div>
          <div class="message-time">
            {{ formatTime(message.timestamp) }}
          </div>
          
          <!-- 显示推理步骤 -->
          <div v-if="message.reasoning_steps?.length" class="reasoning-steps">
            <details>
              <summary>View reasoning process</summary>
              <div class="steps-list">
                <div 
                  v-for="step in message.reasoning_steps" 
                  :key="step.step"
                  class="reasoning-step"
                  :class="`step-${step.type}`"
                >
                  <strong>Step {{ step.step }}:</strong> {{ step.message }}
                </div>
              </div>
            </details>
          </div>
        </div>
        
        <div v-if="isLoading" class="message bot loading">
          <div class="loading-indicator">
            <div class="loading-dots">
              <span></span><span></span><span></span>
            </div>
            <span>Thinking...</span>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <div class="input-container">
          <textarea
            v-model="inputMessage"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact="addNewLine"
            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
            :disabled="isLoading"
            ref="messageInput"
          ></textarea>
          <button 
            @click="sendMessage" 
            :disabled="isLoading || !inputMessage.trim()"
            class="send-button"
          >
            {{ isLoading ? '⏳' : '📤' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiConfig from '@/config/api';

export default {
  name: 'ChatView',
  data() {
    return {
      messages: [],
      inputMessage: '',
      isLoading: false,
      sessionId: `session_${Date.now()}`
    };
  },
  
  mounted() {
    this.addWelcomeMessage();
    this.$refs.messageInput?.focus();
  },
  
  methods: {
    addWelcomeMessage() {
      this.messages.push({
        type: 'bot',
        content: 'Hello! I\'m Emobot, your AI assistant. How can I help you today?',
        timestamp: new Date().toISOString()
      });
    },
    
    async sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return;
      
      const userMessage = {
        type: 'user',
        content: this.inputMessage,
        timestamp: new Date().toISOString()
      };
      
      this.messages.push(userMessage);
      this.isLoading = true;
      
      const messageToSend = this.inputMessage;
      this.inputMessage = '';
      
      try {
        const response = await fetch(`${apiConfig.baseURL}/api/chat/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: messageToSend,
            session_id: this.sessionId
          })
        });
        
        const data = await response.json();
        
        this.messages.push({
          type: 'bot',
          content: data.success ? data.response : `Error: ${data.error}`,
          timestamp: new Date().toISOString(),
          reasoning_steps: data.reasoning_steps || []
        });
        
      } catch (error) {
        console.error('Error sending message:', error);
        this.messages.push({
          type: 'bot',
          content: 'Sorry, I could not connect to the server. Please try again.',
          timestamp: new Date().toISOString()
        });
      } finally {
        this.isLoading = false;
        this.$nextTick(() => {
          this.scrollToBottom();
          this.$refs.messageInput?.focus();
        });
      }
    },
    
    addNewLine() {
      this.inputMessage += '\n';
    },
    
    clearHistory() {
      this.messages = [];
      this.addWelcomeMessage();
    },
    
    exportHistory() {
      const data = {
        session_id: this.sessionId,
        messages: this.messages,
        exported_at: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { 
        type: 'application/json' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat-history-${this.sessionId}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    
    scrollToBottom() {
      const messagesArea = this.$refs.messagesArea;
      if (messagesArea) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
  }
};
</script>

<style scoped>
/* 样式代码... */
</style>
```

## 环境配置

### React环境变量 (.env)

```bash
# .env
REACT_APP_EMOBOT_API_URL=http://127.0.0.1:8000
REACT_APP_EMOBOT_WS_URL=ws://127.0.0.1:8000
```

### Vue环境变量 (.env)

```bash
# .env
VUE_APP_EMOBOT_API_URL=http://127.0.0.1:8000
VUE_APP_EMOBOT_WS_URL=ws://127.0.0.1:8000
```

## 路由配置

### React Router

```jsx
// src/App.js
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import ToolsPage from './pages/ToolsPage';
import ChatPage from './pages/ChatPage';

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          <Link to="/">Home</Link>
          <Link to="/chat">Chat</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/tools">Tools</Link>
        </nav>
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tools" element={<ToolsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
```

### Vue Router

```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import Chat from '@/views/Chat.vue';
import Dashboard from '@/views/Dashboard.vue';
import Tools from '@/views/Tools.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/chat', name: 'Chat', component: Chat },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/tools', name: 'Tools', component: Tools }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
```

## 部署建议

### 开发环境启动顺序

1. 启动Emobot后端：
```bash
python enhanced_web_app.py --debug --port 8000
```

2. 启动前端开发服务器：
```bash
# React
npm start

# Vue
npm run serve
```

### 生产环境部署

1. 构建前端：
```bash
npm run build
```

2. 配置Nginx反向代理：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket代理
    location /socket.io/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

这样你就可以将Emobot完美集成到你现有的React或Vue应用中了！
