import React from 'react';
import { CheckCircle, Clock, AlertCircle, Play, Target } from 'lucide-react';
import { MissionPanelProps } from '../../types/dashboard';

const MissionPanel: React.FC<MissionPanelProps> = ({
  currentMissions,
  completedToday,
  inProgress
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'in_progress':
        return <Play className="w-4 h-4 text-blue-400" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400 bg-green-900/20 border-green-700';
      case 'in_progress':
        return 'text-blue-400 bg-blue-900/20 border-blue-700';
      case 'pending':
        return 'text-yellow-400 bg-yellow-900/20 border-yellow-700';
      case 'failed':
        return 'text-red-400 bg-red-900/20 border-red-700';
      default:
        return 'text-gray-400 bg-gray-900/20 border-gray-700';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 25) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatTimeRemaining = (estimatedCompletion?: Date) => {
    if (!estimatedCompletion) return null;

    const now = new Date();
    const diff = estimatedCompletion.getTime() - now.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes <= 0) return 'Overdue';
    if (minutes < 60) return `${minutes}m remaining`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ${minutes % 60}m remaining`;
    const days = Math.floor(hours / 24);
    return `${days}d remaining`;
  };

  const visibleMissions = currentMissions.slice(0, 3); // Show max 3 missions

  return (
    <div className="bg-[#453f3b] rounded-lg p-6 h-[250px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Active Missions</h3>
        <Target className="w-5 h-5 text-gray-400" />
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{inProgress}</p>
          <p className="text-xs text-gray-400">In Progress</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-400">{completedToday}</p>
          <p className="text-xs text-gray-400">Completed</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-400">{currentMissions.length}</p>
          <p className="text-xs text-gray-400">Total</p>
        </div>
      </div>

      {/* Mission List */}
      <div className="space-y-3 overflow-y-auto max-h-[120px]">
        {visibleMissions.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-400 text-sm">No active missions</p>
          </div>
        ) : (
          visibleMissions.map((mission) => (
            <div
              key={mission.id}
              className="bg-[#1e1e1e] border border-gray-600 rounded-lg p-3 space-y-2"
            >
              {/* Mission Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(mission.status)}
                  <h4 className="text-sm font-medium text-white truncate">
                    {mission.title}
                  </h4>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs border ${getStatusColor(mission.status)}`}
                >
                  {mission.status.replace('_', ' ')}
                </span>
              </div>

              {/* Progress Bar */}
              {mission.progress > 0 && (
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-400">Progress</span>
                    <span className="text-xs text-white">{mission.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all duration-300 ${getProgressColor(mission.progress)}`}
                      style={{ width: `${mission.progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Time Information */}
              {mission.estimatedCompletion && (
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-400">
                    {formatTimeRemaining(mission.estimatedCompletion)}
                  </span>
                  <span className="text-gray-500">
                    Started {mission.startTime.toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              )}
            </div>
          ))
        )}

        {/* Show More Indicator */}
        {currentMissions.length > 3 && (
          <div className="text-center">
            <button className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
              +{currentMissions.length - 3} more missions
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MissionPanel;