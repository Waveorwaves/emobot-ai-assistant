import React from 'react';
import { X, Edit, Trash2, Calendar, Clock, FileText, Tag, AlertTriangle } from 'lucide-react';
import { CalendarEvent, useData } from '../../context/DataContext';

interface EventPreviewProps {
  event: CalendarEvent;
  position: { x: number; y: number };
  onClose: () => void;
  onEdit: (event: CalendarEvent) => void;
  onDelete: (eventId: string) => void;
}

const EventPreview: React.FC<EventPreviewProps> = ({
  event,
  position,
  onClose,
  onEdit,
  onDelete
}) => {
  const { getEventsForDate, detectConflicts } = useData();
  
  // Check for conflicts
  const eventDate = event.date ? new Date(event.date + 'T00:00:00') : new Date();
  const dayEvents = getEventsForDate(eventDate);
  const conflicts = detectConflicts(dayEvents);
  const eventConflicts = conflicts.find(c => c.eventId === event.id);
  const conflictingEvents = eventConflicts ? 
    dayEvents.filter(e => eventConflicts.conflictsWith.includes(e.id)) : [];

  const getEventTypeColor = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'meeting':
        return 'bg-blue-500';
      case 'task':
        return 'bg-green-500';
      case 'reminder':
        return 'bg-yellow-500';
      case 'personal':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getEventTypeIcon = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'meeting':
        return <Calendar className="w-4 h-4" />;
      case 'task':
        return <Tag className="w-4 h-4" />;
      case 'reminder':
        return <Clock className="w-4 h-4" />;
      case 'personal':
        return <Tag className="w-4 h-4" />;
      default:
        return <Calendar className="w-4 h-4" />;
    }
  };

  const handleEdit = () => {
    onEdit(event);
    onClose();
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this event?')) {
      onDelete(event.id);
      onClose();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  // Calculate position to ensure popup stays within viewport
  const maxWidth = 320;
  const maxHeight = 400;
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  
  let adjustedX = position.x;
  let adjustedY = position.y;
  
  // Adjust horizontal position
  if (position.x + maxWidth > viewportWidth) {
    adjustedX = viewportWidth - maxWidth - 20;
  }
  
  // Adjust vertical position
  if (position.y + maxHeight > viewportHeight) {
    adjustedY = position.y - maxHeight - 10;
  }
  
  if (adjustedY < 20) {
    adjustedY = 20;
  }

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 z-40"
        onClick={onClose}
      />
      
      {/* Popup */}
      <div
        className="fixed z-50 bg-[#453f3b] rounded-lg shadow-2xl border border-gray-600 max-w-sm"
        style={{
          left: `${adjustedX}px`,
          top: `${adjustedY}px`,
          width: `${maxWidth}px`
        }}
        onKeyDown={handleKeyDown}
        tabIndex={-1}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-4 border-b border-gray-600">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <div className={`w-3 h-3 rounded-full ${getEventTypeColor(event.type)}`} />
              <span className="text-xs font-medium text-gray-300 capitalize flex items-center space-x-1">
                {getEventTypeIcon(event.type)}
                <span>{event.type}</span>
              </span>
            </div>
            <h3 className="text-lg font-semibold text-white leading-tight">
              {event.title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors ml-2 flex-shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Date info */}
          <div className="flex items-center space-x-3 text-gray-300">
            <Calendar className="w-4 h-4 text-gray-400" />
            <div className="text-sm">
              {event.date ? 
                new Date(event.date + 'T00:00:00').toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  month: 'long', 
                  day: 'numeric' 
                }) :
                new Date().toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  month: 'long', 
                  day: 'numeric' 
                })
              }
            </div>
          </div>

          {/* Time and Duration */}
          <div className="flex items-center space-x-3 text-gray-300">
            <Clock className="w-4 h-4 text-gray-400" />
            <div>
              <div className="text-sm font-medium">{event.time}</div>
              <div className="text-xs text-gray-400">{event.duration}</div>
            </div>
          </div>

          {/* Conflict Warning */}
          {conflictingEvents.length > 0 && (
            <div className="flex items-start space-x-3 text-red-300 bg-red-900/20 rounded-lg p-3 border border-red-600">
              <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium mb-1">Time Conflict</div>
                <div className="text-xs text-red-400 leading-relaxed">
                  Overlaps with: {conflictingEvents.map(e => e.title).join(', ')}
                </div>
              </div>
            </div>
          )}

          {/* Description */}
          {event.description && (
            <div className="flex items-start space-x-3 text-gray-300">
              <FileText className="w-4 h-4 text-gray-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium mb-1">Description</div>
                <div className="text-xs text-gray-400 leading-relaxed">
                  {event.description}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-2 p-4 border-t border-gray-600">
          <button
            onClick={handleDelete}
            className="flex items-center space-x-2 px-3 py-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span className="text-sm">Delete</span>
          </button>
          <button
            onClick={handleEdit}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Edit className="w-4 h-4" />
            <span className="text-sm">Edit</span>
          </button>
        </div>

        {/* Footer */}
        <div className="px-4 pb-3">
          <p className="text-xs text-gray-400 text-center">
            Press Esc to close
          </p>
        </div>
      </div>
    </>
  );
};

export default EventPreview;