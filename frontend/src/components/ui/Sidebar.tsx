import React, { useState, useRef, useEffect } from 'react';
import { Calendar, Mail, CheckSquare, Clock, Settings, Menu, LayoutDashboard, ChevronUp, Brain } from 'lucide-react';
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
    { id: 'systemlog', label: 'System Log', icon: Clock },
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
    <div className={`${isCollapsed ? 'w-20' : 'w-72'} bg-[#1e1e1e] transition-all duration-300 flex flex-col border-r border-[#453f3b]/30 fixed left-0 top-0 h-screen z-10`}>
      {/* Sidebar Header */}
      <div className={`p-4 border-b border-[#453f3b]/30 flex items-center ${isCollapsed ? 'justify-center' : 'px-8'}`}>
        <button
          onClick={onToggleCollapse}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>

      {/* Sidebar Navigation */}
      <div className="flex-1 p-4">
        {sidebarItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleSidebarNavigation(item.id)}
              className={`${
                isCollapsed
                  ? 'w-full h-[56px] flex items-center justify-center mb-2'
                  : 'w-full h-[56px] flex items-center gap-3 px-4 rounded-lg text-left transition-colors mb-2 text-sm'
              } ${!isCollapsed && (isActive ? 'bg-[#453f3b] text-white' : 'text-gray-300 hover:text-white hover:bg-[#453f3b]/50')}`}
            >
              {isCollapsed ? (
                <div
                  className={`flex items-center justify-center w-12 h-12 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-[#453f3b] text-white'
                      : 'text-gray-300 hover:text-white hover:bg-[#453f3b]/50'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                </div>
              ) : (
                <>
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span>{item.label}</span>
                </>
              )}
            </button>
          );
        })}
      </div>

      {/* Profile Dropdown Section */}
      <div className="relative" ref={dropdownRef}>
        {/* Dropdown Menu */}
        {isProfileDropdownOpen && !isCollapsed && (
          <div className="absolute bottom-full left-4 right-4 mb-2 bg-[#453f3b] border border-[#453f3b]/50 rounded-lg shadow-lg overflow-hidden">
            {profileDropdownItems.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSidebarNavigation(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors text-sm ${
                    isActive 
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

        {/* Profile Button - Fixed Height */}
        <div className="border-t border-[#453f3b]/30">
          <button
            onClick={handleProfileDropdownToggle}
            className={`${
              isCollapsed
                ? 'w-full flex justify-center items-center px-4 py-3'
                : 'w-full flex items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-[#453f3b]/50'
            }`}
          >
            {isCollapsed ? (
              <Avatar
                src={userAvatar}
                alt={userName}
                fallback={userName}
                size="sm"
                className="ring-2 ring-[#453f3b] hover:ring-white transition-all duration-200"
              />
            ) : (
              <>
                <Avatar
                  src={userAvatar}
                  alt={userName}
                  fallback={userName}
                  size="sm"
                  className="ring-2 ring-[#453f3b]"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium truncate">{userName}</p>
                </div>
                <ChevronUp
                  className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
                    isProfileDropdownOpen ? 'rotate-180' : ''
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