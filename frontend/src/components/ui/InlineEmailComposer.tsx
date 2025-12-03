import React, { useState, useRef } from 'react';
import { X, Paperclip, Send, Command } from 'lucide-react';
import { emailApi } from '../../utils/api';

interface InlineEmailComposerProps {
    initialTo?: string;
    initialSubject?: string;
    initialBody?: string;
    onSend?: () => void;
    onCancel?: () => void;
}

const InlineEmailComposer: React.FC<InlineEmailComposerProps> = ({
    initialTo = '',
    initialSubject = '',
    initialBody = '',
    onSend,
    onCancel
}) => {
    const [to, setTo] = useState(initialTo);
    const [subject, setSubject] = useState(initialSubject);
    const [content, setContent] = useState(initialBody);
    const [attachments, setAttachments] = useState<File[]>([]);
    const [isSending, setIsSending] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileAttachment = () => {
        fileInputRef.current?.click();
    };

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(event.target.files || []);
        setAttachments(prev => [...prev, ...files]);
    };

    const removeAttachment = (index: number) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
    };

    const handleSend = async () => {
        if (!to.trim() || !subject.trim() || !content.trim()) {
            alert('Please fill in all fields');
            return;
        }

        setIsSending(true);
        try {
            const response = await emailApi.sendEmail({
                to,
                subject,
                body: content
            });

            if (response.success) {
                if (onSend) onSend();
            } else {
                alert('Failed to send email: ' + (response.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error sending email:', error);
            alert('Failed to send email. Please try again.');
        } finally {
            setIsSending(false);
        }
    };

    return (
        <div className="glass-panel border border-primary-500/30 rounded-lg flex flex-col shadow-[0_0_30px_rgba(6,182,212,0.15)] mt-4 max-w-2xl">
            {/* Compose Header */}
            <div className="flex items-center justify-between p-4 border-b border-primary-500/60">
                <h2 className="text-lg font-medium text-white">New Message</h2>
                {onCancel && (
                    <button
                        onClick={onCancel}
                        className="text-gray-400 hover:text-white p-1"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            {/* Compose Form */}
            <div className="p-4 space-y-4">
                {/* To Field */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">To</label>
                    <input
                        type="email"
                        value={to}
                        onChange={(e) => setTo(e.target.value)}
                        placeholder="recipient@example.com"
                        className="w-full bg-black/50 border border-primary-500/60 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                </div>

                {/* Subject Field */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Subject</label>
                    <input
                        type="text"
                        value={subject}
                        onChange={(e) => setSubject(e.target.value)}
                        placeholder="Email subject"
                        className="w-full bg-black/50 border border-primary-500/60 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                </div>

                {/* Content Field */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Message</label>
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="Write your message..."
                        rows={8}
                        className="w-full bg-black/50 border border-primary-500/60 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                    />
                </div>

                {/* Attachments */}
                {attachments.length > 0 && (
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Attachments</label>
                        <div className="space-y-2">
                            {attachments.map((file, index) => (
                                <div key={index} className="flex items-center justify-between bg-black/50 border border-primary-500/60 rounded-lg px-3 py-2">
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
            <div className="flex items-center justify-between p-4 border-t border-primary-500/60">
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
                    {onCancel && (
                        <button
                            onClick={onCancel}
                            className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                    )}
                    <button
                        onClick={handleSend}
                        disabled={isSending}
                        className="btn-neon-flow text-white px-6 py-2 rounded-lg flex items-center space-x-2 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-4 h-4" />
                        <span>{isSending ? 'Sending...' : 'Send'}</span>
                        <div className="flex items-center text-xs opacity-70">
                            <Command className="w-3 h-3" />
                            <span className="ml-1">⏎</span>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default InlineEmailComposer;
