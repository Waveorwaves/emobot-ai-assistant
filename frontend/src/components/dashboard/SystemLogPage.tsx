import React, { useState, useEffect } from 'react';
import {
  Activity,
  Wifi,
  WifiOff,
  CheckCircle,
  XCircle,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Brain,
  Mail,
  Calendar,
  Zap,
  Clock,
  Database,
  Server,
  RefreshCw
} from 'lucide-react';
import { SystemLogPageProps, DashboardState } from '../../types/dashboard';
import Sidebar from '../ui/Sidebar';
import ChatBox from '../ui/ChatBox';
import MissionPanel from './MissionPanel';
import WeeklyStatsPanel from './WeeklyStatsPanel';

interface ConnectionStatus {
  name: string;
  status: 'connected' | 'disconnected' | 'degraded';
  responseTime: number;
  lastCheck: Date;
  uptime: number;
  icon: React.ComponentType<{ className?: string }>;
}

interface NetworkMetrics {
  downloadSpeed: number;
  uploadSpeed: number;
  ping: number;
  trend: 'up' | 'down' | 'stable';
}

const SystemLogPage: React.FC<SystemLogPageProps> = ({
  initialMessages = [],
  onNavigateToFullChat,
  onNavigate
}) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('systemlog');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Network and API connection states - will be populated from backend
  const [networkMetrics, setNetworkMetrics] = useState<NetworkMetrics>({
    downloadSpeed: 0,
    uploadSpeed: 0,
    ping: 0,
    trend: 'stable'
  });

  // Dashboard data for missions and stats - will be populated from backend
  const [dashboardData, setDashboardData] = useState<DashboardState>({
    status: {
      state: 'online',
      lastSeen: new Date(),
      responseTime: 0,
      version: '2.1.0',
      uptime: 0
    },
    metrics: {
      runtime: {
        uptime: 0,
        lastRestart: new Date(),
        uptimePercentage: 0
      },
      interactions: {
        totalInteractions: 0,
        avgResponseTime: 0,
        dailyInteractions: 0
      },
      accuracy: {
        accuracy: 0,
        userSatisfaction: 0,
        errorRate: 0
      }
    },
    missions: [],
    weeklyStats: {
      onTimePercentage: 0,
      totalTasks: 0,
      completedTasks: 0,
      averageResponseTime: 0,
      trend: 'stable'
    },
    weeklyComparison: {
      onTimeChange: 0,
      taskChange: 0,
      responseTimeChange: 0
    },
    chatMessages: initialMessages,
    isLoading: false,
    lastUpdated: new Date()
  });

  const [apiConnections, setApiConnections] = useState<ConnectionStatus[]>([
    {
      name: 'Gemini API',
      status: 'disconnected',
      responseTime: 0,
      lastCheck: new Date(),
      uptime: 0,
      icon: Brain
    },
    {
      name: 'Email Service',
      status: 'disconnected',
      responseTime: 0,
      lastCheck: new Date(),
      uptime: 0,
      icon: Mail
    },
    {
      name: 'Calendar API',
      status: 'disconnected',
      responseTime: 0,
      lastCheck: new Date(),
      uptime: 0,
      icon: Calendar
    }
  ]);

  const handleToggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    try {
      localStorage.setItem('sidebarCollapsed', String(next));
    } catch { }
  };

  const handleSidebarNavigation = (page: string) => {
    setActiveTab(page);
    if (onNavigate && page !== 'systemlog') {
      onNavigate(page);
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Simulate API refresh
    setTimeout(() => {
      setIsRefreshing(false);
      // Update last check times
      setApiConnections(prev => prev.map(conn => ({
        ...conn,
        lastCheck: new Date()
      })));
    }, 1000);
  };

  // Real-time updates would be fetched from backend
  // useEffect(() => {
  //   const interval = setInterval(() => {
  //     // Fetch real metrics from backend
  //   }, 5000);
  //   return () => clearInterval(interval);
  // }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      case 'disconnected': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-900/20 border-green-500';
      case 'degraded': return 'bg-yellow-900/20 border-yellow-500';
      case 'disconnected': return 'bg-red-900/20 border-red-500';
      default: return 'bg-gray-900/20 border-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'disconnected': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="h-screen bg-transparent">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-64'} transition-all duration-300 flex flex-col h-screen`}>
        <div className="flex-1 bg-transparent overflow-y-auto pb-20">

          {/* Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary-500/10 border border-primary-500/60 rounded-lg shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                  <Server className="w-6 h-6 text-primary-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-display font-bold tracking-tight text-white">System Log</h1>
                </div>
              </div>
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center space-x-2 px-4 py-2 glass-button text-white rounded-lg transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {/* Network & System Health Section */}
          <div className="px-6 mb-6">
            <div className="glass-panel rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Activity className="w-5 h-5 text-green-400" />
                <h2 className="text-lg font-display font-bold tracking-tight text-white">Network & System Health</h2>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                {/* Download Speed */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Download</span>
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-baseline space-x-1">
                    <span className="text-2xl font-bold text-white">
                      {networkMetrics.downloadSpeed.toFixed(1)}
                    </span>
                    <span className="text-gray-400 text-xs">Mbps</span>
                  </div>
                </div>

                {/* Upload Speed */}
                <div className="bg-[#1e1e1e] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Upload</span>
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex items-baseline space-x-1">
                    <span className="text-2xl font-bold text-white">
                      {networkMetrics.uploadSpeed.toFixed(1)}
                    </span>
                    <span className="text-gray-400 text-xs">Mbps</span>
                  </div>
                </div>

                {/* Ping */}
                <div className="bg-[#1e1e1e] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Ping</span>
                    <Zap className="w-4 h-4 text-yellow-400" />
                  </div>
                  <div className="flex items-baseline space-x-1">
                    <span className="text-2xl font-bold text-white">
                      {networkMetrics.ping.toFixed(0)}
                    </span>
                    <span className="text-gray-400 text-xs">ms</span>
                  </div>
                </div>

                {/* Overall Status */}
                <div className="bg-[#1e1e1e] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Status</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="text-xl font-bold text-green-400">Healthy</div>
                </div>

                {/* Active Connections */}
                <div className="bg-[#1e1e1e] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Active APIs</span>
                    <Database className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="text-xl font-bold text-white">
                    {apiConnections.filter(c => c.status === 'connected').length}/{apiConnections.length}
                  </div>
                </div>

                {/* Avg Response Time */}
                <div className="bg-[#1e1e1e] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Avg Response</span>
                    <Zap className="w-4 h-4 text-yellow-400" />
                  </div>
                  <div className="text-xl font-bold text-white">
                    {Math.round(apiConnections.reduce((acc, c) => acc + c.responseTime, 0) / apiConnections.length)}ms
                  </div>
                </div>

                {/* Network Quality */}
                <div className="bg-[#1e1e1e] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Network Quality</span>
                    <Wifi className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="text-xl font-bold text-green-400">Excellent</div>
                </div>
              </div>
            </div>
          </div>

          {/* API Connections & System Logs Section */}
          <div className="px-6 mb-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

              {/* API Connections - Left Half */}
              <div className="glass-panel rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Database className="w-5 h-5 text-accent-400" />
                  <h2 className="text-lg font-display font-bold tracking-tight text-white">API Connections</h2>
                </div>

                <div className="space-y-4">
                  {apiConnections.map((connection, index) => {
                    const Icon = connection.icon;
                    return (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border-l-4 ${getStatusBg(connection.status)}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4 flex-1">
                            {/* Icon and Name */}
                            <div className="flex items-center space-x-3">
                              <Icon className={`w-6 h-6 ${getStatusColor(connection.status)}`} />
                              <div>
                                <h3 className="text-white font-medium">{connection.name}</h3>
                                <div className="flex items-center space-x-2 mt-1">
                                  {getStatusIcon(connection.status)}
                                  <span className={`text-sm capitalize ${getStatusColor(connection.status)}`}>
                                    {connection.status}
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Metrics */}
                            <div className="flex items-center space-x-4 ml-auto">
                              {/* Response Time */}
                              <div className="text-center">
                                <div className="text-xs text-gray-400 mb-1">Response Time</div>
                                <div className="text-white font-medium">{connection.responseTime}ms</div>
                              </div>

                              {/* Uptime */}
                              <div className="text-center">
                                <div className="text-xs text-gray-400 mb-1">Uptime</div>
                                <div className="text-green-400 font-medium">{connection.uptime}%</div>
                              </div>

                              {/* Last Check */}
                              <div className="text-center">
                                <div className="text-xs text-gray-400 mb-1">Last Check</div>
                                <div className="text-gray-300 text-sm flex items-center space-x-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{connection.lastCheck.toLocaleTimeString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Recent System Events - Right Half */}
              <div className="glass-panel rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Activity className="w-5 h-5 text-blue-400" />
                  <h2 className="text-lg font-display font-bold tracking-tight text-white">Recent System Events</h2>
                </div>

                <div className="space-y-3">
                  {/* Event 1 */}
                  <div className="p-3 bg-white/5 rounded-lg border-l-4 border-green-500">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
                        <div>
                          <h4 className="text-white text-sm font-medium">All APIs Connected</h4>
                          <p className="text-gray-400 text-xs mt-1">All API services are operational</p>
                        </div>
                      </div>
                      <span className="text-gray-500 text-xs">Just now</span>
                    </div>
                  </div>

                  {/* Event 2 */}
                  <div className="p-3 bg-white/5 rounded-lg border-l-4 border-blue-500">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <Wifi className="w-5 h-5 text-blue-400 mt-0.5" />
                        <div>
                          <h4 className="text-white text-sm font-medium">Network Speed Test Completed</h4>
                          <p className="text-gray-400 text-xs mt-1">Download: 125.4 Mbps, Upload: 45.2 Mbps</p>
                        </div>
                      </div>
                      <span className="text-gray-500 text-xs">2m ago</span>
                    </div>
                  </div>

                  {/* Event 3 */}
                  <div className="p-3 bg-white/5 rounded-lg border-l-4 border-accent-500">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <Brain className="w-5 h-5 text-accent-400 mt-0.5" />
                        <div>
                          <h4 className="text-white text-sm font-medium">Gemini API Response Optimized</h4>
                          <p className="text-gray-400 text-xs mt-1">Response time improved by 15ms</p>
                        </div>
                      </div>
                      <span className="text-gray-500 text-xs">5m ago</span>
                    </div>
                  </div>

                  {/* Event 4 */}
                  <div className="p-3 bg-white/5 rounded-lg border-l-4 border-yellow-500">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5" />
                        <div>
                          <h4 className="text-white text-sm font-medium">System Health Check</h4>
                          <p className="text-gray-400 text-xs mt-1">Scheduled maintenance in 24 hours</p>
                        </div>
                      </div>
                      <span className="text-gray-500 text-xs">10m ago</span>
                    </div>
                  </div>

                  {/* Event 5 */}
                  <div className="p-3 bg-white/5 rounded-lg border-l-4 border-green-500">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <Mail className="w-5 h-5 text-green-400 mt-0.5" />
                        <div>
                          <h4 className="text-white text-sm font-medium">Email Service Synced</h4>
                          <p className="text-gray-400 text-xs mt-1">12 new emails processed successfully</p>
                        </div>
                      </div>
                      <span className="text-gray-500 text-xs">15m ago</span>
                    </div>
                  </div>

                  {/* Event 6 */}
                  <div className="p-3 bg-white/5 rounded-lg border-l-4 border-blue-500">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <Calendar className="w-5 h-5 text-blue-400 mt-0.5" />
                        <div>
                          <h4 className="text-white text-sm font-medium">Calendar Events Updated</h4>
                          <p className="text-gray-400 text-xs mt-1">3 upcoming events synchronized</p>
                        </div>
                      </div>
                      <span className="text-gray-500 text-xs">20m ago</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Mission and Weekly Stats Panels */}
          <div className="px-6 pb-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Mission Panel */}
              <MissionPanel
                currentMissions={dashboardData.missions}
                completedToday={dashboardData.weeklyStats.completedTasks}
                inProgress={dashboardData.missions.filter(m => m.status === 'in_progress').length}
              />

              {/* Weekly Stats Panel */}
              <WeeklyStatsPanel
                weeklyStats={dashboardData.weeklyStats}
                previousWeekComparison={dashboardData.weeklyComparison}
              />
            </div>
          </div>
        </div>

        <ChatBox
          onSendMessage={(message) => console.log('System log chat:', message)}
          onOpenFullChat={() => onNavigateToFullChat && onNavigateToFullChat()}
          sidebarCollapsed={isCollapsed}
        />
      </div>
    </div>
  );
};

export default SystemLogPage;
