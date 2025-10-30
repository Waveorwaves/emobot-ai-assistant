import React, { useState } from 'react';
import { Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import Sidebar from './ui/Sidebar';
import ChatBox from './ui/ChatBox';
import EventModal from './ui/EventModal';
import EventPreview from './ui/EventPreview';
import { useData, CalendarEvent } from '../context/DataContext';


interface CalendarPageProps {
  onNavigate?: (page: string) => void;
}

const CalendarPage: React.FC<CalendarPageProps> = ({ onNavigate }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('calendar');
  const [viewMode, setViewMode] = useState<'day' | 'week' | 'month'>('week');
  const [miniCalendarDate, setMiniCalendarDate] = useState(new Date());
  const [currentDate, setCurrentDate] = useState(new Date());
  const [weekStartDate, setWeekStartDate] = useState(() => {
    const today = new Date();
    const day = today.getDay();
    const diff = today.getDate() - day;
    return new Date(today.setDate(diff));
  });
  
  // Modal and preview states
  const [showEventModal, setShowEventModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | undefined>(undefined);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [previewEvent, setPreviewEvent] = useState<CalendarEvent | undefined>(undefined);
  const [previewPosition, setPreviewPosition] = useState({ x: 0, y: 0 });
  
  // Get real data from context
  const { getEventsForDate, addEvent, updateEvent, deleteEvent, todayEvents, detectConflicts, allEvents } = useData();

  // Helper function to format date in local timezone
  const formatDateLocal = (date: Date) => {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Helper function to check if an event has already passed
  const hasEventPassed = (event: CalendarEvent) => {
    const now = new Date();
    const today = formatDateLocal(now);
    
    // If event is not today, compare dates
    if (event.date !== today) {
      return event.date ? event.date < today : false;
    }
    
    // If event is today, compare times
    const [eventHours, eventMinutes] = event.time.split(':').map(Number);
    const eventTimeInMinutes = eventHours * 60 + eventMinutes;
    
    // Add duration to get end time
    const durationMinutes = (() => {
      if (event.duration.includes('hour')) {
        return parseFloat(event.duration) * 60;
      } else if (event.duration.includes('min')) {
        return parseInt(event.duration);
      } else if (event.duration === 'All day') {
        return 24 * 60; // All day events never "pass" during the day
      }
      return 60; // Default 1 hour
    })();
    
    const eventEndTimeInMinutes = eventTimeInMinutes + durationMinutes;
    const currentTimeInMinutes = now.getHours() * 60 + now.getMinutes();
    
    return eventEndTimeInMinutes <= currentTimeInMinutes;
  };

  // Calculate dynamic counts for overview (only upcoming events)
  const getTodayEventsCount = () => {
    const today = new Date();
    const todayEvents = getEventsForDate(today);
    return todayEvents.filter(event => !hasEventPassed(event)).length;
  };

  const getThisWeekEventsCount = () => {
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay());
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6);
    
    let count = 0;
    for (let d = new Date(startOfWeek); d <= endOfWeek; d.setDate(d.getDate() + 1)) {
      const dayEvents = getEventsForDate(d);
      // Only count events that haven't passed yet
      count += dayEvents.filter(event => !hasEventPassed(event)).length;
    }
    return count;
  };

  const getNextWeekEventsCount = () => {
    const today = new Date();
    const startOfNextWeek = new Date(today);
    startOfNextWeek.setDate(today.getDate() - today.getDay() + 7);
    const endOfNextWeek = new Date(startOfNextWeek);
    endOfNextWeek.setDate(startOfNextWeek.getDate() + 6);
    
    let count = 0;
    for (let d = new Date(startOfNextWeek); d <= endOfNextWeek; d.setDate(d.getDate() + 1)) {
      const dayEvents = getEventsForDate(d);
      // All future week events are by definition not passed yet, but let's be consistent
      count += dayEvents.filter(event => !hasEventPassed(event)).length;
    }
    return count;
  };

  const getEventTypeColor = (type: CalendarEvent['type'], hasConflict: boolean = false) => {
    const baseColors = {
      meeting: 'bg-blue-500',
      task: 'bg-green-500',
      reminder: 'bg-yellow-500',
      personal: 'bg-purple-500',
      default: 'bg-gray-500'
    };
    
    if (hasConflict) {
      // Add red stripe or border for conflicts
      return `${baseColors[type] || baseColors.default} border-2 border-red-500 bg-stripes`;
    }
    
    return baseColors[type] || baseColors.default;
  };

  // Helper function to check if an event has conflicts
  const hasEventConflict = (eventId: string, dayEvents: CalendarEvent[]) => {
    const conflicts = detectConflicts(dayEvents);
    return conflicts.some(conflict => conflict.eventId === eventId);
  };

  // Calculate exact positioning and layout for overlapping events
  const calculateEventLayout = (events: CalendarEvent[], viewType: 'day' | 'week' = 'day') => {
    const conflicts = detectConflicts(events);
    const layout: Array<{
      event: CalendarEvent;
      top: number;
      height: number;
      left: number;
      width: number;
      zIndex: number;
    }> = [];

    events.forEach((event, index) => {
      // Calculate exact time position within the hour
      const [hours, minutes] = event.time.split(':').map(Number);
      const minuteOffset = minutes;
      const pixelsPerMinute = 64 / 60; // 64px per hour slot / 60 minutes
      const topOffset = minuteOffset * pixelsPerMinute;

      // Calculate height based on duration
      const durationMinutes = (() => {
        if (event.duration.includes('hour')) {
          return parseFloat(event.duration) * 60;
        } else if (event.duration.includes('min')) {
          return parseInt(event.duration);
        } else if (event.duration === 'All day') {
          return 60; // Show as 1 hour for visual purposes
        }
        return 60;
      })();
      const height = Math.max(20, (durationMinutes * pixelsPerMinute) - 2); // Minimum 20px height

      // Check if this event conflicts with others
      const eventConflicts = conflicts.find(c => c.eventId === event.id);
      const conflictingEventIds = eventConflicts ? eventConflicts.conflictsWith : [];
      
      // Find all events that conflict with this one (including this event)
      const conflictGroup = events.filter(e => 
        e.id === event.id || 
        conflictingEventIds.includes(e.id) ||
        conflicts.some(c => c.eventId === e.id && c.conflictsWith.includes(event.id))
      );

      // Calculate position within conflict group
      const positionInGroup = conflictGroup.findIndex(e => e.id === event.id);
      const totalInGroup = conflictGroup.length;

      let left = 4; // Default left margin
      let width = 'calc(100% - 8px)'; // Default full width minus margins
      let zIndex = 10;

      if (totalInGroup > 1) {
        // Overlapping layout like Apple Calendar
        if (viewType === 'week') {
          // Tighter layout for week view
          const widthPerEvent = 90 / totalInGroup;
          const leftOffset = positionInGroup * 8; // Smaller offset for week view
          
          left = leftOffset;
          width = `${Math.min(widthPerEvent + 15, 95)}%`; // Constrain max width
          zIndex = 10 + positionInGroup;
        } else {
          // Day view layout
          const widthPerEvent = 85 / totalInGroup;
          const leftOffset = positionInGroup * 12;
          
          left = leftOffset;
          width = `${widthPerEvent + 20}%`;
          zIndex = 10 + positionInGroup;
        }
      }

      layout.push({
        event,
        top: topOffset,
        height,
        left,
        width: typeof width === 'string' ? width : `${width}%`,
        zIndex
      });
    });

    return layout;
  };


  const handleSidebarNavigation = (itemId: string) => {
    setActiveTab(itemId);
    if (onNavigate) {
      onNavigate(itemId);
    }
  };

  const handleToggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    try { 
      localStorage.setItem('sidebarCollapsed', String(next)); 
    } catch {}
  };

  // Mini calendar helper functions
  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const handlePrevMonth = () => {
    setMiniCalendarDate(new Date(miniCalendarDate.getFullYear(), miniCalendarDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setMiniCalendarDate(new Date(miniCalendarDate.getFullYear(), miniCalendarDate.getMonth() + 1, 1));
  };

  const isToday = (day: number) => {
    const today = new Date();
    return (
      today.getDate() === day &&
      today.getMonth() === miniCalendarDate.getMonth() &&
      today.getFullYear() === miniCalendarDate.getFullYear()
    );
  };

  const renderMiniCalendar = () => {
    const daysInMonth = getDaysInMonth(miniCalendarDate);
    const firstDay = getFirstDayOfMonth(miniCalendarDate);
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="w-8 h-8"></div>);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(
        <button
          key={day}
          onClick={() => handleDateClick(day)}
          className={`w-8 h-8 text-sm rounded transition-colors ${
            isToday(day)
              ? 'bg-blue-600 text-white'
              : 'text-gray-300 hover:bg-[#453f3b] hover:text-white'
          }`}
        >
          {day}
        </button>
      );
    }
    
    return days;
  };

  const getWeekDays = () => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(weekStartDate);
      date.setDate(weekStartDate.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const getDayViewDays = () => {
    const days = [];
    for (let i = -3; i <= 3; i++) {
      const date = new Date(currentDate);
      date.setDate(currentDate.getDate() + i);
      days.push(date);
    }
    return days;
  };

  // Event handlers
  const handleNewEvent = () => {
    setEditingEvent(undefined);
    setSelectedDate(new Date());
    setShowEventModal(true);
  };

  const handleEditEvent = (event: CalendarEvent) => {
    setEditingEvent(event);
    setSelectedDate(undefined);
    setShowEventModal(true);
  };

  const handleSaveEvent = (eventData: Omit<CalendarEvent, 'id'> | CalendarEvent) => {
    if ('id' in eventData) {
      // Editing existing event
      updateEvent(eventData);
    } else {
      // Creating new event
      addEvent(eventData);
    }
    setShowEventModal(false);
    setEditingEvent(undefined);
    setSelectedDate(undefined);
  };

  const handleDeleteEvent = (eventId: string) => {
    deleteEvent(eventId);
    setPreviewEvent(undefined);
  };

  const handleEventClick = (event: CalendarEvent, clickEvent: React.MouseEvent) => {
    setPreviewEvent(event);
    setPreviewPosition({ x: clickEvent.clientX, y: clickEvent.clientY });
  };

  const handleClosePreview = () => {
    setPreviewEvent(undefined);
  };

  const handleDateClick = (day: number) => {
    // Create a new date for the clicked day
    const clickedDate = new Date(miniCalendarDate.getFullYear(), miniCalendarDate.getMonth(), day);
    
    // If we're in week mode, show centered 7-day view around the clicked date
    if (viewMode === 'week') {
      // Center the clicked date - calculate 3 days before
      const centerStart = new Date(clickedDate);
      centerStart.setDate(clickedDate.getDate() - 3);
      setWeekStartDate(centerStart);
    } else {
      // For other modes, calculate the start of the week for this date (Sunday)
      const dayOfWeek = clickedDate.getDay();
      const weekStart = new Date(clickedDate);
      weekStart.setDate(clickedDate.getDate() - dayOfWeek);
      setWeekStartDate(weekStart);
    }
    
    // Update the current date
    setCurrentDate(clickedDate);
  };

  const getTimeSlots = () => {
    const slots = [];
    for (let hour = 0; hour < 24; hour++) {
      const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
      const period = hour < 12 ? 'AM' : 'PM';
      slots.push({
        hour,
        display: `${displayHour} ${period}`,
        time: `${hour.toString().padStart(2, '0')}:00`
      });
    }
    return slots;
  };

  const getMonthDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startDay = firstDay.getDay();
    
    const days = [];
    
    // Previous month's trailing days
    const prevMonth = new Date(year, month - 1, 0);
    for (let i = startDay - 1; i >= 0; i--) {
      days.push({
        date: prevMonth.getDate() - i,
        isCurrentMonth: false,
        fullDate: new Date(year, month - 1, prevMonth.getDate() - i)
      });
    }
    
    // Current month's days
    for (let day = 1; day <= daysInMonth; day++) {
      days.push({
        date: day,
        isCurrentMonth: true,
        fullDate: new Date(year, month, day)
      });
    }
    
    // Next month's leading days
    const remainingSlots = 42 - days.length; // 6 rows × 7 days
    for (let day = 1; day <= remainingSlots; day++) {
      days.push({
        date: day,
        isCurrentMonth: false,
        fullDate: new Date(year, month + 1, day)
      });
    }
    
    return days;
  };

  const navigateDate = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    
    if (viewMode === 'day') {
      newDate.setDate(currentDate.getDate() + (direction === 'next' ? 1 : -1));
    } else if (viewMode === 'week') {
      newDate.setDate(currentDate.getDate() + (direction === 'next' ? 7 : -7));
      const weekStart = new Date(newDate);
      weekStart.setDate(newDate.getDate() - newDate.getDay());
      setWeekStartDate(weekStart);
    } else if (viewMode === 'month') {
      newDate.setMonth(currentDate.getMonth() + (direction === 'next' ? 1 : -1));
    }
    
    setCurrentDate(newDate);
  };

  const formatDateHeader = () => {
    if (viewMode === 'day') {
      return currentDate.toLocaleDateString('en-US', { 
        weekday: 'long', 
        month: 'long', 
        day: 'numeric', 
        year: 'numeric' 
      });
    } else if (viewMode === 'week') {
      const endDate = new Date(weekStartDate);
      endDate.setDate(weekStartDate.getDate() + 6);
      return `${weekStartDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`;
    } else {
      return currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
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
        {/* Calendar Content Area */}
        <div className="flex-1 bg-[#1e1e1e] overflow-y-auto">
          {/* Calendar Header */}
          <div className="p-6 border-b border-[#453f3b]/30">
            <div className="flex items-center justify-between">
              <h1 className="text-white text-2xl font-medium">Calendar</h1>
              <div className="flex items-center space-x-4">
                <div className="flex bg-[#453f3b] rounded-lg p-1">
                  <button 
                    onClick={() => setViewMode('day')}
                    className={`px-4 py-2 rounded text-sm transition-colors ${viewMode === 'day' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'}`}
                  >
                    Day
                  </button>
                  <button 
                    onClick={() => setViewMode('week')}
                    className={`px-4 py-2 rounded text-sm transition-colors ${viewMode === 'week' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'}`}
                  >
                    Week
                  </button>
                  <button 
                    onClick={() => setViewMode('month')}
                    className={`px-4 py-2 rounded text-sm transition-colors ${viewMode === 'month' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'}`}
                  >
                    Month
                  </button>
                </div>
                <button 
                  onClick={handleNewEvent}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Event</span>
                </button>
              </div>
            </div>
          </div>

          {/* Calendar Grid */}
          <div className="p-6 grid grid-cols-1 lg:grid-cols-4 gap-6 max-w-full mx-auto">
            {/* Main Calendar Content */}
            <div className="lg:col-span-3">
              {/* Calendar Header with Navigation */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => navigateDate('prev')}
                    className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-[#453f3b]"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <h2 className="text-2xl font-semibold text-white">{formatDateHeader()}</h2>
                  <button
                    onClick={() => navigateDate('next')}
                    className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-[#453f3b]"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
                <button
                  onClick={() => {
                    const today = new Date();
                    setCurrentDate(today);
                    const weekStart = new Date(today);
                    weekStart.setDate(today.getDate() - today.getDay());
                    setWeekStartDate(weekStart);
                  }}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-[#453f3b] border border-[#453f3b]"
                >
                  Today
                </button>
              </div>

              {/* Calendar Content */}
              <div className="bg-[#1e1e1e] rounded-lg overflow-hidden">
              {/* Day View */}
              {viewMode === 'day' && (
                <div className="h-[600px] overflow-y-auto">
                  {/* Day Header */}
                  <div className="sticky top-0 bg-[#1e1e1e] z-10 border-b border-gray-700 p-4">
                    <div className="text-center">
                      <div className="text-sm text-gray-400">
                        {currentDate.toLocaleDateString('en-US', { weekday: 'long' })}
                      </div>
                      <div className="text-3xl font-light text-white">
                        {currentDate.getDate()}
                      </div>
                    </div>
                  </div>
                  
                  {/* All-day events */}
                  <div className="border-b border-gray-700 p-4">
                    <div className="text-xs text-gray-400 mb-2">all-day</div>
                  </div>
                  
                  {/* Time slots */}
                  <div className="relative">
                    {getTimeSlots().map((slot) => {
                      const dayEvents = getEventsForDate(currentDate);
                      const slotEvents = dayEvents.filter(event => {
                        const eventTime = event.time;
                        const eventHour = parseInt(eventTime.split(':')[0]);
                        return eventHour === slot.hour;
                      });
                      
                      const eventLayouts = calculateEventLayout(slotEvents, 'day');
                      
                      return (
                        <div key={slot.hour} className="flex border-b border-gray-800 h-16">
                          <div className="w-16 flex-shrink-0 p-2 text-xs text-gray-400 text-right">
                            {slot.display}
                          </div>
                          <div className="flex-1 relative border-l border-gray-700">
                            {eventLayouts.map((layout) => {
                              const hasConflict = hasEventConflict(layout.event.id, dayEvents);
                              return (
                                <div
                                  key={layout.event.id}
                                  onClick={(e) => handleEventClick(layout.event, e)}
                                  className={`absolute ${getEventTypeColor(layout.event.type, hasConflict)} rounded text-xs p-2 cursor-pointer hover:opacity-90 transition-all ${hasConflict ? 'ring-1 ring-red-400' : ''}`}
                                  style={{ 
                                    top: `${layout.top}px`,
                                    height: `${layout.height}px`,
                                    left: `${layout.left}%`,
                                    width: layout.width,
                                    zIndex: layout.zIndex
                                  }}
                                  title={hasConflict ? 'This event conflicts with another event' : ''}
                                >
                                  <div className="text-white font-medium truncate text-xs">
                                    {layout.event.title}
                                  </div>
                                  <div className="text-white/80 text-xs">{layout.event.time}</div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Week View */}
              {viewMode === 'week' && (
                <div className="h-[600px] overflow-y-auto">
                  {/* Week headers */}
                  <div className="sticky top-0 bg-[#1e1e1e] z-10 border-b border-gray-700">
                    <div className="flex">
                      <div className="w-16 flex-shrink-0"></div>
                      {getWeekDays().map((date, index) => {
                        const isToday = date.toDateString() === new Date().toDateString();
                        return (
                          <div key={index} className="flex-1 text-center p-4 border-l border-gray-700">
                            <div className={`text-xs ${isToday ? 'text-red-500' : 'text-gray-400'}`}>
                              {date.toLocaleDateString('en-US', { weekday: 'short' })}
                            </div>
                            <div className={`text-2xl font-light ${isToday ? 'text-red-500' : 'text-white'}`}>
                              {date.getDate()}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    
                    {/* All-day events row */}
                    <div className="flex border-t border-gray-700">
                      <div className="w-16 flex-shrink-0 p-2 text-xs text-gray-400">all-day</div>
                      {getWeekDays().map((date, index) => (
                        <div key={index} className="flex-1 border-l border-gray-700 p-1 min-h-[40px]">
                          {/* All-day events would go here */}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Time slots */}
                  <div className="relative">
                    {getTimeSlots().map((slot) => (
                      <div key={slot.hour} className="flex h-16 border-b border-gray-800">
                        <div className="w-16 flex-shrink-0 p-2 text-xs text-gray-400 text-right">
                          {slot.display}
                        </div>
                        {getWeekDays().map((date, dayIndex) => {
                          const dayEvents = getEventsForDate(date);
                          const slotEvents = dayEvents.filter(event => {
                            const eventTime = event.time;
                            const eventHour = parseInt(eventTime.split(':')[0]);
                            return eventHour === slot.hour;
                          });
                          
                          const eventLayouts = calculateEventLayout(slotEvents, 'week');
                          const isToday = date.toDateString() === new Date().toDateString();
                          
                          return (
                            <div key={dayIndex} className={`flex-1 relative border-l border-gray-700 ${isToday ? 'bg-red-900/5' : ''}`}>
                              {eventLayouts.map((layout) => {
                                const hasConflict = hasEventConflict(layout.event.id, dayEvents);
                                return (
                                  <div
                                    key={layout.event.id}
                                    onClick={(e) => handleEventClick(layout.event, e)}
                                    className={`absolute ${getEventTypeColor(layout.event.type, hasConflict)} rounded cursor-pointer hover:opacity-90 transition-all ${hasConflict ? 'ring-1 ring-red-400' : ''}`}
                                    style={{ 
                                      top: `${layout.top}px`,
                                      height: `${Math.max(layout.height, 14)}px`, // Minimum height for week view
                                      left: `${layout.left}%`,
                                      width: layout.width,
                                      zIndex: layout.zIndex,
                                      fontSize: '10px',
                                      padding: '1px 2px'
                                    }}
                                    title={hasConflict ? 'This event conflicts with another event' : ''}
                                  >
                                    <div className="text-white font-medium truncate leading-tight">
                                      {layout.event.title}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          );
                        })}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Month View */}
              {viewMode === 'month' && (
                <div>
                  {/* Month headers */}
                  <div className="grid grid-cols-7 border-b border-gray-700">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                      <div key={day} className="p-4 text-center text-sm font-medium text-gray-400 border-r border-gray-700 last:border-r-0">
                        {day}
                      </div>
                    ))}
                  </div>
                  
                  {/* Month grid */}
                  <div className="grid grid-cols-7" style={{ height: '600px' }}>
                    {getMonthDays().map((day, index) => {
                      const isToday = day.fullDate.toDateString() === new Date().toDateString();
                      const dayEvents = getEventsForDate(day.fullDate);
                      
                      return (
                        <div 
                          key={index} 
                          className={`border-r border-b border-gray-700 last:border-r-0 p-2 h-24 overflow-hidden ${
                            day.isCurrentMonth ? 'bg-[#1e1e1e]' : 'bg-[#151515]'
                          }`}
                          onClick={() => {
                            setCurrentDate(day.fullDate);
                            setViewMode('day');
                          }}
                        >
                          <div className={`text-sm mb-1 ${
                            isToday ? 'w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center font-medium' :
                            day.isCurrentMonth ? 'text-white' : 'text-gray-500'
                          }`}>
                            {day.date}
                          </div>
                          <div className="space-y-1">
                            {dayEvents.slice(0, 3).map((event) => {
                              const hasConflict = hasEventConflict(event.id, dayEvents);
                              return (
                                <div
                                  key={event.id}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleEventClick(event, e);
                                  }}
                                  className={`${getEventTypeColor(event.type, hasConflict)} rounded px-1 py-0.5 text-xs text-white truncate cursor-pointer hover:opacity-80 transition-opacity ${hasConflict ? 'ring-1 ring-red-400' : ''}`}
                                  title={hasConflict ? 'This event conflicts with another event' : ''}
                                >
                                  {hasConflict && '⚠️ '}{event.title}
                                </div>
                              );
                            })}
                            {dayEvents.length > 3 && (
                              <div className="text-xs text-gray-400">+{dayEvents.length - 3} more</div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              </div>
            </div>

            {/* Quick Overview Sidebar */}
            <div className="space-y-6">
              {/* Stats */}
              <div className="bg-[#453f3b] rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Overview</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Today</span>
                    <span className="text-white font-medium">{getTodayEventsCount()} events</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">This Week</span>
                    <span className="text-white font-medium">{getThisWeekEventsCount()} events</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Next Week</span>
                    <span className="text-white font-medium">{getNextWeekEventsCount()} events</span>
                  </div>
                </div>
              </div>

              {/* Mini Calendar */}
              <div className="bg-[#453f3b] rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">
                    {miniCalendarDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </h3>
                  <div className="flex space-x-1">
                    <button
                      onClick={handlePrevMonth}
                      className="p-1 text-gray-400 hover:text-white transition-colors"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={handleNextMonth}
                      className="p-1 text-gray-400 hover:text-white transition-colors"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {/* Day headers */}
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day) => (
                    <div key={day} className="w-8 h-6 text-xs text-gray-400 text-center font-medium">
                      {day}
                    </div>
                  ))}
                </div>
                
                {/* Calendar grid */}
                <div className="grid grid-cols-7 gap-1">
                  {renderMiniCalendar()}
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

      <ChatBox
        onSendMessage={(message) => console.log('Calendar chat:', message)}
        onOpenFullChat={() => onNavigate && onNavigate('main')}
        sidebarCollapsed={isCollapsed}
      />

      {/* Event Modal */}
      <EventModal
        isOpen={showEventModal}
        onClose={() => {
          setShowEventModal(false);
          setEditingEvent(undefined);
          setSelectedDate(undefined);
        }}
        onSave={handleSaveEvent}
        event={editingEvent}
        selectedDate={selectedDate}
      />

      {/* Event Preview */}
      {previewEvent && (
        <EventPreview
          event={previewEvent}
          position={previewPosition}
          onClose={handleClosePreview}
          onEdit={handleEditEvent}
          onDelete={handleDeleteEvent}
        />
      )}
    </div>
  );
};

export default CalendarPage;