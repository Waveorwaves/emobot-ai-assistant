import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import Avatar from './ui/Avatar';

interface LoginPageProps {
  onLogin?: (email: string, password: string) => void;
  onSignUp?: () => void;
  onForgotPassword?: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    
    setIsLoading(true);
    try {
      await onLogin?.(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#1e1e1e] flex flex-col items-center justify-center p-8">
      {/* Circular Avatar/Logo */}
      <div className="w-[200px] h-[200px] rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center mb-8 shadow-2xl">
        <Avatar 
          src="/emobot-cat-avatar.png" 
          alt="Emobot"
          size="xl"
          className="w-full h-full"
        />
      </div>

      {/* Login Form */}
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
        {/* Email Field */}
        <div className="relative">
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-[439px] h-[56px] bg-[#453f3b] border-none rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 px-4 text-sm"
            required
          />
        </div>

        {/* Password Field */}
        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-[439px] h-[56px] bg-[#453f3b] border-none rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 px-4 pr-12 text-sm"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-300 hover:text-white transition-colors"
          >
            {showPassword ? (
              <EyeOff className="h-5 w-5" />
            ) : (
              <Eye className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Login Button */}
        <button
          type="submit"
          disabled={isLoading || !email || !password}
          className="w-[439px] h-[56px] bg-[#453f3b] hover:bg-[#524d48] disabled:bg-[#3a352f] disabled:opacity-50 rounded-lg text-white font-medium transition-all duration-200 disabled:cursor-not-allowed mt-6"
        >
          {isLoading ? (
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Signing in...
            </div>
          ) : (
            'Sign In'
          )}
        </button>
      </form>
    </div>
  );
};

export default LoginPage;