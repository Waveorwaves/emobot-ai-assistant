import React from 'react';
import { StatusPanelProps } from '../../types/dashboard';
import { Wifi, WifiOff, Clock, AlertCircle } from 'lucide-react';

const StatusPanel: React.FC<StatusPanelProps> = ({
  status,
  lastSeen,
  responseTime
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'online':
        return 'bg-green-500 shadow-green-500/50';
      case 'offline':
        return 'bg-red-500 shadow-red-500/50';
      case 'busy':
        return 'bg-amber-500 shadow-amber-500/50';
      case 'maintenance':
        return 'bg-blue-500 shadow-blue-500/50';
      default:
        return 'bg-gray-500 shadow-gray-500/50';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'online':
        return <Wifi className="w-8 h-8 text-white" />;
      case 'offline':
        return <WifiOff className="w-8 h-8 text-white" />;
      case 'busy':
        return <Clock className="w-8 h-8 text-white" />;
      case 'maintenance':
        return <AlertCircle className="w-8 h-8 text-white" />;
      default:
        return <WifiOff className="w-8 h-8 text-white" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'online':
        return 'Online';
      case 'offline':
        return 'Offline';
      case 'busy':
        return 'Busy';
      case 'maintenance':
        return 'Maintenance';
      default:
        return 'Unknown';
    }
  };

  const getPulseAnimation = () => {
    return status === 'online' || status === 'busy' ? 'animate-pulse' : '';
  };

  const formatLastSeen = () => {
    if (!lastSeen) return 'Unknown';
    const now = new Date();
    const diff = now.getTime() - lastSeen.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="glass-panel rounded-lg p-6 h-[300px] flex flex-col items-center justify-center overflow-hidden">
      {/* Status Circle */}
      <div className="relative mb-4">
        <div
          className={`
            w-24 h-24 rounded-full ${getStatusColor()} ${getPulseAnimation()}
            flex items-center justify-center shadow-lg
            transition-all duration-300 ease-in-out
            hover:scale-105
          `}
          title={`Status: ${getStatusText()}${responseTime ? ` | Response: ${responseTime}ms` : ''}`}
        >
          {getStatusIcon()}
        </div>

        {/* Pulse Ring for Active States */}
        {(status === 'online' || status === 'busy') && (
          <div className={`
            absolute inset-0 w-24 h-24 rounded-full ${getStatusColor().split(' ')[0]} 
            animate-ping opacity-20
          `} />
        )}
      </div>

      {/* Status Text */}
      <h3 className="text-xl font-semibold text-white mb-2">
        {getStatusText()}
      </h3>

      {/* Status Details */}
      <div className="text-center space-y-1">
        {responseTime && (
          <p className="text-sm text-gray-300">
            Response: {responseTime}ms
          </p>
        )}

        <p className="text-xs text-gray-400">
          Last seen: {formatLastSeen()}
        </p>
      </div>

      {/* Additional Status Indicators */}
      <div className="mt-3 flex space-x-3">
        {status === 'online' && (
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
        )}
        {status === 'busy' && (
          <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" />
        )}
        {status === 'maintenance' && (
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
        )}
        {status === 'offline' && (
          <div className="w-2 h-2 bg-red-400 rounded-full" />
        )}
      </div>
    </div>
  );
};

export default StatusPanel;