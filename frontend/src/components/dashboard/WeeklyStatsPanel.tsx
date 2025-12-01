import React from 'react';
import { TrendingUp, TrendingDown, Minus, Calendar, Clock } from 'lucide-react';
import { WeeklyStatsPanelProps } from '../../types/dashboard';

const WeeklyStatsPanel: React.FC<WeeklyStatsPanelProps> = ({
  weeklyStats,
  previousWeekComparison
}) => {
  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      case 'stable':
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTrendColor = (change: number) => {
    if (change > 0) return 'text-green-400';
    if (change < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  const getOnTimeColor = (percentage: number) => {
    if (percentage >= 95) return 'text-green-400';
    if (percentage >= 85) return 'text-yellow-400';
    return 'text-red-400';
  };

  const formatChange = (change: number, suffix: string = '%') => {
    const sign = change > 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}${suffix}`;
  };

  const completionRate = (weeklyStats.completedTasks / weeklyStats.totalTasks) * 100;

  return (
    <div className="glass-panel rounded-lg p-6 h-[250px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Weekly Performance</h3>
        <Calendar className="w-5 h-5 text-gray-400" />
      </div>

      {/* Main On-Time Metric */}
      <div className="text-center mb-4">
        <div className="flex items-center justify-center space-x-2 mb-1">
          <p className={`text-3xl font-bold ${getOnTimeColor(weeklyStats.onTimePercentage)}`}>
            {weeklyStats.onTimePercentage.toFixed(1)}%
          </p>
          {getTrendIcon(weeklyStats.trend)}
        </div>
        <p className="text-sm text-gray-400">On-Time Completion</p>

        {/* Trend Indicator */}
        <div className="flex items-center justify-center space-x-1 mt-1">
          <span className={`text-xs ${getTrendColor(previousWeekComparison.onTimeChange)}`}>
            {formatChange(previousWeekComparison.onTimeChange)} vs last week
          </span>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-3 gap-3">
        {/* Tasks Completed */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-1">
            <p className="text-lg font-bold text-white">
              {weeklyStats.completedTasks}
            </p>
            <span className={`text-xs ${getTrendColor(previousWeekComparison.taskChange)}`}>
              {previousWeekComparison.taskChange > 0 ? '+' : ''}{previousWeekComparison.taskChange}
            </span>
          </div>
          <p className="text-xs text-gray-400">Completed</p>

          {/* Completion Rate Bar */}
          <div className="mt-1 w-full bg-gray-700 rounded-full h-1">
            <div
              className={`h-1 rounded-full transition-all duration-300 ${completionRate >= 90 ? 'bg-green-500' :
                  completionRate >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
              style={{ width: `${Math.min(completionRate, 100)}%` }}
            />
          </div>
        </div>

        {/* Total Tasks */}
        <div className="text-center">
          <p className="text-lg font-bold text-white">
            {weeklyStats.totalTasks}
          </p>
          <p className="text-xs text-gray-400">Total Tasks</p>

          {/* Weekly Progress Indicator */}
          <div className="mt-1 flex justify-center space-x-0.5">
            {[...Array(7)].map((_, i) => (
              <div
                key={i}
                className={`w-1 h-2 rounded-sm ${i < 5 ? 'bg-blue-500' : 'bg-gray-600'
                  }`}
              />
            ))}
          </div>
        </div>

        {/* Avg Response */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-1">
            <p className="text-lg font-bold text-white">
              {weeklyStats.averageResponseTime}ms
            </p>
            <span className={`text-xs ${getTrendColor(-previousWeekComparison.responseTimeChange)}`}>
              {formatChange(previousWeekComparison.responseTimeChange, 'ms')}
            </span>
          </div>
          <p className="text-xs text-gray-400">Avg Response</p>

          {/* Response Time Indicator */}
          <div className="mt-1 flex items-center justify-center">
            <Clock className={`w-3 h-3 ${weeklyStats.averageResponseTime <= 500 ? 'text-green-400' :
                weeklyStats.averageResponseTime <= 1000 ? 'text-yellow-400' : 'text-red-400'
              }`} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeeklyStatsPanel;