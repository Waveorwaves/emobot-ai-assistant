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
    <div className="min-h-screen flex flex-col items-center justify-center p-8 relative overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/30 rounded-full blur-3xl -z-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/30 rounded-full blur-3xl -z-10 animate-pulse delay-1000"></div>

      <div className="glass-panel p-12 rounded-3xl shadow-2xl w-full max-w-lg backdrop-blur-xl border border-white/10">
        {/* Circular Avatar/Logo */}
        <div className="flex justify-center mb-10">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full blur opacity-50 group-hover:opacity-100 transition duration-500"></div>
            <div className="w-[160px] h-[160px] rounded-full bg-surface-800 flex items-center justify-center relative z-10 overflow-hidden border-4 border-surface-700">
              <Avatar
                src="/emobot-cat-avatar.png"
                alt="Emobot"
                size="xl"
                className="w-full h-full"
              />
            </div>
          </div>
        </div>

        <h2 className="text-3xl font-bold text-center text-white mb-8 tracking-tight">Welcome Back</h2>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email Field */}
          <div className="relative group">
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full h-14 bg-surface-900/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent px-5 text-base transition-all duration-200 group-hover:bg-surface-900/70"
              required
            />
          </div>

          {/* Password Field */}
          <div className="relative group">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full h-14 bg-surface-900/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent px-5 pr-12 text-base transition-all duration-200 group-hover:bg-surface-900/70"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-white transition-colors"
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
            className="w-full h-14 btn-neon-flow disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white font-bold text-lg mt-8 transform hover:-translate-y-0.5"
          >
            {isLoading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Signing in...
              </div>
            ) : (
              'Sign In'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;