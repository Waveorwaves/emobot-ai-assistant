<!--
  Emobot Dashboard Component - Vue 3
  完整的仪表板组件，显示Agent状态、分析数据和工具管理
-->

<template>
  <div class="emobot-dashboard">
    <!-- 头部 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1>🤖 Emobot Dashboard</h1>
        <p class="subtitle">Monitor and manage your AI assistant</p>
      </div>
      <div class="header-right">
        <div class="status-badge" :class="agentStatus.status">
          <div class="status-dot"></div>
          {{ agentStatus.status || 'Unknown' }}
        </div>
        <button @click="refreshData" :disabled="isLoading" class="refresh-btn">
          <span :class="{ 'spinning': isLoading }">🔄</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- 主要指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">💬</div>
        <div class="metric-content">
          <div class="metric-value">{{ analytics.overview?.total_interactions || 0 }}</div>
          <div class="metric-label">Total Interactions</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">🎯</div>
        <div class="metric-content">
          <div class="metric-value">{{ agentStatus.execution_stats?.success_rate || 0 }}%</div>
          <div class="metric-label">Success Rate</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">🧠</div>
        <div class="metric-content">
          <div class="metric-value">{{ agentStatus.memory_stats?.short_term_size || 0 }}</div>
          <div class="metric-label">Memory Entries</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">🔧</div>
        <div class="metric-content">
          <div class="metric-value">{{ tools.length }}</div>
          <div class="metric-label">Available Tools</div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="dashboard-content">
      <!-- Agent状态面板 -->
      <div class="panel agent-panel">
        <div class="panel-header">
          <h3>🤖 Agent Status</h3>
          <div class="panel-actions">
            <button @click="clearMemory" class="btn-secondary">Clear Memory</button>
            <button @click="triggerReflection" class="btn-secondary">Reflect</button>
          </div>
        </div>
        
        <div class="panel-content">
          <div class="status-grid">
            <div class="status-item">
              <label>Model:</label>
              <span>{{ agentStatus.model_id || 'Unknown' }}</span>
            </div>
            <div class="status-item">
              <label>Active Sessions:</label>
              <span>{{ agentStatus.active_sessions || 0 }}</span>
            </div>
            <div class="status-item">
              <label>Server URL:</label>
              <span>{{ agentStatus.server_url || 'N/A' }}</span>
            </div>
            <div class="status-item">
              <label>Last Update:</label>
              <span>{{ formatTime(agentStatus.timestamp) }}</span>
            </div>
          </div>

          <!-- 内存统计 -->
          <div class="memory-stats" v-if="agentStatus.memory_stats">
            <h4>Memory Statistics</h4>
            <div class="memory-grid">
              <div class="memory-item">
                <span class="memory-label">Short-term:</span>
                <span class="memory-value">{{ agentStatus.memory_stats.short_term_size }}</span>
              </div>
              <div class="memory-item">
                <span class="memory-label">Episodic:</span>
                <span class="memory-value">{{ agentStatus.memory_stats.episodic_count }}</span>
              </div>
              <div class="memory-item">
                <span class="memory-label">Working Keys:</span>
                <span class="memory-value">{{ agentStatus.memory_stats.working_memory_keys?.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 工具管理面板 -->
      <div class="panel tools-panel">
        <div class="panel-header">
          <h3>🔧 Tools Management</h3>
          <div class="panel-actions">
            <button @click="refreshTools" class="btn-secondary">Refresh Tools</button>
          </div>
        </div>
        
        <div class="panel-content">
          <div class="tools-list">
            <div 
              v-for="tool in tools" 
              :key="tool.name" 
              class="tool-item"
              :class="{ 'tool-active': tool.usage_stats?.calls > 0 }"
            >
              <div class="tool-info">
                <div class="tool-name">{{ tool.name }}</div>
                <div class="tool-description">{{ tool.description }}</div>
                <div class="tool-stats">
                  <span class="stat">{{ tool.usage_stats?.calls || 0 }} calls</span>
                  <span class="stat">{{ tool.usage_stats?.success_rate?.toFixed(1) || 0 }}% success</span>
                  <span class="stat">{{ tool.usage_stats?.average_time?.toFixed(2) || 0 }}s avg</span>
                </div>
              </div>
              <div class="tool-actions">
                <button 
                  @click="executeTool(tool.name)" 
                  :disabled="isExecutingTool === tool.name"
                  class="btn-small"
                >
                  {{ isExecutingTool === tool.name ? '⏳' : '▶️' }}
                  Execute
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分析数据面板 -->
      <div class="panel analytics-panel">
        <div class="panel-header">
          <h3>📊 Analytics</h3>
          <div class="panel-actions">
            <button @click="exportData" class="btn-secondary">Export Data</button>
          </div>
        </div>
        
        <div class="panel-content">
          <!-- 用户模式 -->
          <div class="analytics-section" v-if="analytics.user_patterns">
            <h4>User Patterns</h4>
            <div class="patterns-grid">
              <div class="pattern-item" v-if="analytics.user_patterns.most_used_intents?.length">
                <label>Most Used Intents:</label>
                <div class="intent-list">
                  <span 
                    v-for="[intent, count] in analytics.user_patterns.most_used_intents.slice(0, 3)" 
                    :key="intent"
                    class="intent-tag"
                  >
                    {{ intent }} ({{ count }})
                  </span>
                </div>
              </div>
              
              <div class="pattern-item" v-if="analytics.user_patterns.active_hours?.length">
                <label>Active Hours:</label>
                <div class="hours-list">
                  <span 
                    v-for="hour in analytics.user_patterns.active_hours.slice(0, 5)" 
                    :key="hour"
                    class="hour-tag"
                  >
                    {{ hour }}:00
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 工具使用统计 -->
          <div class="analytics-section" v-if="analytics.tools">
            <h4>Tool Usage</h4>
            <div class="tool-analytics">
              <div class="most-used-tool">
                <label>Most Used Tool:</label>
                <span class="tool-highlight">{{ analytics.tools.most_used || 'None' }}</span>
              </div>
              
              <div class="tool-stats-chart" v-if="analytics.tools.tool_stats">
                <div 
                  v-for="[toolName, stats] in Object.entries(analytics.tools.tool_stats).slice(0, 5)" 
                  :key="toolName"
                  class="tool-stat-bar"
                >
                  <span class="tool-stat-name">{{ toolName }}</span>
                  <div class="tool-stat-progress">
                    <div 
                      class="tool-stat-fill" 
                      :style="{ width: `${(stats.calls / maxToolCalls) * 100}%` }"
                    ></div>
                  </div>
                  <span class="tool-stat-count">{{ stats.calls }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading dashboard data...</p>
      </div>
    </div>

    <!-- 通知 -->
    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmobotDashboard',
  
  props: {
    apiBaseUrl: {
      type: String,
      default: 'http://127.0.0.1:8000'
    },
    autoRefresh: {
      type: Boolean,
      default: true
    },
    refreshInterval: {
      type: Number,
      default: 30000 // 30秒
    }
  },

  data() {
    return {
      agentStatus: {},
      analytics: {},
      tools: [],
      isLoading: false,
      isExecutingTool: null,
      notification: null,
      refreshTimer: null
    };
  },

  computed: {
    maxToolCalls() {
      if (!this.analytics.tools?.tool_stats) return 1;
      const counts = Object.values(this.analytics.tools.tool_stats).map(s => s.calls);
      return Math.max(...counts, 1);
    }
  },

  async mounted() {
    await this.loadDashboardData();
    
    if (this.autoRefresh) {
      this.startAutoRefresh();
    }
  },

  beforeUnmount() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  },

  methods: {
    async loadDashboardData() {
      this.isLoading = true;
      
      try {
        const [statusRes, analyticsRes, toolsRes] = await Promise.all([
          fetch(`${this.apiBaseUrl}/api/agent/status`),
          fetch(`${this.apiBaseUrl}/api/data/analytics`),
          fetch(`${this.apiBaseUrl}/api/tools/list`)
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
        this.showNotification('Failed to load dashboard data', 'error');
      } finally {
        this.isLoading = false;
      }
    },

    async refreshData() {
      await this.loadDashboardData();
      this.showNotification('Dashboard data refreshed', 'success');
    },

    async refreshTools() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/tools/list`);
        if (response.ok) {
          const data = await response.json();
          this.tools = data.tools || [];
          this.showNotification('Tools refreshed', 'success');
        }
      } catch (error) {
        console.error('Error refreshing tools:', error);
        this.showNotification('Failed to refresh tools', 'error');
      }
    },

    async clearMemory() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/agent/memory/clear`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: 'short_term' })
        });
        
        if (response.ok) {
          this.showNotification('Memory cleared successfully', 'success');
          await this.loadDashboardData();
        }
      } catch (error) {
        console.error('Error clearing memory:', error);
        this.showNotification('Failed to clear memory', 'error');
      }
    },

    async triggerReflection() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/agent/reflection`, {
          method: 'POST'
        });
        
        if (response.ok) {
          const data = await response.json();
          this.showNotification('Agent reflection completed', 'success');
          console.log('Reflection result:', data.reflection);
        }
      } catch (error) {
        console.error('Error triggering reflection:', error);
        this.showNotification('Failed to trigger reflection', 'error');
      }
    },

    async executeTool(toolName) {
      this.isExecutingTool = toolName;
      
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/tools/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            tool_name: toolName,
            parameters: {}
          })
        });
        
        if (response.ok) {
          const result = await response.json();
          this.showNotification(`Tool ${toolName} executed successfully`, 'success');
          console.log('Tool result:', result);
          await this.refreshTools();
        }
      } catch (error) {
        console.error('Error executing tool:', error);
        this.showNotification(`Failed to execute ${toolName}`, 'error');
      } finally {
        this.isExecutingTool = null;
      }
    },

    async exportData() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/data/export?type=all`);
        if (response.ok) {
          const data = await response.json();
          
          // 创建下载链接
          const blob = new Blob([JSON.stringify(data.data, null, 2)], { 
            type: 'application/json' 
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `emobot-data-${new Date().toISOString().split('T')[0]}.json`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
          
          this.showNotification('Data exported successfully', 'success');
        }
      } catch (error) {
        console.error('Error exporting data:', error);
        this.showNotification('Failed to export data', 'error');
      }
    },

    startAutoRefresh() {
      this.refreshTimer = setInterval(() => {
        this.loadDashboardData();
      }, this.refreshInterval);
    },

    showNotification(message, type = 'info') {
      this.notification = { message, type };
      setTimeout(() => {
        this.notification = null;
      }, 3000);
    },

    formatTime(timestamp) {
      if (!timestamp) return 'N/A';
      return new Date(timestamp).toLocaleString();
    }
  }
};
</script>

<style scoped>
.emobot-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
}

/* 头部样式 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.header-left h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.subtitle {
  margin: 4px 0 0 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 14px;
  text-transform: capitalize;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.error {
  background: #ffebee;
  color: #c62828;
}

.status-badge.not_initialized {
  background: #fff3e0;
  color: #ef6c00;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 指标卡片网格 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.metric-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

/* 主要内容区域 */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.btn-secondary, .btn-small {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-secondary:hover, .btn-small:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.btn-small {
  padding: 4px 12px;
  font-size: 12px;
}

.panel-content {
  padding: 20px;
}

/* Agent面板特定样式 */
.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item label {
  font-weight: 500;
  color: #666;
}

.memory-stats h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
}

.memory-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.memory-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.memory-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.memory-value {
  font-size: 18px;
  font-weight: bold;
  color: #667eea;
}

/* 工具面板特定样式 */
.tools-list {
  max-height: 400px;
  overflow-y: auto;
}

.tool-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.tool-item:hover {
  background: #f8f9fa;
}

.tool-item.tool-active {
  border-left: 4px solid #667eea;
}

.tool-info {
  flex: 1;
}

.tool-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.tool-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.tool-stats {
  display: flex;
  gap: 16px;
}

.stat {
  font-size: 12px;
  color: #888;
}

/* 分析面板特定样式 */
.analytics-panel {
  grid-column: 1 / -1;
}

.analytics-section {
  margin-bottom: 32px;
}

.analytics-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
}

.patterns-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.pattern-item label {
  display: block;
  font-weight: 500;
  color: #666;
  margin-bottom: 8px;
}

.intent-list, .hours-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.intent-tag, .hour-tag {
  padding: 4px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.hour-tag {
  background: #f3e5f5;
  color: #7b1fa2;
}

.most-used-tool {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.tool-highlight {
  padding: 4px 12px;
  background: #667eea;
  color: white;
  border-radius: 16px;
  font-weight: 500;
}

.tool-stats-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tool-stat-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-stat-name {
  width: 120px;
  font-size: 14px;
  color: #666;
}

.tool-stat-progress {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.tool-stat-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.tool-stat-count {
  width: 40px;
  text-align: right;
  font-size: 14px;
  color: #666;
}

/* 加载和通知样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1001;
  animation: slideInRight 0.3s ease;
}

.notification.success {
  background: #4caf50;
}

.notification.error {
  background: #f44336;
}

.notification.info {
  background: #2196f3;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
  
  .analytics-panel {
    grid-column: 1;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .patterns-grid {
    grid-template-columns: 1fr;
  }
}
</style>
