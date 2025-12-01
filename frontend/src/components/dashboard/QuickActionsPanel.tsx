import React from 'react';
import { Settings, RefreshCw, Download, Bell, HelpCircle, Zap } from 'lucide-react';

const QuickActionsPanel: React.FC = () => {
  const actions = [
    {
      id: 'refresh',
      icon: RefreshCw,
      label: 'Refresh Data',
      color: 'text-blue-400 hover:text-blue-300',
      bgColor: 'hover:bg-blue-900/20'
    },
    {
      id: 'settings',
      icon: Settings,
      label: 'Settings',
      color: 'text-gray-400 hover:text-gray-300',
      bgColor: 'hover:bg-gray-900/20'
    },
    {
      id: 'export',
      icon: Download,
      label: 'Export Data',
      color: 'text-green-400 hover:text-green-300',
      bgColor: 'hover:bg-green-900/20'
    },
    {
      id: 'notifications',
      icon: Bell,
      label: 'Notifications',
      color: 'text-yellow-400 hover:text-yellow-300',
      bgColor: 'hover:bg-yellow-900/20'
    },
    {
      id: 'boost',
      icon: Zap,
      label: 'Performance\nBoost',
      color: 'text-sky-400 hover:text-sky-300',
      bgColor: 'hover:bg-sky-900/20'
    },
    {
      id: 'help',
      icon: HelpCircle,
      label: 'Help',
      color: 'text-cyan-400 hover:text-cyan-300',
      bgColor: 'hover:bg-cyan-900/20'
    }
  ];

  const handleAction = (actionId: string) => {
    switch (actionId) {
      case 'refresh':
        window.location.reload();
        break;
      case 'settings':
        console.log('Opening settings...');
        break;
      case 'export':
        console.log('Exporting data...');
        break;
      case 'notifications':
        console.log('Opening notifications...');
        break;
      case 'boost':
        console.log('Initiating performance boost...');
        break;
      case 'help':
        console.log('Opening help...');
        break;
      default:
        console.log(`Action ${actionId} not implemented`);
    }
  };

  return (
    <div className="glass-panel rounded-lg p-6 h-[250px] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
        <Zap className="w-5 h-5 text-gray-400" />
      </div>

      {/* Actions Grid */}
      <div className="grid grid-cols-3 gap-2 h-[140px] overflow-hidden">
        {actions.map((action) => {
          const IconComponent = action.icon;
          return (
            <button
              key={action.id}
              onClick={() => handleAction(action.id)}
              className={`
                flex flex-col items-center justify-center space-y-1 p-2 rounded-lg
                bg-white/5 border border-primary-500/60 transition-all duration-200 min-h-[60px]
                ${action.bgColor} hover:border-white/30 hover:bg-white/10 hover:scale-105
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50
              `}
              title={action.label.replace('\n', ' ')}
            >
              <IconComponent className={`w-4 h-4 ${action.color} transition-colors flex-shrink-0`} />
              <span className="text-xs text-gray-300 text-center leading-tight whitespace-pre-line overflow-hidden">
                {action.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActionsPanel;