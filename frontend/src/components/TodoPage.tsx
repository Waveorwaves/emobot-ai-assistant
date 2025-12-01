import React, { useState } from 'react';
import { Plus, Star, Edit3, Trash2, Check, CheckSquare, Calendar, FolderPlus, Eye, X, ChevronDown, ChevronRight } from 'lucide-react';
import Sidebar from './ui/Sidebar';
import ChatBox from './ui/ChatBox';
import { useData, TodoItem } from '../context/DataContext';


interface TodoPageProps {
  onNavigate?: (page: string) => void;
}

const TodoPage: React.FC<TodoPageProps> = ({ onNavigate }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('todo');
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [newTodo, setNewTodo] = useState<{ title: string; description: string; priority: 'low' | 'medium' | 'high'; category: string; dueDate: string; dueTime: string; isProject: boolean }>({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '', isProject: false });
  const [editingTodo, setEditingTodo] = useState<string | null>(null);
  const [editTodo, setEditTodo] = useState<{ title: string; description: string; priority: 'low' | 'medium' | 'high'; category: string; dueDate: string; dueTime: string }>({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '' });
  const [selectedTodoDetails, setSelectedTodoDetails] = useState<TodoItem | null>(null);
  const [completedTimeFilter, setCompletedTimeFilter] = useState<string>('all');
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(new Set());
  const [addingSubtaskTo, setAddingSubtaskTo] = useState<string | null>(null);
  const [newSubtask, setNewSubtask] = useState({ title: '', description: '', priority: 'medium' as const, category: 'personal', dueDate: '', dueTime: '' });
  const [sortBy, setSortBy] = useState<'date' | 'priority'>('date');
  const [customStat, setCustomStat] = useState<string>('high');
  const [showStatDropdown, setShowStatDropdown] = useState(false);
  const [customCategories, setCustomCategories] = useState<{ id: string, label: string, color: string }[]>(() => {
    try {
      const saved = localStorage.getItem('todoCategories');
      return saved ? JSON.parse(saved) : [
        { id: 'personal', label: 'Personal', color: 'bg-blue-500' },
        { id: 'work', label: 'Work', color: 'bg-green-500' },
        { id: 'study', label: 'Study', color: 'bg-sky-500' },
        { id: 'health', label: 'Health', color: 'bg-red-500' },
        { id: 'finance', label: 'Finance', color: 'bg-yellow-500' },
      ];
    } catch {
      return [
        { id: 'personal', label: 'Personal', color: 'bg-blue-500' },
        { id: 'work', label: 'Work', color: 'bg-green-500' },
        { id: 'study', label: 'Study', color: 'bg-sky-500' },
        { id: 'health', label: 'Health', color: 'bg-red-500' },
        { id: 'finance', label: 'Finance', color: 'bg-yellow-500' },
      ];
    }
  });
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [editingCategory, setEditingCategory] = useState<string | null>(null);
  const [newCategory, setNewCategory] = useState({ label: '', color: 'bg-blue-500' });

  // Get real data from context
  const { todos, toggleTodoComplete, toggleTodoStar, addTodo, updateTodo, deleteTodo, addSubtask, getSubtasks } = useData();

  // Helper function to check if task was completed yesterday (define before using)
  const wasCompletedYesterday = (todo: TodoItem) => {
    return todo.completed && (
      todo.dueDate === 'Yesterday' ||
      todo.dueDate === 'Last Week' ||
      todo.createdAt === 'Yesterday' ||
      todo.createdAt === '1 week ago' ||
      todo.createdAt === '2 days ago'
    );
  };

  // Helper function to convert due date to sortable value
  const getDueDateSortValue = (dueDate?: string) => {
    if (!dueDate) return 9999; // No due date goes to end

    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];

    switch (dueDate.toLowerCase()) {
      case 'today':
        return 0;
      case 'tomorrow':
        const tomorrow = new Date(today);
        tomorrow.setDate(today.getDate() + 1);
        return 1;
      case 'yesterday':
        return -1;
      case 'this weekend':
        return 5;
      case 'next week':
        return 7;
      case 'friday':
        return 4;
      default:
        // Try to parse as date
        try {
          const dueDateTime = new Date(dueDate);
          const todayTime = new Date(todayStr);
          const diffTime = dueDateTime.getTime() - todayTime.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          return diffDays;
        } catch {
          return 9999; // Invalid date goes to end
        }
    }
  };

  const todoFilters = [
    {
      id: 'all',
      label: 'All Tasks',
      count: todos.filter(t => !wasCompletedYesterday(t)).length // Exclude old completed tasks
    },
    { id: 'active', label: 'Active', count: todos.filter(t => !t.completed).length },
    { id: 'completed', label: 'Completed', count: todos.filter(t => t.completed).length },
    { id: 'starred', label: 'Starred', count: todos.filter(t => t.starred).length },
    { id: 'projects', label: 'Projects', count: todos.filter(t => t.isProject).length },
    { id: 'today', label: 'Due Today', count: todos.filter(t => t.dueDate === 'Today').length },
  ];



  const handleToggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    try {
      localStorage.setItem('sidebarCollapsed', String(next));
    } catch { }
  };

  const handleSidebarNavigation = (itemId: string) => {
    setActiveTab(itemId);
    if (onNavigate) {
      onNavigate(itemId);
    }
  };

  // Helper function to categorize completed tasks by time
  const getCompletionTimeCategory = (todo: TodoItem) => {
    if (!todo.completed) return null;

    const createdTime = todo.createdAt.toLowerCase();

    // Today
    if (createdTime.includes('just now') || createdTime.includes('minutes ago') || createdTime.includes('hours ago')) {
      return 'today';
    }

    // This week
    if (createdTime.includes('yesterday') || createdTime === '1 day ago' || createdTime === '2 days ago') {
      return 'this-week';
    }

    // This month  
    if (createdTime.includes('1 week ago') || createdTime.includes('2 weeks ago') || createdTime.includes('3 weeks ago')) {
      return 'this-month';
    }

    // Past 3 months
    if (createdTime.includes('1 month ago') || createdTime.includes('2 months ago') || createdTime.includes('3 months ago')) {
      return 'past-3-months';
    }

    // Older
    return 'older';
  };

  const completedTimeFilters = [
    { id: 'all', label: 'All Completed', count: todos.filter(t => t.completed).length },
    { id: 'today', label: 'Done Today', count: todos.filter(t => t.completed && getCompletionTimeCategory(t) === 'today').length },
    { id: 'this-week', label: 'This Week', count: todos.filter(t => t.completed && getCompletionTimeCategory(t) === 'this-week').length },
    { id: 'this-month', label: 'This Month', count: todos.filter(t => t.completed && getCompletionTimeCategory(t) === 'this-month').length },
    { id: 'past-3-months', label: 'Past 3 Months', count: todos.filter(t => t.completed && getCompletionTimeCategory(t) === 'past-3-months').length },
  ];

  const filteredTodos = todos.filter(todo => {
    // Exclude subtasks from main list (they'll show under projects)
    if (todo.parentId) return false;

    // Handle old completed tasks - only show in "completed" filter
    if (wasCompletedYesterday(todo)) {
      return activeFilter === 'completed';
    }

    switch (activeFilter) {
      case 'active':
        return !todo.completed;
      case 'completed':
        // Apply time-based filter for completed tasks
        if (!todo.completed) return false;

        if (completedTimeFilter === 'all') {
          return true;
        } else {
          return getCompletionTimeCategory(todo) === completedTimeFilter;
        }
      case 'starred':
        return todo.starred;
      case 'projects':
        return todo.isProject;
      case 'today':
        return todo.dueDate === 'Today';
      default:
        // For "all" filter, exclude old completed tasks
        return activeFilter === 'all' ? !wasCompletedYesterday(todo) : true;
    }
  }).sort((a, b) => {
    // For "All Tasks" view, sort completed tasks to bottom
    if (activeFilter === 'all') {
      if (a.completed !== b.completed) {
        return a.completed ? 1 : -1; // Completed tasks go to bottom
      }
    }

    // Sort by the selected criteria
    if (sortBy === 'date') {
      // Sort by due date first
      const aDueValue = getDueDateSortValue(a.dueDate);
      const bDueValue = getDueDateSortValue(b.dueDate);

      if (aDueValue !== bDueValue) {
        return aDueValue - bDueValue; // Earlier due dates first
      }

      // If due dates are same, sort by priority (high first)
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      if (a.priority !== b.priority) {
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      }
    } else {
      // Sort by priority first
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      if (a.priority !== b.priority) {
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      }

      // If priorities are same, sort by due date
      const aDueValue = getDueDateSortValue(a.dueDate);
      const bDueValue = getDueDateSortValue(b.dueDate);

      if (aDueValue !== bDueValue) {
        return aDueValue - bDueValue; // Earlier due dates first
      }
    }

    // Finally sort by ID (newer first)
    return parseInt(b.id) - parseInt(a.id);
  });

  const getPriorityColor = (priority: TodoItem['priority']) => {
    switch (priority) {
      case 'high':
        return 'text-red-400 bg-red-900/20 border-red-700';
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/20 border-yellow-700';
      case 'low':
        return 'text-green-400 bg-green-900/20 border-green-700';
    }
  };


  const handleDeleteTodo = (todoId: string) => {
    deleteTodo(todoId);
  };

  const handleAddTodo = () => {
    if (!newTodo.title.trim()) return;

    // Combine date and time if both are provided
    let combinedDueDate = newTodo.dueDate;
    if (newTodo.dueDate && newTodo.dueTime) {
      combinedDueDate = `${newTodo.dueDate}T${newTodo.dueTime}`;
    }

    const todo = {
      title: newTodo.title,
      description: newTodo.description,
      completed: false,
      priority: newTodo.priority,
      category: newTodo.category,
      dueDate: combinedDueDate,
      createdAt: 'Just now',
      starred: false,
      isProject: newTodo.isProject,
      subtasks: newTodo.isProject ? [] : undefined
    };

    addTodo(todo);
    setNewTodo({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '', isProject: false });
    setShowAddForm(false);
    setShowProjectForm(false);
  };

  const handleEditTodo = (todo: TodoItem) => {
    setEditingTodo(todo.id);
    setEditTodo({
      title: todo.title,
      description: todo.description || '',
      priority: todo.priority as 'low' | 'medium' | 'high',
      category: todo.category,
      dueDate: todo.dueDate || '',
      dueTime: ''
    });
  };

  const handleSaveEdit = () => {
    if (!editTodo.title.trim() || !editingTodo) return;

    // Combine date and time if both are provided
    let combinedDueDate = editTodo.dueDate;
    if (editTodo.dueDate && editTodo.dueTime) {
      combinedDueDate = `${editTodo.dueDate}T${editTodo.dueTime}`;
    }

    updateTodo(editingTodo, {
      title: editTodo.title,
      description: editTodo.description,
      priority: editTodo.priority,
      category: editTodo.category,
      dueDate: combinedDueDate
    });

    setEditingTodo(null);
    setEditTodo({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '' });
  };

  const handleCancelEdit = () => {
    setEditingTodo(null);
    setEditTodo({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '' });
  };

  const toggleProjectExpansion = (projectId: string) => {
    setExpandedProjects(prev => {
      const newSet = new Set(prev);
      if (newSet.has(projectId)) {
        newSet.delete(projectId);
      } else {
        newSet.add(projectId);
      }
      return newSet;
    });
  };

  const handleAddSubtask = (projectId: string) => {
    if (!newSubtask.title.trim()) return;

    // Combine date and time if both are provided
    let combinedDueDate = newSubtask.dueDate;
    if (newSubtask.dueDate && newSubtask.dueTime) {
      combinedDueDate = `${newSubtask.dueDate}T${newSubtask.dueTime}`;
    }

    const subtask = {
      title: newSubtask.title,
      description: newSubtask.description,
      completed: false,
      priority: newSubtask.priority,
      category: newSubtask.category,
      dueDate: combinedDueDate,
      createdAt: 'Just now',
      starred: false
    };

    addSubtask(projectId, subtask);
    setNewSubtask({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '' });
    setAddingSubtaskTo(null);
  };

  // Category management functions
  const saveCategoriesToStorage = (categories: typeof customCategories) => {
    try {
      localStorage.setItem('todoCategories', JSON.stringify(categories));
    } catch { }
  };

  const addCategory = () => {
    if (!newCategory.label.trim()) return;

    const categoryId = newCategory.label.toLowerCase().replace(/\s+/g, '-');
    const newCat = {
      id: categoryId,
      label: newCategory.label,
      color: newCategory.color
    };

    const updated = [...customCategories, newCat];
    setCustomCategories(updated);
    saveCategoriesToStorage(updated);
    setNewCategory({ label: '', color: 'bg-blue-500' });
    setShowAddCategory(false);
  };

  const editCategory = (categoryId: string) => {
    const category = customCategories.find(c => c.id === categoryId);
    if (category) {
      setEditingCategory(categoryId);
      setNewCategory({ label: category.label, color: category.color });
    }
  };

  const saveEditCategory = () => {
    if (!newCategory.label.trim() || !editingCategory) return;

    const updated = customCategories.map(cat =>
      cat.id === editingCategory
        ? { ...cat, label: newCategory.label, color: newCategory.color }
        : cat
    );

    setCustomCategories(updated);
    saveCategoriesToStorage(updated);
    setEditingCategory(null);
    setNewCategory({ label: '', color: 'bg-blue-500' });
  };

  const deleteCategory = (categoryId: string) => {
    // Don't allow deleting if there are todos using this category
    const hasTodos = todos.some(t => t.category === categoryId);
    if (hasTodos) {
      alert('Cannot delete category with existing todos. Please change the category of existing todos first.');
      return;
    }

    const updated = customCategories.filter(cat => cat.id !== categoryId);
    setCustomCategories(updated);
    saveCategoriesToStorage(updated);
  };

  const getCategoryColor = (categoryId: string) => {
    const category = customCategories.find(cat => cat.id === categoryId);
    return category?.color || 'bg-gray-500';
  };

  const getCustomStatValue = () => {
    switch (customStat) {
      case 'high':
        return todos.filter(t => t.priority === 'high').length;
      case 'starred':
        return todos.filter(t => t.starred).length;
      case 'projects':
        return todos.filter(t => t.isProject).length;
      case 'thisMonth':
        return todos.filter(t => {
          const dueValue = getDueDateSortValue(t.dueDate);
          return dueValue >= 0 && dueValue <= 30; // Tasks due within 30 days
        }).length;
      default:
        // Check if it's a custom category
        const isCategory = customCategories.some(cat => cat.id === customStat);
        if (isCategory) {
          return todos.filter(t => t.category === customStat).length;
        }
        return 0;
    }
  };

  const getCustomStatLabel = () => {
    switch (customStat) {
      case 'high':
        return 'High';
      case 'starred':
        return 'Starred';
      case 'projects':
        return 'Projects';
      case 'thisMonth':
        return 'This Month';
      default:
        // Check if it's a custom category
        const category = customCategories.find(cat => cat.id === customStat);
        if (category) {
          return category.label;
        }
        return customStat.charAt(0).toUpperCase() + customStat.slice(1);
    }
  };

  const getCustomStatColor = () => {
    switch (customStat) {
      case 'high':
        return 'text-red-400';
      case 'starred':
        return 'text-yellow-400';
      case 'projects':
        return 'text-green-400';
      case 'thisMonth':
        return 'text-sky-400';
      default:
        // For category stats, use the category color but convert to text color
        const category = customCategories.find(cat => cat.id === customStat);
        if (category) {
          const colorMap: { [key: string]: string } = {
            'bg-blue-500': 'text-blue-400',
            'bg-green-500': 'text-green-400',
            'bg-sky-500': 'text-sky-400',
            'bg-red-500': 'text-red-400',
            'bg-yellow-500': 'text-yellow-400',
            'bg-pink-500': 'text-pink-400',
            'bg-cyan-500': 'text-cyan-400',
            'bg-orange-500': 'text-orange-400'
          };
          return colorMap[category.color] || 'text-gray-400';
        }
        return 'text-gray-400';
    }
  };

  const stats = {
    today: todos.filter(t => t.dueDate === 'Today').length,
    thisWeek: todos.filter(t => t.dueDate === 'Today' || t.dueDate === 'Tomorrow' || t.dueDate === 'This Weekend' || t.dueDate === 'Friday').length,
    completed: todos.filter(t => t.completed && getCompletionTimeCategory(t) === 'today').length,
    custom: getCustomStatValue()
  };

  return (
    <div className="h-screen bg-transparent">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-64'} transition-all duration-300 flex flex-col h-screen`}>
        {/* Main Header */}
        <div className="p-6 border-b border-primary-500/60">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-500/10 border border-primary-500/60 rounded-lg shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                <CheckSquare className="w-6 h-6 text-primary-400" />
              </div>
              <div>
                <h1 className="text-white text-2xl font-display font-bold tracking-tight">Tasks & Projects</h1>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* Todo Filters Sidebar */}
          <div className="w-64 h-full flex-shrink-0 glass-panel border-r border-primary-500/60 border-l-0 p-4 overflow-y-auto pb-32">
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-display font-bold tracking-tight text-lg text-white">TODO List</h2>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowAddForm(true)}
                  className="btn-neon-flow text-white p-2 rounded-lg font-display font-semibold uppercase tracking-wide text-xs"
                  title="Add Task"
                >
                  <Plus className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setShowProjectForm(true)}
                  className="bg-green-600 hover:bg-green-700 text-white p-2 rounded-lg transition-colors"
                  title="Add Project"
                >
                  <FolderPlus className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="glass-panel rounded-lg p-4 mb-6">
              <h3 className="text-white font-bold mb-3">Overview</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="text-center">
                  <div className="font-display font-bold tracking-tight text-xl text-blue-400">{stats.today}</div>
                  <div className="text-gray-400">Today</div>
                </div>
                <div className="text-center">
                  <div className="font-display font-bold tracking-tight text-xl text-sky-400">{stats.thisWeek}</div>
                  <div className="text-gray-400">This Week</div>
                </div>
                <div className="text-center">
                  <div className="font-display font-bold tracking-tight text-xl text-green-400">{stats.completed}</div>
                  <div className="text-gray-400">Done</div>
                </div>
                <div className="text-center relative">
                  <div className={`font-display font-bold tracking-tight text-xl ${getCustomStatColor()}`}>{stats.custom}</div>
                  <button
                    onClick={() => setShowStatDropdown(!showStatDropdown)}
                    className="flex items-center justify-center w-full space-x-1 text-gray-400 hover:text-white transition-colors"
                  >
                    <span>{getCustomStatLabel()}</span>
                    <ChevronDown className="w-3 h-3" />
                  </button>

                  {showStatDropdown && (
                    <div className="absolute top-full left-0 right-0 mt-1 glass-panel border border-primary-500/60 rounded-lg shadow-lg z-50">
                      <div className="py-1">
                        {[
                          { id: 'high', label: 'High Priority' },
                          { id: 'starred', label: 'Starred' },
                          { id: 'projects', label: 'Projects' },
                          { id: 'thisMonth', label: 'This Month' },
                          ...customCategories.map(cat => ({ id: cat.id, label: cat.label }))
                        ].map(option => (
                          <button
                            key={option.id}
                            onClick={() => {
                              setCustomStat(option.id as any);
                              setShowStatDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm transition-colors ${customStat === option.id
                              ? 'bg-primary-600 text-white'
                              : 'text-white/70 hover:bg-white/10 hover:text-white'
                              }`}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="space-y-2">
              {todoFilters.map(filter => (
                <button
                  key={filter.id}
                  onClick={() => setActiveFilter(filter.id)}
                  className={`relative w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-all duration-200 ${activeFilter === filter.id
                    ? 'bg-transparent text-white shadow-[0_0_20px_rgba(6,182,212,0.15)] border border-primary-500'
                    : 'text-white/70 hover:text-white hover:bg-accent-500/10 hover:shadow-[0_0_15px_rgba(236,72,153,0.2)] border border-transparent'
                    }`}
                >
                  {activeFilter === filter.id && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-4 bg-primary-400 rounded-r-full shadow-[0_0_10px_rgba(6,182,212,0.5)]" />
                  )}
                  <span className="capitalize ml-2 font-medium">{filter.label}</span>
                  {filter.count > 0 && (
                    <span className={`${activeFilter === filter.id ? 'bg-primary-500/20 text-primary-200' : 'bg-gray-800 text-gray-400'} text-xs px-2 py-0.5 rounded-full`}>
                      {filter.count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Categories */}
            <div className="mt-8">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-gray-400 text-sm font-medium">Categories</h4>
                <button
                  onClick={() => setShowAddCategory(true)}
                  className="text-gray-400 hover:text-white transition-colors"
                  title="Add Category"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>

              {/* Add Category Form */}
              {showAddCategory && (
                <div className="mb-4 p-3 bg-white/5 rounded-lg space-y-2">
                  <input
                    type="text"
                    placeholder="Category name..."
                    value={newCategory.label}
                    onChange={(e) => setNewCategory(prev => ({ ...prev, label: e.target.value }))}
                    className="w-full p-2 bg-black/20 border border-primary-500/60 rounded text-white text-xs focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-400">Color:</span>
                    {['bg-blue-500', 'bg-green-500', 'bg-sky-500', 'bg-red-500', 'bg-yellow-500', 'bg-pink-500', 'bg-cyan-500', 'bg-orange-500'].map(color => (
                      <button
                        key={color}
                        onClick={() => setNewCategory(prev => ({ ...prev, color }))}
                        className={`w-4 h-4 rounded-full ${color} ${newCategory.color === color ? 'ring-2 ring-white' : ''}`}
                      />
                    ))}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={addCategory}
                      className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs transition-colors"
                    >
                      Add
                    </button>
                    <button
                      onClick={() => {
                        setShowAddCategory(false);
                        setNewCategory({ label: '', color: 'bg-blue-500' });
                      }}
                      className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1 rounded text-xs transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Edit Category Form */}
              {editingCategory && (
                <div className="mb-4 p-3 bg-white/5 rounded-lg space-y-2">
                  <input
                    type="text"
                    placeholder="Category name..."
                    value={newCategory.label}
                    onChange={(e) => setNewCategory(prev => ({ ...prev, label: e.target.value }))}
                    className="w-full p-2 bg-black/20 border border-primary-500/60 rounded text-white text-xs focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-400">Color:</span>
                    {['bg-blue-500', 'bg-green-500', 'bg-sky-500', 'bg-red-500', 'bg-yellow-500', 'bg-pink-500', 'bg-cyan-500', 'bg-orange-500'].map(color => (
                      <button
                        key={color}
                        onClick={() => setNewCategory(prev => ({ ...prev, color }))}
                        className={`w-4 h-4 rounded-full ${color} ${newCategory.color === color ? 'ring-2 ring-white' : ''}`}
                      />
                    ))}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={saveEditCategory}
                      className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs transition-colors"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setEditingCategory(null);
                        setNewCategory({ label: '', color: 'bg-blue-500' });
                      }}
                      className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1 rounded text-xs transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                {customCategories.map(category => (
                  <div key={category.id} className="flex items-center justify-between group">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${category.color}`} />
                      <span className="text-gray-300 text-sm">{category.label}</span>
                      <span className="text-xs text-gray-500">
                        ({todos.filter(t => t.category === category.id).length})
                      </span>
                    </div>
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => editCategory(category.id)}
                        className="text-gray-500 hover:text-white p-1"
                        title="Edit"
                      >
                        <Edit3 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => deleteCategory(category.id)}
                        className="text-gray-500 hover:text-red-400 p-1"
                        title="Delete"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Todo List */}
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-white/10 flex-shrink-0">
              <div className="flex items-center justify-between mb-4">
                <h1 className="text-2xl font-light text-white capitalize">
                  {activeFilter === 'all' ? 'All Tasks' : activeFilter} ({filteredTodos.length})
                </h1>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setSortBy('date')}
                    className={`px-3 py-1 text-sm transition-colors ${sortBy === 'date'
                      ? 'text-primary-400 bg-primary-900/20 border border-primary-600 rounded'
                      : 'text-white/70 hover:text-white'
                      }`}
                  >
                    Sort by Date
                  </button>
                  <button
                    onClick={() => setSortBy('priority')}
                    className={`px-3 py-1 text-sm transition-colors ${sortBy === 'priority'
                      ? 'text-primary-400 bg-primary-900/20 border border-primary-600 rounded'
                      : 'text-white/70 hover:text-white'
                      }`}
                  >
                    Sort by Priority
                  </button>
                </div>
              </div>

              {/* Time-based filters for completed tasks */}
              {activeFilter === 'completed' && (
                <div className="flex items-center space-x-2 flex-wrap gap-2">
                  {completedTimeFilters.map(filter => (
                    <button
                      key={filter.id}
                      onClick={() => setCompletedTimeFilter(filter.id)}
                      className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${completedTimeFilter === filter.id
                        ? 'bg-primary-600 text-white'
                        : 'bg-white/10 text-white/70 hover:text-white hover:bg-white/20'
                        }`}
                    >
                      <span>{filter.label}</span>
                      {filter.count > 0 && (
                        <span className={`text-xs px-1.5 py-0.5 rounded-full ${completedTimeFilter === filter.id
                          ? 'bg-blue-500'
                          : 'bg-gray-600'
                          }`}>
                          {filter.count}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Add Task Form */}
            {(showAddForm || showProjectForm) && (
              <div className="p-6 bg-white/5 border-b border-primary-500/60 backdrop-blur-sm flex-shrink-0">
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-white font-medium">
                      {showProjectForm ? 'New Project' : 'New Task'}
                    </h3>
                    {showProjectForm && (
                      <span className="text-xs text-green-400 bg-green-900/20 px-2 py-1 rounded-full">
                        Project
                      </span>
                    )}
                  </div>

                  <input
                    type="text"
                    placeholder={showProjectForm ? "Project title..." : "Task title..."}
                    value={newTodo.title}
                    onChange={(e) => setNewTodo(prev => ({ ...prev, title: e.target.value, isProject: showProjectForm }))}
                    className="w-full p-3 bg-black/50 border border-primary-500/60 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <textarea
                    placeholder="Description (optional)..."
                    value={newTodo.description}
                    onChange={(e) => setNewTodo(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full p-3 bg-black/50 border border-primary-500/60 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                    rows={3}
                  />

                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-400 text-sm">Priority:</span>
                      <select
                        value={newTodo.priority}
                        onChange={(e) => setNewTodo(prev => ({ ...prev, priority: e.target.value as any }))}
                        className="bg-black/50 border border-primary-500/60 rounded text-white text-sm p-1 focus:outline-none"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-gray-400 text-sm">Category:</span>
                      <select
                        value={newTodo.category}
                        onChange={(e) => setNewTodo(prev => ({ ...prev, category: e.target.value }))}
                        className="bg-black/50 border border-primary-500/60 rounded text-white text-sm p-1 focus:outline-none"
                      >
                        {customCategories.map(cat => (
                          <option key={cat.id} value={cat.id}>{cat.label}</option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-gray-400 text-sm">Due:</span>
                      <input
                        type="date"
                        value={newTodo.dueDate}
                        onChange={(e) => setNewTodo(prev => ({ ...prev, dueDate: e.target.value }))}
                        className="bg-black/50 border border-primary-500/60 rounded text-white text-sm p-1 focus:outline-none"
                      />
                      <input
                        type="time"
                        value={newTodo.dueTime}
                        onChange={(e) => setNewTodo(prev => ({ ...prev, dueTime: e.target.value }))}
                        className="bg-black/50 border border-primary-500/60 rounded text-white text-sm p-1 focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 pt-2">
                    <button
                      onClick={handleAddTodo}
                      className="btn-neon-flow text-white px-4 py-2 rounded-lg font-medium"
                    >
                      {showProjectForm ? 'Create Project' : 'Add Task'}
                    </button>
                    <button
                      onClick={() => {
                        setShowAddForm(false);
                        setShowProjectForm(false);
                        setNewTodo({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '', isProject: false });
                      }}
                      className="text-gray-400 hover:text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Tasks */}
            <div className="flex-1 overflow-y-auto">
              {filteredTodos.length === 0 ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <CheckSquare className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">No tasks found</p>
                  </div>
                </div>
              ) : (
                <div className="p-6 space-y-4 pb-32">
                  {filteredTodos.map(todo => (
                    <div
                      key={todo.id}
                      className={`bg-white/5 rounded-lg p-4 border border-white/10 transition-all hover:border-primary-500/50 ${todo.completed ? 'opacity-60' : ''
                        } ${todo.isProject ? 'border-l-4 border-l-green-500' : ''}`}
                    >
                      {editingTodo === todo.id ? (
                        // Edit Mode
                        <div className="space-y-3">
                          <input
                            type="text"
                            value={editTodo.title}
                            onChange={(e) => setEditTodo(prev => ({ ...prev, title: e.target.value }))}
                            className="w-full p-2 bg-[#1e1e1e] border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <textarea
                            value={editTodo.description}
                            onChange={(e) => setEditTodo(prev => ({ ...prev, description: e.target.value }))}
                            className="w-full p-2 bg-[#1e1e1e] border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                            rows={2}
                          />
                          <div className="flex items-center space-x-2">
                            <select
                              value={editTodo.priority}
                              onChange={(e) => setEditTodo(prev => ({ ...prev, priority: e.target.value as any }))}
                              className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                            >
                              <option value="low">Low</option>
                              <option value="medium">Medium</option>
                              <option value="high">High</option>
                            </select>
                            <select
                              value={editTodo.category}
                              onChange={(e) => setEditTodo(prev => ({ ...prev, category: e.target.value }))}
                              className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                            >
                              {customCategories.map(cat => (
                                <option key={cat.id} value={cat.id}>{cat.label}</option>
                              ))}
                            </select>
                            <input
                              type="date"
                              value={editTodo.dueDate}
                              onChange={(e) => setEditTodo(prev => ({ ...prev, dueDate: e.target.value }))}
                              className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                            />
                            <input
                              type="time"
                              value={editTodo.dueTime}
                              onChange={(e) => setEditTodo(prev => ({ ...prev, dueTime: e.target.value }))}
                              className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                              placeholder="HH:MM"
                            />
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={handleSaveEdit}
                              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors"
                            >
                              Save
                            </button>
                            <button
                              onClick={handleCancelEdit}
                              className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        // View Mode
                        <div className="flex items-start space-x-4">
                          <div className="flex items-center space-x-2">
                            {todo.isProject && (
                              <button
                                onClick={() => toggleProjectExpansion(todo.id)}
                                className="text-gray-400 hover:text-white"
                              >
                                {expandedProjects.has(todo.id) ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                              </button>
                            )}

                            <button
                              onClick={() => toggleTodoComplete(todo.id)}
                              className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${todo.completed
                                ? 'bg-green-600 border-green-600 text-white'
                                : 'border-gray-400 hover:border-green-400'
                                }`}
                            >
                              {todo.completed && <Check className="w-3 h-3" />}
                            </button>
                          </div>

                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <h4 className={`font-medium ${todo.completed ? 'line-through text-gray-400' : 'text-white'}`}>
                                  {todo.title}
                                </h4>
                                {todo.isProject && (
                                  <span className="text-xs text-green-400 bg-green-900/20 px-2 py-1 rounded-full">
                                    Project ({getSubtasks(todo.id).length} tasks)
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={() => setSelectedTodoDetails(todo)}
                                  className="text-gray-400 hover:text-blue-400"
                                  title="View details"
                                >
                                  <Eye className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => toggleTodoStar(todo.id)}
                                  className={`${todo.starred ? 'text-yellow-400' : 'text-gray-400 hover:text-yellow-400'}`}
                                >
                                  <Star className={`w-4 h-4 ${todo.starred ? 'fill-current' : ''}`} />
                                </button>
                                <button
                                  onClick={() => handleEditTodo(todo)}
                                  className="text-gray-400 hover:text-white"
                                >
                                  <Edit3 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteTodo(todo.id)}
                                  className="text-gray-400 hover:text-red-400"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </div>

                            {todo.description && (
                              <p className={`text-sm mb-3 ${todo.completed ? 'text-gray-500' : 'text-gray-300'}`}>
                                {todo.description}
                              </p>
                            )}

                            {/* Project preview - show recent undone subtasks */}
                            {todo.isProject && !expandedProjects.has(todo.id) && (
                              <div className="mb-3">
                                {(() => {
                                  const subtasks = getSubtasks(todo.id);
                                  const uncompletedSubtasks = subtasks.filter(s => !s.completed).slice(0, 1);

                                  if (uncompletedSubtasks.length > 0) {
                                    return (
                                      <div className="space-y-1">
                                        <p className="text-xs text-gray-400 font-medium">Next tasks:</p>
                                        {uncompletedSubtasks.map(subtask => (
                                          <div key={subtask.id} className="flex items-center space-x-2 text-sm text-gray-400">
                                            <div className="w-2 h-2 border border-gray-500 rounded-sm" />
                                            <span className="truncate">{subtask.title}</span>
                                            {subtask.dueDate && (
                                              <span className="text-xs text-gray-500">({subtask.dueDate})</span>
                                            )}
                                          </div>
                                        ))}
                                        {subtasks.filter(s => !s.completed).length > 1 && (
                                          <p className="text-xs text-gray-500">
                                            +{subtasks.filter(s => !s.completed).length - 1} more tasks
                                          </p>
                                        )}
                                      </div>
                                    );
                                  } else if (subtasks.length > 0) {
                                    return (
                                      <p className="text-sm text-green-400">All tasks completed! ✓</p>
                                    );
                                  } else {
                                    return (
                                      <p className="text-sm text-gray-500">Click to add tasks to this project</p>
                                    );
                                  }
                                })()}
                              </div>
                            )}

                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <span className={`px-2 py-1 rounded text-xs border ${getPriorityColor(todo.priority)}`}>
                                  {todo.priority.toUpperCase()}
                                </span>
                                <div className="flex items-center space-x-1">
                                  <div className={`w-2 h-2 rounded-full ${getCategoryColor(todo.category)}`} />
                                  <span className="text-xs text-gray-400 capitalize">{todo.category}</span>
                                </div>
                              </div>

                              <div className="flex items-center space-x-3 text-xs text-gray-500">
                                {todo.dueDate && <span>Due: {todo.dueDate}</span>}
                                <span>Created: {todo.createdAt}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Subtasks section for expanded projects */}
                      {todo.isProject && expandedProjects.has(todo.id) && (
                        <div className="mt-4 ml-6 space-y-3">
                          {/* Existing subtasks */}
                          {getSubtasks(todo.id).map(subtask => (
                            <div key={subtask.id} className="bg-white/5 rounded-lg p-3 border border-white/10">
                              {editingTodo === subtask.id ? (
                                // Edit Mode for Subtask
                                <div className="space-y-3">
                                  <input
                                    type="text"
                                    value={editTodo.title}
                                    onChange={(e) => setEditTodo(prev => ({ ...prev, title: e.target.value }))}
                                    className="w-full p-2 bg-[#1e1e1e] border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                  />
                                  <textarea
                                    value={editTodo.description}
                                    onChange={(e) => setEditTodo(prev => ({ ...prev, description: e.target.value }))}
                                    className="w-full p-2 bg-[#1e1e1e] border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                    rows={2}
                                  />
                                  <div className="flex items-center space-x-2">
                                    <select
                                      value={editTodo.priority}
                                      onChange={(e) => setEditTodo(prev => ({ ...prev, priority: e.target.value as any }))}
                                      className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                                    >
                                      <option value="low">Low</option>
                                      <option value="medium">Medium</option>
                                      <option value="high">High</option>
                                    </select>
                                    <select
                                      value={editTodo.category}
                                      onChange={(e) => setEditTodo(prev => ({ ...prev, category: e.target.value }))}
                                      className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                                    >
                                      {customCategories.map(cat => (
                                        <option key={cat.id} value={cat.id}>{cat.label}</option>
                                      ))}
                                    </select>
                                    <input
                                      type="date"
                                      value={editTodo.dueDate}
                                      onChange={(e) => setEditTodo(prev => ({ ...prev, dueDate: e.target.value }))}
                                      className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                                    />
                                    <input
                                      type="time"
                                      value={editTodo.dueTime}
                                      onChange={(e) => setEditTodo(prev => ({ ...prev, dueTime: e.target.value }))}
                                      className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                                      placeholder="HH:MM"
                                    />
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <button
                                      onClick={handleSaveEdit}
                                      className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors"
                                    >
                                      Save
                                    </button>
                                    <button
                                      onClick={handleCancelEdit}
                                      className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors"
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                // View Mode for Subtask
                                <div className="flex items-start space-x-3">
                                  <button
                                    onClick={() => toggleTodoComplete(subtask.id)}
                                    className={`flex-shrink-0 w-4 h-4 rounded border-2 flex items-center justify-center transition-colors ${subtask.completed
                                      ? 'bg-green-600 border-green-600 text-white'
                                      : 'border-gray-500 hover:border-green-400'
                                      }`}
                                  >
                                    {subtask.completed && <Check className="w-2.5 h-2.5" />}
                                  </button>

                                  <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                      <h5 className={`text-sm font-medium ${subtask.completed ? 'line-through text-gray-500' : 'text-gray-200'}`}>
                                        {subtask.title}
                                      </h5>
                                      <div className="flex items-center space-x-1">
                                        <button
                                          onClick={() => toggleTodoStar(subtask.id)}
                                          className={`${subtask.starred ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'}`}
                                        >
                                          <Star className={`w-3 h-3 ${subtask.starred ? 'fill-current' : ''}`} />
                                        </button>
                                        <button
                                          onClick={() => handleEditTodo(subtask)}
                                          className="text-gray-500 hover:text-white"
                                        >
                                          <Edit3 className="w-3 h-3" />
                                        </button>
                                        <button
                                          onClick={() => deleteTodo(subtask.id)}
                                          className="text-gray-500 hover:text-red-400"
                                        >
                                          <Trash2 className="w-3 h-3" />
                                        </button>
                                      </div>
                                    </div>
                                    {subtask.description && (
                                      <p className="text-xs text-gray-400 mb-2">{subtask.description}</p>
                                    )}
                                    <div className="flex items-center space-x-2">
                                      <span className={`px-2 py-0.5 rounded text-xs border ${getPriorityColor(subtask.priority)}`}>
                                        {subtask.priority.toUpperCase()}
                                      </span>
                                      {subtask.dueDate && (
                                        <span className="text-xs text-gray-500">Due: {subtask.dueDate}</span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}

                          {/* Add subtask form */}
                          {addingSubtaskTo === todo.id ? (
                            <div className="bg-white/5 rounded-lg p-3 border border-white/10 space-y-3">
                              <input
                                type="text"
                                placeholder="Subtask title..."
                                value={newSubtask.title}
                                onChange={(e) => setNewSubtask(prev => ({ ...prev, title: e.target.value }))}
                                className="w-full p-2 bg-[#1e1e1e] border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                              />
                              <textarea
                                placeholder="Description (optional)..."
                                value={newSubtask.description}
                                onChange={(e) => setNewSubtask(prev => ({ ...prev, description: e.target.value }))}
                                className="w-full p-2 bg-[#1e1e1e] border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                rows={2}
                              />
                              <div className="flex items-center space-x-2">
                                <select
                                  value={newSubtask.priority}
                                  onChange={(e) => setNewSubtask(prev => ({ ...prev, priority: e.target.value as any }))}
                                  className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                                >
                                  <option value="low">Low</option>
                                  <option value="medium">Medium</option>
                                  <option value="high">High</option>
                                </select>
                                <input
                                  type="date"
                                  value={newSubtask.dueDate}
                                  onChange={(e) => setNewSubtask(prev => ({ ...prev, dueDate: e.target.value }))}
                                  className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                                />
                                <input
                                  type="time"
                                  value={newSubtask.dueTime}
                                  onChange={(e) => setNewSubtask(prev => ({ ...prev, dueTime: e.target.value }))}
                                  className="p-1 bg-[#1e1e1e] border border-gray-600 rounded text-white text-xs focus:outline-none"
                                  placeholder="HH:MM"
                                />
                              </div>
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={() => handleAddSubtask(todo.id)}
                                  className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors"
                                >
                                  Add Subtask
                                </button>
                                <button
                                  onClick={() => {
                                    setAddingSubtaskTo(null);
                                    setNewSubtask({ title: '', description: '', priority: 'medium', category: 'personal', dueDate: '', dueTime: '' });
                                  }}
                                  className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <button
                              onClick={() => setAddingSubtaskTo(todo.id)}
                              className="flex items-center space-x-2 text-gray-400 hover:text-green-400 text-sm transition-colors"
                            >
                              <Plus className="w-4 h-4" />
                              <span>Add Subtask</span>
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <ChatBox
          onSendMessage={(message) => console.log('Todo chat:', message)}
          onOpenFullChat={() => onNavigate && onNavigate('main')}
          sidebarCollapsed={isCollapsed}
        />
      </div>

      {/* Todo Details Modal */}
      {selectedTodoDetails && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1e1e1e] border border-gray-600 rounded-lg w-[600px] max-h-[80vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-600">
              <div className="flex items-center space-x-3">
                <h2 className="text-xl font-medium text-white">{selectedTodoDetails.title}</h2>
                {selectedTodoDetails.isProject && (
                  <span className="text-sm text-green-400 bg-green-900/20 px-3 py-1 rounded-full">
                    Project
                  </span>
                )}
              </div>
              <button
                onClick={() => setSelectedTodoDetails(null)}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 p-6 space-y-6 overflow-y-auto">
              {/* Status and Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => {
                      toggleTodoComplete(selectedTodoDetails.id);
                      setSelectedTodoDetails(prev => prev ? { ...prev, completed: !prev.completed } : null);
                    }}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${selectedTodoDetails.completed
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-600 hover:bg-gray-500 text-gray-200'
                      }`}
                  >
                    <Check className="w-4 h-4" />
                    <span>{selectedTodoDetails.completed ? 'Completed' : 'Mark Complete'}</span>
                  </button>
                  <button
                    onClick={() => {
                      toggleTodoStar(selectedTodoDetails.id);
                      setSelectedTodoDetails(prev => prev ? { ...prev, starred: !prev.starred } : null);
                    }}
                    className={`p-2 rounded-lg transition-colors ${selectedTodoDetails.starred
                      ? 'text-yellow-400'
                      : 'text-gray-400 hover:text-yellow-400'
                      }`}
                  >
                    <Star className={`w-5 h-5 ${selectedTodoDetails.starred ? 'fill-current' : ''}`} />
                  </button>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      handleEditTodo(selectedTodoDetails);
                      setSelectedTodoDetails(null);
                    }}
                    className="text-gray-400 hover:text-white px-3 py-2 rounded-lg transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      handleDeleteTodo(selectedTodoDetails.id);
                      setSelectedTodoDetails(null);
                    }}
                    className="text-gray-400 hover:text-red-400 px-3 py-2 rounded-lg transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>

              {/* Description */}
              {selectedTodoDetails.description && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">Description</h3>
                  <p className="text-gray-200 bg-white/5 rounded-lg p-4">
                    {selectedTodoDetails.description}
                  </p>
                </div>
              )}

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">Priority</h3>
                  <span className={`px-3 py-1 rounded text-sm border ${getPriorityColor(selectedTodoDetails.priority)}`}>
                    {selectedTodoDetails.priority.toUpperCase()}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">Category</h3>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${getCategoryColor(selectedTodoDetails.category)}`} />
                    <span className="text-gray-200 capitalize">{selectedTodoDetails.category}</span>
                  </div>
                </div>

                {selectedTodoDetails.dueDate && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-400 mb-2">Due Date</h3>
                    <span className="text-gray-200">{selectedTodoDetails.dueDate}</span>
                  </div>
                )}

                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">Created</h3>
                  <span className="text-gray-200">{selectedTodoDetails.createdAt}</span>
                </div>
              </div>

              {/* Subtasks Section (for projects) */}
              {selectedTodoDetails.isProject && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-3">Subtasks ({getSubtasks(selectedTodoDetails.id).length})</h3>
                  <div className="bg-white/5 rounded-lg p-4">
                    {getSubtasks(selectedTodoDetails.id).length === 0 ? (
                      <p className="text-gray-400 text-sm">No subtasks yet. Add some to organize this project!</p>
                    ) : (
                      <div className="space-y-3">
                        {getSubtasks(selectedTodoDetails.id).map(subtask => (
                          <div key={subtask.id} className="flex items-center justify-between bg-[#353535] rounded-lg p-3">
                            <div className="flex items-center space-x-3">
                              <button
                                onClick={() => toggleTodoComplete(subtask.id)}
                                className={`flex-shrink-0 w-4 h-4 rounded border-2 flex items-center justify-center transition-colors ${subtask.completed
                                  ? 'bg-green-600 border-green-600 text-white'
                                  : 'border-gray-500 hover:border-green-400'
                                  }`}
                              >
                                {subtask.completed && <Check className="w-2.5 h-2.5" />}
                              </button>
                              <div>
                                <h4 className={`text-sm font-medium ${subtask.completed ? 'line-through text-gray-500' : 'text-gray-200'}`}>
                                  {subtask.title}
                                </h4>
                                {subtask.description && (
                                  <p className="text-xs text-gray-400">{subtask.description}</p>
                                )}
                                <div className="flex items-center space-x-2 mt-1">
                                  <span className={`px-2 py-0.5 rounded text-xs border ${getPriorityColor(subtask.priority)}`}>
                                    {subtask.priority.toUpperCase()}
                                  </span>
                                  {subtask.dueDate && (
                                    <span className="text-xs text-gray-500">Due: {subtask.dueDate}</span>
                                  )}
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => toggleTodoStar(subtask.id)}
                                className={`${subtask.starred ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'}`}
                              >
                                <Star className={`w-3 h-3 ${subtask.starred ? 'fill-current' : ''}`} />
                              </button>
                              <button
                                onClick={() => {
                                  handleEditTodo(subtask);
                                  setSelectedTodoDetails(null);
                                }}
                                className="text-gray-500 hover:text-white"
                              >
                                <Edit3 className="w-3 h-3" />
                              </button>
                              <button
                                onClick={() => deleteTodo(subtask.id)}
                                className="text-gray-500 hover:text-red-400"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TodoPage;