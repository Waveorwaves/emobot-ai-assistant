import React, { useState, useRef } from 'react';
import { User, Bell, Shield, Palette, Database, Zap, Save, RefreshCw, Upload, LogOut } from 'lucide-react';
import Avatar from './ui/Avatar';
import Sidebar from './ui/Sidebar';
import ChatBox from './ui/ChatBox';
import { useData } from '../context/DataContext';

interface SettingsPageProps {
  onNavigate?: (page: string) => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({ onNavigate }) => {
  const { userAvatar, setUserAvatar, userName, setUserName, emobotAvatar, setEmobotAvatar, emobotName, setEmobotName } = useData();
  const userFileInputRef = useRef<HTMLInputElement>(null);
  const emobotFileInputRef = useRef<HTMLInputElement>(null);

  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('settings');
  const [activeSettingsTab, setActiveSettingsTab] = useState<string>('profile');
  
  // Settings state
  const [profileSettings, setProfileSettings] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    avatar: '',
    timezone: 'UTC-8',
    language: 'English'
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    desktopNotifications: false,
    taskReminders: true,
    calendarAlerts: true,
    emailDigest: 'weekly'
  });

  const [privacySettings, setPrivacySettings] = useState({
    dataCollection: true,
    analytics: false,
    shareUsageData: false,
    autoSave: true,
    sessionTimeout: '30'
  });

  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: 'dark',
    accentColor: 'blue',
    fontSize: 'medium',
    compactMode: false,
    animations: true
  });

  const [systemSettings, setSystemSettings] = useState({
    autoUpdate: true,
    errorReporting: true,
    performanceMode: false,
    cacheSize: '500',
    maxHistoryItems: '1000'
  });


  const settingsTabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy & Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'system', label: 'System', icon: Database }
  ];

  const handleToggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    try { 
      localStorage.setItem('sidebarCollapsed', String(next)); 
    } catch {}
  };

  const handleSidebarNavigation = (itemId: string) => {
    setActiveTab(itemId);
    if (onNavigate) {
      onNavigate(itemId);
    }
  };


  const handleSaveSettings = () => {
    // Implement save logic here
    console.log('Saving settings...', {
      profile: profileSettings,
      notifications: notificationSettings,
      privacy: privacySettings,
      appearance: appearanceSettings,
      system: systemSettings
    });
  };

  const handleResetSettings = () => {
    if (confirm('Are you sure you want to reset all settings to default?')) {
      // Reset to default values
      setProfileSettings({
        name: 'John Doe',
        email: 'john.doe@example.com',
        avatar: '',
        timezone: 'UTC-8',
        language: 'English'
      });
      // Reset other settings similarly...
    }
  };

  const handleSignOut = () => {
    if (confirm('Are you sure you want to sign out?')) {
      // Clear any stored session data
      try {
        localStorage.removeItem('sidebarCollapsed');
        // Clear other session data if needed
      } catch (error) {
        console.error('Error clearing session data:', error);
      }
      // Navigate to login page
      if (onNavigate) {
        onNavigate('login');
      }
    }
  };

  const handleUserAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
      }
      const imageUrl = URL.createObjectURL(file);
      setUserAvatar(imageUrl);
    }
  };

  const handleRemoveUserAvatar = () => {
    setUserAvatar('');
  };

  const handleUserUploadClick = () => {
    userFileInputRef.current?.click();
  };

  const handleEmobotAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
      }
      const imageUrl = URL.createObjectURL(file);
      setEmobotAvatar(imageUrl);
    }
  };

  const handleRemoveEmobotAvatar = () => {
    setEmobotAvatar('/emobot-cat-avatar.png');
  };

  const handleEmobotUploadClick = () => {
    emobotFileInputRef.current?.click();
  };

  const renderProfileSettings = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-white">Profile Settings</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Your Name</label>
          <input
            type="text"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
          <input
            type="email"
            value={profileSettings.email}
            onChange={(e) => setProfileSettings(prev => ({ ...prev, email: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Timezone</label>
          <select
            value={profileSettings.timezone}
            onChange={(e) => setProfileSettings(prev => ({ ...prev, timezone: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="UTC-8">Pacific Time (UTC-8)</option>
            <option value="UTC-5">Eastern Time (UTC-5)</option>
            <option value="UTC+0">Greenwich Mean Time (UTC+0)</option>
            <option value="UTC+1">Central European Time (UTC+1)</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Language</label>
          <select
            value={profileSettings.language}
            onChange={(e) => setProfileSettings(prev => ({ ...prev, language: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="English">English</option>
            <option value="Spanish">Spanish</option>
            <option value="French">French</option>
            <option value="German">German</option>
          </select>
        </div>
      </div>

      {/* User Profile Picture */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Your Profile Picture</label>
        <div className="flex items-center space-x-4">
          <Avatar
            src={userAvatar}
            alt={userName}
            fallback={userName}
            size="lg"
            className="border-2 border-gray-600"
          />
          <div>
            <input
              ref={userFileInputRef}
              type="file"
              accept="image/*"
              onChange={handleUserAvatarUpload}
              className="hidden"
            />
            <button
              onClick={handleUserUploadClick}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors mr-2 flex items-center space-x-2 inline-flex"
            >
              <Upload className="w-4 h-4" />
              <span>Upload New</span>
            </button>
            <button
              onClick={handleRemoveUserAvatar}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Remove
            </button>
          </div>
        </div>
        <p className="text-gray-400 text-sm mt-2">
          This profile picture will appear in the sidebar.
        </p>
      </div>

      {/* EmoBot Settings */}
      <div className="space-y-4">
        <h4 className="text-lg font-medium text-white">EmoBot Settings</h4>

        {/* EmoBot Name */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">EmoBot Name</label>
          <input
            type="text"
            value={emobotName}
            onChange={(e) => setEmobotName(e.target.value)}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter EmoBot's name"
          />
          <p className="text-gray-400 text-xs mt-1">
            This name will appear in chat conversations and the welcome screen.
          </p>
        </div>

        {/* EmoBot Avatar */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">EmoBot Avatar</label>
          <div className="flex items-center space-x-4">
            <Avatar
              src={emobotAvatar}
              alt={emobotName}
              size="lg"
              className="border-2 border-gray-600"
            />
            <div>
              <input
                ref={emobotFileInputRef}
                type="file"
                accept="image/*"
                onChange={handleEmobotAvatarUpload}
                className="hidden"
              />
              <button
                onClick={handleEmobotUploadClick}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors mr-2 flex items-center space-x-2 inline-flex"
              >
                <Upload className="w-4 h-4" />
                <span>Upload New</span>
              </button>
              <button
                onClick={handleRemoveEmobotAvatar}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Reset to Default
              </button>
            </div>
          </div>
          <p className="text-gray-400 text-xs mt-1">
            This avatar represents {emobotName} in chat conversations and welcome screens.
          </p>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-white">Notification Settings</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Email Notifications</h4>
            <p className="text-gray-400 text-sm">Receive notifications via email</p>
          </div>
          <input
            type="checkbox"
            checked={notificationSettings.emailNotifications}
            onChange={(e) => setNotificationSettings(prev => ({ ...prev, emailNotifications: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Push Notifications</h4>
            <p className="text-gray-400 text-sm">Receive push notifications on your device</p>
          </div>
          <input
            type="checkbox"
            checked={notificationSettings.pushNotifications}
            onChange={(e) => setNotificationSettings(prev => ({ ...prev, pushNotifications: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Desktop Notifications</h4>
            <p className="text-gray-400 text-sm">Show notifications on your desktop</p>
          </div>
          <input
            type="checkbox"
            checked={notificationSettings.desktopNotifications}
            onChange={(e) => setNotificationSettings(prev => ({ ...prev, desktopNotifications: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Task Reminders</h4>
            <p className="text-gray-400 text-sm">Get reminded about upcoming tasks</p>
          </div>
          <input
            type="checkbox"
            checked={notificationSettings.taskReminders}
            onChange={(e) => setNotificationSettings(prev => ({ ...prev, taskReminders: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Email Digest Frequency</label>
          <select
            value={notificationSettings.emailDigest}
            onChange={(e) => setNotificationSettings(prev => ({ ...prev, emailDigest: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="never">Never</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderPrivacySettings = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-white">Privacy & Security</h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Data Collection</h4>
            <p className="text-gray-400 text-sm">Allow collection of usage data to improve service</p>
          </div>
          <input
            type="checkbox"
            checked={privacySettings.dataCollection}
            onChange={(e) => setPrivacySettings(prev => ({ ...prev, dataCollection: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Analytics</h4>
            <p className="text-gray-400 text-sm">Share anonymous analytics data</p>
          </div>
          <input
            type="checkbox"
            checked={privacySettings.analytics}
            onChange={(e) => setPrivacySettings(prev => ({ ...prev, analytics: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Auto-Save</h4>
            <p className="text-gray-400 text-sm">Automatically save your work</p>
          </div>
          <input
            type="checkbox"
            checked={privacySettings.autoSave}
            onChange={(e) => setPrivacySettings(prev => ({ ...prev, autoSave: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Session Timeout (minutes)</label>
          <select
            value={privacySettings.sessionTimeout}
            onChange={(e) => setPrivacySettings(prev => ({ ...prev, sessionTimeout: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="15">15 minutes</option>
            <option value="30">30 minutes</option>
            <option value="60">1 hour</option>
            <option value="120">2 hours</option>
            <option value="never">Never</option>
          </select>
        </div>
      </div>

      {/* Sign Out Section */}
      <div className="mt-8 pt-6 border-t border-[#453f3b]/30">
        <h4 className="text-lg font-medium text-white mb-4">Account Actions</h4>
        <button
          onClick={handleSignOut}
          className="w-full md:w-auto bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg flex items-center justify-center space-x-2 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
        <p className="text-gray-400 text-sm mt-2">
          Sign out of your account and return to the login page
        </p>
      </div>
    </div>
  );

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-white">Appearance</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Theme</label>
          <select
            value={appearanceSettings.theme}
            onChange={(e) => setAppearanceSettings(prev => ({ ...prev, theme: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="dark">Dark</option>
            <option value="light">Light</option>
            <option value="auto">Auto (System)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Accent Color</label>
          <select
            value={appearanceSettings.accentColor}
            onChange={(e) => setAppearanceSettings(prev => ({ ...prev, accentColor: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="blue">Blue</option>
            <option value="green">Green</option>
            <option value="purple">Purple</option>
            <option value="red">Red</option>
            <option value="orange">Orange</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Font Size</label>
          <select
            value={appearanceSettings.fontSize}
            onChange={(e) => setAppearanceSettings(prev => ({ ...prev, fontSize: e.target.value }))}
            className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Compact Mode</h4>
            <p className="text-gray-400 text-sm">Use smaller spacing and elements</p>
          </div>
          <input
            type="checkbox"
            checked={appearanceSettings.compactMode}
            onChange={(e) => setAppearanceSettings(prev => ({ ...prev, compactMode: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Animations</h4>
            <p className="text-gray-400 text-sm">Enable UI animations and transitions</p>
          </div>
          <input
            type="checkbox"
            checked={appearanceSettings.animations}
            onChange={(e) => setAppearanceSettings(prev => ({ ...prev, animations: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );

  const renderSystemSettings = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-white">System Settings</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Auto Update</h4>
            <p className="text-gray-400 text-sm">Automatically update to the latest version</p>
          </div>
          <input
            type="checkbox"
            checked={systemSettings.autoUpdate}
            onChange={(e) => setSystemSettings(prev => ({ ...prev, autoUpdate: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Error Reporting</h4>
            <p className="text-gray-400 text-sm">Send error reports to help improve the app</p>
          </div>
          <input
            type="checkbox"
            checked={systemSettings.errorReporting}
            onChange={(e) => setSystemSettings(prev => ({ ...prev, errorReporting: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-[#453f3b] rounded-lg">
          <div>
            <h4 className="text-white font-medium">Performance Mode</h4>
            <p className="text-gray-400 text-sm">Optimize for better performance</p>
          </div>
          <input
            type="checkbox"
            checked={systemSettings.performanceMode}
            onChange={(e) => setSystemSettings(prev => ({ ...prev, performanceMode: e.target.checked }))}
            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Cache Size (MB)</label>
            <input
              type="number"
              value={systemSettings.cacheSize}
              onChange={(e) => setSystemSettings(prev => ({ ...prev, cacheSize: e.target.value }))}
              className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Max History Items</label>
            <input
              type="number"
              value={systemSettings.maxHistoryItems}
              onChange={(e) => setSystemSettings(prev => ({ ...prev, maxHistoryItems: e.target.value }))}
              className="w-full p-3 bg-[#453f3b] border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettingsContent = () => {
    switch (activeSettingsTab) {
      case 'profile':
        return renderProfileSettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'privacy':
        return renderPrivacySettings();
      case 'appearance':
        return renderAppearanceSettings();
      case 'system':
        return renderSystemSettings();
      default:
        return renderProfileSettings();
    }
  };

  return (
    <div className="h-screen bg-[#1e1e1e]">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-72'} transition-all duration-300 flex flex-col h-screen`}>

        {/* Settings Content Area */}
        <div className="flex-1 bg-[#1e1e1e] flex overflow-hidden">
          {/* Settings Navigation */}
          <div className="w-64 bg-[#1e1e1e] border-r border-[#453f3b]/30 p-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-white text-lg font-medium">Settings</h2>
              <Zap className="w-5 h-5 text-gray-400" />
            </div>

            <div className="space-y-2">
              {settingsTabs.map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveSettingsTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-left transition-colors text-sm ${
                      activeSettingsTab === tab.id
                        ? 'bg-[#453f3b] text-white'
                        : 'text-gray-300 hover:text-white hover:bg-[#453f3b]/50'
                    }`}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Settings Content */}
          <div className="flex-1 p-6 pb-20 overflow-y-auto">
            {renderSettingsContent()}

            {/* Action Buttons */}
            <div className="mt-8 pt-6 border-t border-[#453f3b]/30 flex items-center space-x-4">
              <button
                onClick={handleSaveSettings}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </button>
              <button
                onClick={handleResetSettings}
                className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Reset to Default</span>
              </button>
            </div>
          </div>
        </div>

        <ChatBox
          onSendMessage={(message) => console.log('Settings chat:', message)}
          onOpenFullChat={() => onNavigate && onNavigate('main')}
          sidebarCollapsed={isCollapsed}
        />
      </div>
    </div>
  );
};

export default SettingsPage;