import React from 'react';
import { Clock, Zap, Target, Activity } from 'lucide-react';
import { MetricsPanelProps } from '../../types/dashboard';

const MetricsPanel: React.FC<MetricsPanelProps> = ({
  runtime,
  performance
}) => {
  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}d ${hours}h`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const getUptimeColor = (percentage: number) => {
    if (percentage >= 99) return 'text-green-400';
    if (percentage >= 95) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getResponseTimeColor = (ms: number) => {
    if (ms <= 500) return 'text-green-400';
    if (ms <= 1000) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getAccuracyColor = (percentage: number) => {
    if (percentage >= 95) return 'text-green-400';
    if (percentage >= 90) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="glass-panel rounded-lg p-6 h-[300px] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Performance</h3>
        <Activity className="w-5 h-5 text-gray-400" />
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 h-[140px]">
        {/* Uptime */}
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Uptime</span>
          </div>
          <div className="space-y-1">
            <p className="text-lg font-bold text-white">
              {formatUptime(runtime.uptime)}
            </p>
            <p className={`text-sm font-medium ${getUptimeColor(runtime.uptimePercentage)}`}>
              {runtime.uptimePercentage.toFixed(1)}%
            </p>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full transition-all duration-300 ${runtime.uptimePercentage >= 99 ? 'bg-green-500' :
                    runtime.uptimePercentage >= 95 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                style={{ width: `${Math.min(runtime.uptimePercentage, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Response Time */}
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Response</span>
          </div>
          <div className="space-y-1">
            <p className="text-lg font-bold text-white">
              {performance.avgResponseTime}ms
            </p>
            <p className={`text-sm font-medium ${getResponseTimeColor(performance.avgResponseTime)}`}>
              {performance.avgResponseTime <= 500 ? 'Excellent' :
                performance.avgResponseTime <= 1000 ? 'Good' : 'Slow'}
            </p>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full transition-all duration-300 ${performance.avgResponseTime <= 500 ? 'bg-green-500' :
                    performance.avgResponseTime <= 1000 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                style={{
                  width: `${Math.max(20, Math.min(100, 100 - (performance.avgResponseTime / 20)))}%`
                }}
              />
            </div>
          </div>
        </div>

        {/* Accuracy */}
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Target className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Accuracy</span>
          </div>
          <div className="space-y-1">
            <p className="text-lg font-bold text-white">
              {performance.accuracy.toFixed(1)}%
            </p>
            <p className={`text-sm font-medium ${getAccuracyColor(performance.accuracy)}`}>
              {performance.accuracy >= 95 ? 'Excellent' :
                performance.accuracy >= 90 ? 'Good' : 'Needs Work'}
            </p>
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div
                className={`h-1.5 rounded-full transition-all duration-300 ${performance.accuracy >= 95 ? 'bg-green-500' :
                    performance.accuracy >= 90 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                style={{ width: `${performance.accuracy}%` }}
              />
            </div>
          </div>
        </div>

        {/* Total Interactions */}
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Total</span>
          </div>
          <div className="space-y-1">
            <p className="text-lg font-bold text-white">
              {formatNumber(performance.totalInteractions)}
            </p>
            <p className="text-sm font-medium text-blue-400">
              Interactions
            </p>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
              <span className="text-xs text-gray-400">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsPanel;