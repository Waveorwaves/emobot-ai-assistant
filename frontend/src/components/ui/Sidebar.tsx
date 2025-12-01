import React, { useState, useRef, useEffect } from 'react';
import { Calendar, Mail, CheckSquare, Clock, Settings, Menu, LayoutDashboard, ChevronUp, Brain, Server } from 'lucide-react';
import Avatar from './Avatar';
import { useData } from '../../context/DataContext';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  activeTab: string;
  onNavigate: (page: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggleCollapse,
  activeTab,
  onNavigate
}) => {
  const { userAvatar, userName } = useData();
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'calendar', label: 'Calendar', icon: Calendar },
    { id: 'email', label: 'Email', icon: Mail },
    { id: 'todo', label: 'TODO List', icon: CheckSquare },
    { id: 'systemlog', label: 'System Log', icon: Server },
  ];

  const profileDropdownItems = [
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'history', label: 'History', icon: Clock },
    { id: 'memory', label: 'Memory', icon: Brain },
  ];

  const handleSidebarNavigation = (itemId: string) => {
    onNavigate(itemId);
    setIsProfileDropdownOpen(false);
  };

  const handleProfileDropdownToggle = () => {
    if (!isCollapsed) {
      setIsProfileDropdownOpen(!isProfileDropdownOpen);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsProfileDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div
      className={`${isCollapsed ? 'w-20' : 'w-64'} bg-black/40 backdrop-blur-xl border-r border-primary-500/60 text-white transition-all duration-300 flex flex-col fixed left-0 top-0 h-screen z-50 shadow-[0_0_30px_rgba(0,0,0,0.5)]`}
    >  {/* Sidebar Header */}
      <div className={`p-4 flex items-center ${isCollapsed ? 'justify-center' : 'px-6 justify-between'}`}>
        {!isCollapsed && <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-accent-400">Emobot</span>}
        <button
          onClick={onToggleCollapse}
          className="text-white/60 hover:text-white transition-colors p-2 hover:bg-white/5 rounded-lg"
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>

      {/* Sidebar Navigation */}
      <div className="flex-1 px-3 py-4 space-y-1">
        {sidebarItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleSidebarNavigation(item.id)}
              className={`group relative flex items-center transition-all duration-200 ${isCollapsed
                ? 'w-full justify-center h-[56px] rounded-xl mb-2'
                : 'w-full px-4 h-[56px] gap-3 rounded-xl mb-2'
                } ${isActive
                  ? 'bg-transparent text-white shadow-[0_0_20px_rgba(6,182,212,0.15)] border border-primary-500'
                  : 'text-gray-400 hover:text-white hover:bg-accent-500/10 hover:shadow-[0_0_15px_rgba(236,72,153,0.2)] hover:border-accent-500/30'
                }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary-400 rounded-r-full"></div>
              )}

              <Icon className={`w-5 h-5 flex-shrink-0 transition-colors ${isActive ? 'text-primary-400' : 'group-hover:text-white'}`} />

              {!isCollapsed && (
                <span className="font-display font-semibold uppercase tracking-wide text-sm">{item.label}</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Profile Dropdown Section */}
      <div className="relative p-3" ref={dropdownRef}>
        {/* Dropdown Menu */}
        {isProfileDropdownOpen && !isCollapsed && (
          <div className="absolute bottom-full left-3 right-3 mb-2 glass-panel rounded-xl overflow-hidden shadow-2xl animate-in slide-in-from-bottom-2 fade-in duration-200">
            {profileDropdownItems.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSidebarNavigation(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-2 text-left transition-colors font-display font-semibold uppercase tracking-wide text-xs ${isActive
                    ? 'bg-[#524d48] text-white'
                    : 'text-gray-300 hover:text-white hover:bg-[#524d48]'
                    }`}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Profile Button */}
        <div className="border-t border-white/10 pt-3">
          <button
            onClick={handleProfileDropdownToggle}
            className={`w-full flex items-center transition-all duration-200 rounded-xl hover:bg-white/5 ${isCollapsed
              ? 'justify-center p-2'
              : 'gap-3 px-3 py-2 text-left'
              }`}
          >
            <Avatar
              src={userAvatar}
              alt={userName}
              fallback={userName}
              size="sm"
              className="ring-2 ring-primary-500/50"
            />
            {!isCollapsed && (
              <>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium truncate">{userName}</p>
                  <p className="text-xs text-gray-400 truncate">Online</p>
                </div>
                <ChevronUp
                  className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isProfileDropdownOpen ? 'rotate-180' : ''
                    }`}
                />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;