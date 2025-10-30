import React from 'react';
import { User } from 'lucide-react';
import { clsx } from 'clsx';

interface AvatarProps {
  src?: string;
  alt?: string;
  fallback?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  status?: 'online' | 'offline' | 'away' | 'busy';
  className?: string;
  onClick?: () => void;
}

const sizeClasses = {
  xs: 'w-8 h-8 text-xs',
  sm: 'w-12 h-12 text-sm',
  md: 'w-16 h-16 text-base',
  lg: 'w-20 h-20 text-lg',
  xl: 'w-24 h-24 text-xl',
  '2xl': 'w-32 h-32 text-2xl'
};

const statusColors = {
  online: 'bg-green-500',
  offline: 'bg-gray-400',
  away: 'bg-yellow-500',
  busy: 'bg-red-500'
};

const statusSizes = {
  xs: 'w-2 h-2',
  sm: 'w-2.5 h-2.5',
  md: 'w-3 h-3',
  lg: 'w-3.5 h-3.5',
  xl: 'w-4 h-4',
  '2xl': 'w-5 h-5'
};

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  fallback,
  size = 'md',
  status,
  className,
  onClick
}) => {
  const [imageError, setImageError] = React.useState(false);

  const handleImageError = () => {
    setImageError(true);
  };

  const showFallback = !src || imageError;

  const getFallbackContent = () => {
    if (fallback) {
      return fallback.charAt(0).toUpperCase();
    }
    return <User className="w-1/2 h-1/2 text-gray-400" />;
  };

  return (
    <div
      className={clsx(
        'relative inline-flex items-center justify-center rounded-full overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 shadow-lg ring-2 ring-white ring-opacity-20 flex-shrink-0',
        sizeClasses[size],
        onClick && 'cursor-pointer hover:shadow-xl hover:scale-105 transition-all duration-200 ease-out',
        className
      )}
      onClick={onClick}
    >
      {/* Image */}
      {src && !imageError && (
        <img
          src={src}
          alt={alt || 'Avatar'}
          className="w-full h-full object-cover"
          onError={handleImageError}
        />
      )}
      
      {/* Fallback */}
      {showFallback && (
        <div className="flex items-center justify-center w-full h-full text-gray-500 font-medium bg-gradient-to-br from-slate-100 to-slate-200">
          {getFallbackContent()}
        </div>
      )}
      
      {/* Status indicator */}
      {status && (
        <div className={clsx(
          'absolute bottom-0 right-0 rounded-full border-2 border-white shadow-sm',
          statusColors[status],
          statusSizes[size]
        )} />
      )}
    </div>
  );
};

export default Avatar;