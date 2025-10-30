import { useState } from 'react';
import LoginPage from './components/LoginPage';
import MainPage from './components/MainPage';
import DashboardPage from './components/dashboard/DashboardPage';
import SystemLogPage from './components/dashboard/SystemLogPage';
import CalendarPage from './components/CalendarPage';
import EmailPage from './components/EmailPage';
import TodoPage from './components/TodoPage';
import HistoryPage from './components/HistoryPage';
import SettingsPage from './components/SettingsPage';
import MemoryPage from './components/MemoryPage';
import { Message } from './types/dashboard';
import { DataProvider } from './context/DataContext';

type PageType = 'login' | 'main' | 'dashboard' | 'systemlog' | 'calendar' | 'email' | 'todo' | 'history' | 'settings' | 'memory';

// Legacy Message interface for MainPage compatibility
interface LegacyMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

function App() {
  // Dashboard is the default landing page
  const [currentPage, setCurrentPage] = useState<PageType>('dashboard');
  const [messages] = useState<Message[]>([]);
  // Removed theme/light-mode support
  const [legacyMessages] = useState<LegacyMessage[]>([]);

  const handleLogin = async (email: string, password: string) => {
    // TODO: Implement actual authentication logic
    console.log('Login attempt:', { email, password });
    // After login, show dashboard as main landing page
    setCurrentPage('dashboard');
  };

  const handleSignUp = () => {
    // TODO: Navigate to sign up page or show sign up modal
    console.log('Sign up clicked');
  };

  const handleForgotPassword = () => {
    // TODO: Navigate to forgot password page or show reset modal
    console.log('Forgot password clicked');
  };

  const handleNavigateToFullChat = () => {
    setCurrentPage('main');
  };

  const handleNavigate = (page: string) => {
    setCurrentPage(page as PageType);
  };

  return (
    <DataProvider>
      <div className="min-h-screen">
        {/* Light mode removed */}
      {currentPage === 'login' && (
        <LoginPage 
          onLogin={handleLogin}
          onSignUp={handleSignUp}
          onForgotPassword={handleForgotPassword}
        />
      )}
      
      {currentPage === 'main' && (
        <MainPage initialMessages={legacyMessages} onNavigate={handleNavigate} />
      )}

      {currentPage === 'dashboard' && (
        <DashboardPage 
          onNavigate={handleNavigate}
        />
      )}

      {currentPage === 'systemlog' && (
        <SystemLogPage 
          initialMessages={messages}
          onNavigateToFullChat={handleNavigateToFullChat}
          onNavigate={handleNavigate}
        />
      )}

      {currentPage === 'calendar' && (
        <CalendarPage onNavigate={handleNavigate} />
      )}

      {currentPage === 'email' && (
        <EmailPage onNavigate={handleNavigate} />
      )}

      {currentPage === 'todo' && (
        <TodoPage onNavigate={handleNavigate} />
      )}

      {currentPage === 'history' && (
        <HistoryPage onNavigate={handleNavigate} />
      )}

      {currentPage === 'settings' && (
        <SettingsPage onNavigate={handleNavigate} />
      )}

      {currentPage === 'memory' && (
        <MemoryPage onNavigate={handleNavigate} />
      )}
      </div>
    </DataProvider>
  );
}

export default App;