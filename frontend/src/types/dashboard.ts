// Dashboard Data Models and TypeScript Interfaces

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export interface ChatbotStatus {
  state: 'online' | 'offline' | 'busy' | 'maintenance';
  lastSeen: Date;
  responseTime: number;
  version: string;
  uptime: number;
}

export interface RuntimeMetrics {
  uptime: number; // seconds
  lastRestart: Date;
  uptimePercentage: number;
}

export interface InteractionMetrics {
  totalInteractions: number;
  avgResponseTime: number; // milliseconds
  dailyInteractions: number;
}

export interface AccuracyMetrics {
  accuracy: number; // percentage
  userSatisfaction: number; // percentage
  errorRate: number; // percentage
}

export interface PerformanceMetrics {
  runtime: RuntimeMetrics;
  interactions: InteractionMetrics;
  accuracy: AccuracyMetrics;
}

export interface Mission {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number; // 0-100
  startTime: Date;
  estimatedCompletion?: Date;
}

export interface WeeklyStats {
  onTimePercentage: number;
  totalTasks: number;
  completedTasks: number;
  averageResponseTime: number;
  trend: 'up' | 'down' | 'stable';
}

export interface WeeklyComparison {
  onTimeChange: number; // percentage change
  taskChange: number;
  responseTimeChange: number;
}

export interface DashboardState {
  status: ChatbotStatus;
  metrics: PerformanceMetrics;
  missions: Mission[];
  weeklyStats: WeeklyStats;
  weeklyComparison: WeeklyComparison;
  chatMessages: Message[];
  isLoading: boolean;
  lastUpdated: Date;
}

// Component Props Interfaces

export interface DashboardPageProps {
  initialMessages?: Message[];
  onNavigateToFullChat?: () => void;
  onNavigate?: (page: string) => void;
}

export interface SystemLogPageProps {
  initialMessages?: Message[];
  onNavigateToFullChat?: () => void;
  onNavigate?: (page: string) => void;
}

export interface StatusPanelProps {
  status: 'online' | 'offline' | 'busy' | 'maintenance';
  lastSeen?: Date;
  responseTime?: number;
}

export interface ChatPanelProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onExpandChat: () => void;
  maxVisibleMessages?: number;
}

export interface MetricsPanelProps {
  runtime: RuntimeMetrics;
  performance: {
    avgResponseTime: number;
    accuracy: number;
    totalInteractions: number;
  };
}

export interface MissionPanelProps {
  currentMissions: Mission[];
  completedToday: number;
  inProgress: number;
}

export interface WeeklyStatsPanelProps {
  weeklyStats: WeeklyStats;
  previousWeekComparison: WeeklyComparison;
}