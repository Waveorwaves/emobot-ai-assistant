import React, { useState, useRef } from 'react';
import { Mail, Star, Archive, Trash2, Reply, Forward, MoreHorizontal, Search, Settings, Command, ChevronDown, Clock, Paperclip, X, Send, Tag, RotateCcw, Plus, AlertCircle, XCircle } from 'lucide-react';
import Avatar from './ui/Avatar';
import { useData, Email } from '../context/DataContext';
import Sidebar from './ui/Sidebar';
import ChatBox from './ui/ChatBox';
import { emailApi } from '../utils/api';

interface EmailPageProps {
  onNavigate?: (page: string) => void;
}

const EmailPage: React.FC<EmailPageProps> = ({ onNavigate }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [activeTab, setActiveTab] = useState<string>('email');
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [activeFolder, setActiveFolder] = useState<string>('inbox');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showCompose, setShowCompose] = useState<boolean>(false);
  const [composeForm, setComposeForm] = useState({
    to: '',
    subject: '',
    content: '',
    attachments: [] as File[]
  });
  const [sortBy, setSortBy] = useState<'date' | 'sender' | 'subject'>('date');
  const [showTagModal, setShowTagModal] = useState<boolean>(false);
  const [tagEmail, setTagEmail] = useState<Email | null>(null);
  const [newTag, setNewTag] = useState<string>('');
  const [activeFilterTab, setActiveFilterTab] = useState<string>('all');
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Get real data from context
  const { emails, setEmails, markEmailAsRead, toggleEmailStar, toggleEmailImportant, deleteEmail, archiveEmail, restoreEmail, addEmail, addTagToEmail, removeTagFromEmail } = useData();

  // Tag color system
  const getTagColor = (tag: string) => {
    const colors = {
      work: 'bg-blue-900/30 text-blue-300 border-blue-600/20',
      personal: 'bg-green-900/30 text-green-300 border-green-600/20',
      urgent: 'bg-red-900/30 text-red-300 border-red-600/20',
      important: 'bg-yellow-900/30 text-yellow-300 border-yellow-600/20',
      design: 'bg-purple-900/30 text-purple-300 border-purple-600/20',
      feedback: 'bg-orange-900/30 text-orange-300 border-orange-600/20',
      report: 'bg-indigo-900/30 text-indigo-300 border-indigo-600/20',
      performance: 'bg-pink-900/30 text-pink-300 border-pink-600/20',
      'follow-up': 'bg-teal-900/30 text-teal-300 border-teal-600/20',
      project: 'bg-cyan-900/30 text-cyan-300 border-cyan-600/20',
      meeting: 'bg-violet-900/30 text-violet-300 border-violet-600/20'
    };
    
    // Use clean white color for custom tags (like Claude Code white)
    return colors[tag as keyof typeof colors] || 'bg-white/10 text-white border-white/20';
  };

  const emailFolders = [
    { 
      id: 'inbox', 
      label: 'Inbox', 
      count: emails.filter(email => !email.folder || email.folder === 'inbox').length 
    },
    { 
      id: 'starred', 
      label: 'Starred', 
      count: emails.filter(email => email.starred).length 
    },
    { 
      id: 'sent', 
      label: 'Sent', 
      count: emails.filter(email => email.folder === 'sent').length 
    },
    { 
      id: 'drafts', 
      label: 'Drafts', 
      count: emails.filter(email => email.folder === 'drafts').length 
    },
    { 
      id: 'archive', 
      label: 'Archive', 
      count: emails.filter(email => email.folder === 'archive').length 
    },
    { 
      id: 'trash', 
      label: 'Trash', 
      count: emails.filter(email => email.folder === 'trash').length 
    },
  ];

  // Helper function to get emails for current folder
  const getEmailsForCurrentFolder = () => {
    return emails.filter(email => {
      switch (activeFolder) {
        case 'starred':
          return email.starred;
        case 'sent':
          return email.folder === 'sent';
        case 'drafts':
          return email.folder === 'drafts';
        case 'trash':
          return email.folder === 'trash';
        case 'archive':
          return email.folder === 'archive';
        case 'inbox':
        default:
          return !email.folder || email.folder === 'inbox';
      }
    });
  };

  const currentFolderEmails = getEmailsForCurrentFolder();

  // Get all unique tags from current folder emails
  const getAllTags = () => {
    const tagSet = new Set<string>();
    currentFolderEmails.forEach(email => {
      if (email.tags) {
        email.tags.forEach(tag => tagSet.add(tag));
      }
    });
    return Array.from(tagSet).sort();
  };

  const allTags = getAllTags();

  const filterTabs = [
    { 
      id: 'all', 
      label: 'All', 
      count: currentFolderEmails.length,
      filter: () => true
    },
    { 
      id: 'unread', 
      label: 'Unread', 
      count: currentFolderEmails.filter(email => !email.read).length,
      filter: (email: Email) => !email.read
    },
    { 
      id: 'important', 
      label: 'Important', 
      count: currentFolderEmails.filter(email => email.important).length,
      filter: (email: Email) => email.important
    },
    // Dynamically create filter tabs for all tags
    ...allTags.map(tag => ({
      id: tag,
      label: tag.charAt(0).toUpperCase() + tag.slice(1),
      count: currentFolderEmails.filter(email => email.tags?.includes(tag)).length,
      filter: (email: Email) => email.tags?.includes(tag) || false
    }))
  ];

  const handleEmailClick = async (email: Email) => {
    // Set the email immediately for UI responsiveness
    setSelectedEmail(email);
    
    // Mark as read if unread
    if (!email.read) {
      markEmailAsRead(email.id);
    }

    // Fetch full email content from backend if not already loaded
    if (!email.content || email.content === email.preview) {
      try {
        console.log('Fetching email content for ID:', email.id);
        const response = await emailApi.readEmail(email.id);
        console.log('Email API response:', response);
        
        if (response.success && response.email) {
          console.log('Email data received:', response.email);
          
          // Update the selected email with full content
          const fullEmail = {
            ...email,
            content: response.email.body || response.email.content || response.email.preview || email.preview
          };
          console.log('Setting full email with content:', fullEmail.content);
          setSelectedEmail(fullEmail);
        } else {
          console.warn('Email API returned success=false or no email data');
        }
      } catch (error) {
        console.error('Error fetching email content:', error);
        // Keep showing the preview if fetch fails
      }
    }
  };

  const filteredEmails = emails
    .filter(email => {
      const matchesSearch = !searchQuery || 
        email.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
        email.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
        email.preview.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (email.tags && email.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())));
      
      const matchesFolder = (() => {
        switch (activeFolder) {
          case 'starred':
            return email.starred;
          case 'sent':
            return email.folder === 'sent';
          case 'drafts':
            return email.folder === 'drafts';
          case 'trash':
            return email.folder === 'trash';
          case 'archive':
            return email.folder === 'archive';
          case 'inbox':
          default:
            return !email.folder || email.folder === 'inbox';
        }
      })();

      const matchesFilterTab = (() => {
        const activeTab = filterTabs.find(tab => tab.id === activeFilterTab);
        return activeTab ? activeTab.filter(email) : true;
      })();

      return matchesSearch && matchesFolder && matchesFilterTab;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'sender':
          return a.sender.localeCompare(b.sender);
        case 'subject':
          return a.subject.localeCompare(b.subject);
        case 'date':
        default:
          // Simple date sorting by ID (newer first)
          return parseInt(b.id) - parseInt(a.id);
      }
    });

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

  const handleEmailAction = (action: string, emailId: string) => {
    switch (action) {
      case 'star':
        toggleEmailStar(emailId);
        break;
      case 'important':
        toggleEmailImportant(emailId);
        break;
      case 'delete':
        deleteEmail(emailId);
        if (selectedEmail?.id === emailId) {
          setSelectedEmail(null);
        }
        break;
      case 'archive':
        archiveEmail(emailId);
        if (selectedEmail?.id === emailId) {
          setSelectedEmail(null);
        }
        break;
      case 'restore':
        restoreEmail(emailId);
        if (selectedEmail?.id === emailId) {
          setSelectedEmail(null);
        }
        break;
      case 'move-to-inbox':
        restoreEmail(emailId);
        if (selectedEmail?.id === emailId) {
          setSelectedEmail(null);
        }
        break;
      case 'tag':
        const email = emails.find(e => e.id === emailId);
        if (email) {
          setTagEmail(email);
          setShowTagModal(true);
        }
        break;
      case 'remove-tags':
        const emailToUpdate = emails.find(e => e.id === emailId);
        if (emailToUpdate && emailToUpdate.tags) {
          // Remove all tags from the email
          emailToUpdate.tags.forEach(tag => {
            removeTagFromEmail(emailId, tag);
          });
          // Clear selected email if it's the one being updated
          if (selectedEmail?.id === emailId) {
            setSelectedEmail(prev => prev ? { ...prev, tags: [] } : null);
          }
        }
        break;
      case 'reply':
      case 'forward':
        console.log(`${action} functionality coming soon...`);
        break;
      default:
        console.log(`Action: ${action} on email ${emailId}`);
    }
  };

  const getTimeDisplay = (timestamp: string) => {
    // You could implement more sophisticated time parsing here
    return timestamp;
  };

  const handleCompose = () => {
    setShowCompose(true);
    setComposeForm({ to: '', subject: '', content: '', attachments: [] });
  };

  const handleSendEmail = async () => {
    if (!composeForm.to.trim() || !composeForm.subject.trim() || !composeForm.content.trim()) {
      alert('Please fill in all fields');
      return;
    }

    try {
      // Call the backend API to actually send the email
      const response = await emailApi.sendEmail({
        to: composeForm.to,
        subject: composeForm.subject,
        body: composeForm.content
      });

      if (response.success) {
        setShowCompose(false);
        setComposeForm({ to: '', subject: '', content: '', attachments: [] });
        
        // Show success message
        alert('Email sent successfully!');
        
        // Refresh emails from backend to show the sent email
        // This will fetch from Gmail, so no duplicate email to yourself
        await refreshEmails();
      } else {
        alert('Failed to send email: ' + (response.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error sending email:', error);
      alert('Failed to send email. Please try again.');
    }
  };

  const refreshEmails = async () => {
    try {
      const response = await emailApi.listEmails();
      if (response.success && response.emails) {
        setEmails(response.emails);
      }
    } catch (error) {
      console.error('Error refreshing emails:', error);
    }
  };

  const handleCancelCompose = () => {
    setShowCompose(false);
    setComposeForm({ to: '', subject: '', content: '', attachments: [] });
  };

  const handleFileAttachment = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setComposeForm(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...files]
    }));
  };

  const removeAttachment = (index: number) => {
    setComposeForm(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  const handleAddTag = () => {
    if (newTag.trim() && tagEmail) {
      const tag = newTag.trim();
      addTagToEmail(tagEmail.id, tag);
      // Update local state to reflect the change immediately
      setTagEmail(prev => prev ? {
        ...prev,
        tags: [...(prev.tags || []), tag].filter((t, index, arr) => arr.indexOf(t) === index)
      } : null);
      setNewTag('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    if (tagEmail) {
      removeTagFromEmail(tagEmail.id, tag);
      // Update local state to reflect the change immediately
      setTagEmail(prev => prev ? {
        ...prev,
        tags: (prev.tags || []).filter(t => t !== tag)
      } : null);
    }
  };

  const closeTagModal = () => {
    setShowTagModal(false);
    setTagEmail(null);
    setNewTag('');
  };

  return (
    <div className="h-screen bg-[#0a0a0a] text-white">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
        activeTab={activeTab}
        onNavigate={handleSidebarNavigation}
      />

      {/* Main Content Area */}
      <div className={`${isCollapsed ? 'ml-20' : 'ml-72'} transition-all duration-300 flex flex-col h-screen`}>
        
        {/* Top Header Bar */}
        <div className="h-16 bg-[#0a0a0a] border-b border-gray-800 flex items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-light text-white">Inbox</h1>
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <span>{filteredEmails.filter(e => !e.read).length} unread</span>
              <span>•</span>
              <span>{filteredEmails.length} total</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[#1a1a1a] border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <Command className="w-3 h-3 text-gray-500" />
                <span className="text-xs text-gray-500 ml-1">K</span>
              </div>
            </div>
            
            <button 
              onClick={refreshEmails}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="Refresh emails"
            >
              <RotateCcw className="w-5 h-5 text-gray-400" />
            </button>
            
            <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
              <Settings className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        <div className="flex-1 flex">
          {/* Left Sidebar - Email Folders */}
          <div className="w-64 bg-[#0a0a0a] border-r border-gray-800">
            {/* Compose Button */}
            <div className="p-4">
              <button 
                onClick={handleCompose}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                <span>Compose</span>
                <div className="flex items-center text-xs opacity-70">
                  <Command className="w-3 h-3" />
                  <span className="ml-1">N</span>
                </div>
              </button>
            </div>

            {/* Folders */}
            <div className="px-2">
              {emailFolders.map(folder => (
                <button
                  key={folder.id}
                  onClick={() => setActiveFolder(folder.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors text-sm mb-1 ${
                    activeFolder === folder.id
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  <span className="font-medium">{folder.label}</span>
                  {folder.count > 0 && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      activeFolder === folder.id ? 'bg-gray-700' : 'bg-gray-700/50'
                    }`}>
                      {folder.count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Filter Tabs - Only show if there are tagged emails in current folder */}
            {(currentFolderEmails.some(email => email.tags && email.tags.length > 0) || currentFolderEmails.some(email => email.important) || currentFolderEmails.some(email => !email.read)) && (
              <div className="px-2 mt-6">
                <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider px-3 mb-2">Filters</h3>
                <div className="space-y-1">
                  {filterTabs.filter(tab => tab.count > 0 || tab.id === 'all').map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveFilterTab(tab.id)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors text-sm ${
                        activeFilterTab === tab.id
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                      }`}
                    >
                      <span className="font-medium">{tab.label}</span>
                      {tab.count > 0 && (
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          activeFilterTab === tab.id ? 'bg-blue-500' : 'bg-gray-700/50'
                        }`}>
                          {tab.count}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Middle - Email List */}
          <div className="w-96 bg-[#0a0a0a] border-r border-gray-800 flex flex-col">
            {/* Email List Header */}
            <div className="h-12 border-b border-gray-800 flex items-center justify-between px-4">
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => selectedEmail && handleEmailAction('archive', selectedEmail.id)}
                  className="text-gray-400 hover:text-white disabled:opacity-50"
                  disabled={!selectedEmail}
                  title="Archive selected email"
                >
                  <Archive className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => selectedEmail && handleEmailAction('delete', selectedEmail.id)}
                  className="text-gray-400 hover:text-red-400 disabled:opacity-50"
                  disabled={!selectedEmail}
                  title="Delete selected email"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => selectedEmail && selectedEmail.tags && selectedEmail.tags.length > 0 && handleEmailAction('remove-tags', selectedEmail.id)}
                  className="text-gray-400 hover:text-orange-400 disabled:opacity-50"
                  disabled={!selectedEmail || !selectedEmail.tags || selectedEmail.tags.length === 0}
                  title="Remove all tags from selected email"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="relative">
                <button 
                  onClick={() => {
                    const sortOptions = ['date', 'sender', 'subject'] as const;
                    const currentIndex = sortOptions.indexOf(sortBy);
                    const nextIndex = (currentIndex + 1) % sortOptions.length;
                    setSortBy(sortOptions[nextIndex]);
                  }}
                  className="text-gray-400 hover:text-white flex items-center space-x-1 text-xs"
                >
                  <span className="capitalize">{sortBy}</span>
                  <ChevronDown className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Email List */}
            <div className="flex-1 overflow-y-auto">
              {filteredEmails.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Mail className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">No emails found</p>
                  </div>
                </div>
              ) : (
                filteredEmails.map(email => (
                  <div
                    key={email.id}
                    onClick={() => handleEmailClick(email)}
                    className={`group border-b border-gray-800/50 cursor-pointer transition-all hover:bg-gray-900/30 ${
                      selectedEmail?.id === email.id ? 'bg-gray-900/50 border-gray-700' : ''
                    } ${!email.read ? 'bg-gray-900/20' : ''}`}
                  >
                    <div className="px-4 py-3">
                      {/* Header */}
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center min-w-0 flex-1">
                          <span className={`text-sm font-medium truncate ${
                            !email.read ? 'text-white' : 'text-gray-300'
                          }`}>
                            {email.sender}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-2 flex-shrink-0">
                          {/* Tags */}
                          {email.tags && email.tags.length > 0 && (
                            <div className="flex items-center space-x-1">
                              {email.tags.slice(0, 1).map(tag => (
                                <span 
                                  key={tag}
                                  className={`inline-block px-2 py-0.5 text-xs rounded-full border ${getTagColor(tag)}`}
                                >
                                  {tag}
                                </span>
                              ))}
                              {email.tags.length > 1 && (
                                <span className="text-xs text-gray-500">+{email.tags.length - 1}</span>
                              )}
                            </div>
                          )}
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEmailAction('star', email.id);
                            }}
                            className={`p-1 rounded hover:bg-gray-700 transition-colors ${
                              email.starred ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'
                            }`}
                            title="Star email"
                          >
                            <Star className={`w-4 h-4 ${email.starred ? 'fill-current' : ''}`} />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEmailAction('important', email.id);
                            }}
                            className={`p-1 rounded transition-colors ${
                              email.important ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400'
                            }`}
                            title="Mark as important"
                          >
                            <div className={`w-2 h-2 rounded-full ${
                              email.important ? 'bg-yellow-400' : 'bg-gray-600'
                            }`} />
                          </button>
                          <span className="text-xs text-gray-500">
                            {getTimeDisplay(email.timestamp)}
                          </span>
                        </div>
                      </div>

                      {/* Subject */}
                      <div className="mb-1">
                        <h3 className={`text-sm font-medium truncate ${
                          !email.read ? 'text-white' : 'text-gray-300'
                        }`}>
                          {email.subject}
                        </h3>
                      </div>

                      {/* Preview */}
                      <p className="text-xs text-gray-500 line-clamp-2">
                        {email.preview}
                      </p>

                      {/* Attachments */}
                      {email.attachments && (
                        <div className="flex items-center space-x-1 mt-2">
                          <Paperclip className="w-3 h-3 text-gray-500" />
                          <span className="text-xs text-gray-500">
                            {email.attachments}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Right - Email Content */}
          <div className="flex-1 bg-[#0a0a0a] flex flex-col">
            {selectedEmail ? (
              <>
                {/* Email Header - Outlook Style */}
                <div className="border-b border-gray-800 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1 min-w-0">
                      {/* Subject */}
                      <h1 className="text-2xl font-normal text-white mb-4">
                        {selectedEmail.subject}
                      </h1>
                      
                      {/* Sender and Time - Outlook Style */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-white">{selectedEmail.sender}</span>
                            <span className="text-sm text-gray-500">&lt;{selectedEmail.senderEmail}&gt;</span>
                          </div>
                          <span className="text-sm text-gray-400">{selectedEmail.timestamp}</span>
                        </div>
                        <div className="text-sm text-gray-400">
                          <span>To: </span>
                          <span className="text-gray-300">me</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex items-center space-x-1 ml-4">
                      <button
                        onClick={() => handleEmailAction('star', selectedEmail.id)}
                        className={`p-2 rounded-lg transition-colors ${
                          selectedEmail.starred 
                            ? 'text-yellow-400 hover:bg-gray-800' 
                            : 'text-gray-400 hover:text-yellow-400 hover:bg-gray-800'
                        }`}
                        title="Star email"
                      >
                        <Star className={`w-4 h-4 ${selectedEmail.starred ? 'fill-current' : ''}`} />
                      </button>
                      <button
                        onClick={() => handleEmailAction('important', selectedEmail.id)}
                        className={`p-2 rounded-lg transition-colors ${
                          selectedEmail.important 
                            ? 'text-yellow-400 hover:bg-gray-800' 
                            : 'text-gray-400 hover:text-yellow-400 hover:bg-gray-800'
                        }`}
                        title="Mark as important"
                      >
                        <AlertCircle className={`w-4 h-4 ${selectedEmail.important ? 'fill-current' : ''}`} />
                      </button>
                      <button
                        onClick={() => handleEmailAction('tag', selectedEmail.id)}
                        className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-800 rounded-lg transition-colors"
                        title="Add tags"
                      >
                        <Tag className="w-4 h-4" />
                      </button>
                      {selectedEmail.folder === 'trash' ? (
                        <button
                          onClick={() => handleEmailAction('restore', selectedEmail.id)}
                          className="p-2 text-gray-400 hover:text-green-400 hover:bg-gray-800 rounded-lg transition-colors"
                          title="Restore email"
                        >
                          <RotateCcw className="w-4 h-4" />
                        </button>
                      ) : selectedEmail.folder === 'archive' ? (
                        <button
                          onClick={() => handleEmailAction('move-to-inbox', selectedEmail.id)}
                          className="p-2 text-gray-400 hover:text-green-400 hover:bg-gray-800 rounded-lg transition-colors"
                          title="Move to Inbox"
                        >
                          <RotateCcw className="w-4 h-4" />
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => handleEmailAction('archive', selectedEmail.id)}
                            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                            title="Archive email"
                          >
                            <Archive className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleEmailAction('delete', selectedEmail.id)}
                            className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
                            title="Delete email"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                      <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Email Body - Full Content */}
                <div className="flex-1 overflow-y-auto bg-[#0a0a0a]">
                  <div className="p-6 max-w-4xl">
                    {/* Show full email content */}
                    <div className="text-gray-200 leading-relaxed whitespace-pre-wrap text-[15px] font-normal">
                      {selectedEmail.content || selectedEmail.preview || 'No content available'}
                    </div>
                    
                    {/* Show if content is just preview */}
                    {!selectedEmail.content && selectedEmail.preview && (
                      <div className="mt-4 text-sm text-gray-500 italic">
                        (Preview only - full content may not be available)
                      </div>
                    )}
                  </div>
                </div>

                {/* Reply Section */}
                <div className="border-t border-gray-800 p-6">
                  <div className="flex space-x-3">
                    <button 
                      onClick={() => handleEmailAction('reply', selectedEmail.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors font-medium"
                    >
                      <Reply className="w-4 h-4" />
                      <span>Reply</span>
                      <div className="flex items-center text-xs opacity-70">
                        <Command className="w-3 h-3" />
                        <span className="ml-1">R</span>
                      </div>
                    </button>
                    <button 
                      onClick={() => handleEmailAction('forward', selectedEmail.id)}
                      className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors font-medium"
                    >
                      <Forward className="w-4 h-4" />
                      <span>Forward</span>
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <Mail className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">No email selected</h3>
                  <p className="text-gray-600 text-sm">Choose an email from the list to view it here</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <ChatBox
          onSendMessage={(message) => console.log('Email chat:', message)}
          onOpenFullChat={() => onNavigate && onNavigate('main')}
          sidebarCollapsed={isCollapsed}
        />
      </div>

      {/* Compose Modal */}
      {showCompose && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1a1a] border border-gray-700 rounded-lg w-[600px] max-h-[80vh] flex flex-col">
            {/* Compose Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h2 className="text-lg font-medium text-white">New Message</h2>
              <button
                onClick={handleCancelCompose}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Compose Form */}
            <div className="flex-1 p-4 space-y-4">
              {/* To Field */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">To</label>
                <input
                  type="email"
                  value={composeForm.to}
                  onChange={(e) => setComposeForm(prev => ({ ...prev, to: e.target.value }))}
                  placeholder="recipient@example.com"
                  className="w-full bg-[#0a0a0a] border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Subject Field */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Subject</label>
                <input
                  type="text"
                  value={composeForm.subject}
                  onChange={(e) => setComposeForm(prev => ({ ...prev, subject: e.target.value }))}
                  placeholder="Email subject"
                  className="w-full bg-[#0a0a0a] border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Content Field */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Message</label>
                <textarea
                  value={composeForm.content}
                  onChange={(e) => setComposeForm(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Write your message..."
                  rows={10}
                  className="w-full bg-[#0a0a0a] border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              {/* Attachments */}
              {composeForm.attachments.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Attachments</label>
                  <div className="space-y-2">
                    {composeForm.attachments.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-[#0a0a0a] border border-gray-600 rounded-lg px-3 py-2">
                        <div className="flex items-center space-x-2">
                          <Paperclip className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-300">{file.name}</span>
                          <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                        </div>
                        <button
                          onClick={() => removeAttachment(index)}
                          className="text-gray-400 hover:text-red-400 p-1"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Compose Footer */}
            <div className="flex items-center justify-between p-4 border-t border-gray-700">
              <div className="flex items-center space-x-2">
                <button 
                  onClick={handleFileAttachment}
                  className="text-gray-400 hover:text-white p-2"
                  title="Attach file"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleCancelCompose}
                  className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendEmail}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors font-medium"
                >
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                  <div className="flex items-center text-xs opacity-70">
                    <Command className="w-3 h-3" />
                    <span className="ml-1">⏎</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tag Modal */}
      {showTagModal && tagEmail && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1a1a1a] border border-gray-700 rounded-lg w-[400px] max-h-[80vh] flex flex-col">
            {/* Tag Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h2 className="text-lg font-medium text-white">Manage Tags</h2>
              <button
                onClick={closeTagModal}
                className="text-gray-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Tag Modal Content */}
            <div className="flex-1 p-4 space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-300 mb-2">Email: {tagEmail.subject}</h3>
              </div>

              {/* Current Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Current Tags</label>
                <div className="flex flex-wrap gap-2">
                  {tagEmail.tags && tagEmail.tags.length > 0 ? (
                    tagEmail.tags.map(tag => (
                      <div key={tag} className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs border ${getTagColor(tag)}`}>
                        <span>{tag}</span>
                        <button
                          onClick={() => handleRemoveTag(tag)}
                          className="hover:text-red-400 ml-1"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <span className="text-gray-500 text-sm">No tags added</span>
                  )}
                </div>
              </div>

              {/* Add New Tag */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Add Tag</label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    placeholder="Enter tag name"
                    className="flex-1 bg-[#0a0a0a] border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  />
                  <button
                    onClick={handleAddTag}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg flex items-center space-x-1 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add</span>
                  </button>
                </div>
              </div>

              {/* Common Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Quick Tags</label>
                <div className="flex flex-wrap gap-2">
                  {['work', 'personal', 'urgent', 'important', 'follow-up', 'project', 'meeting'].map(tag => (
                    <button
                      key={tag}
                      onClick={() => {
                        if (tagEmail && !tagEmail.tags?.includes(tag)) {
                          setNewTag(tag);
                          handleAddTag();
                        }
                      }}
                      disabled={tagEmail?.tags?.includes(tag)}
                      className={`px-2 py-1 text-xs rounded-full border transition-colors ${
                        tagEmail?.tags?.includes(tag) 
                          ? `${getTagColor(tag)} opacity-50 cursor-not-allowed`
                          : `${getTagColor(tag)} hover:opacity-80 cursor-pointer`
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Tag Modal Footer */}
            <div className="flex items-center justify-end p-4 border-t border-gray-700">
              <button
                onClick={closeTagModal}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailPage;