import React, { useState } from 'react';
import { X, Send, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

interface CreatePostModalProps {
    isOpen: boolean;
    onClose: () => void;
    connectedAccounts: Array<{
        id: number;
        platform: string;
        name: string;
        is_active: boolean;
    }>;
}

const CreatePostModal: React.FC<CreatePostModalProps> = ({ isOpen, onClose, connectedAccounts }) => {
    const [content, setContent] = useState('');
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

    if (!isOpen) return null;

    const handlePlatformToggle = (platform: string) => {
        setSelectedPlatforms(prev =>
            prev.includes(platform)
                ? prev.filter(p => p !== platform)
                : [...prev, platform]
        );
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim() || selectedPlatforms.length === 0) return;

        setIsSubmitting(true);
        setResult(null);

        try {
            const response = await fetch('/api/v1/social/posts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content,
                    platforms: selectedPlatforms,
                    // campaign_id: null // Optional
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setResult({ success: true, message: 'Post sent successfully!' });
                setTimeout(() => {
                    onClose();
                    setContent('');
                    setResult(null);
                }, 2000);
            } else {
                setResult({ success: false, message: data.detail || 'Failed to send post.' });
            }
        } catch (error) {
            setResult({ success: false, message: 'An error occurred while sending the post.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden animate-in fade-in zoom-in duration-200">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
                    <h3 className="text-lg font-semibold text-gray-900">Create New Post</h3>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Platform Selection */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Select Platforms
                        </label>
                        <div className="flex flex-wrap gap-2">
                            {connectedAccounts.filter(acc => acc.is_active).map(account => (
                                <button
                                    key={account.id}
                                    type="button"
                                    onClick={() => handlePlatformToggle(account.platform)}
                                    className={`flex items-center px-3 py-1.5 rounded-full text-sm font-medium transition-colors border ${selectedPlatforms.includes(account.platform)
                                            ? 'bg-blue-50 border-blue-200 text-blue-700'
                                            : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                                        }`}
                                >
                                    <span className="capitalize">{account.platform}</span>
                                </button>
                            ))}
                            {connectedAccounts.filter(acc => acc.is_active).length === 0 && (
                                <p className="text-sm text-gray-500 italic">No active accounts connected.</p>
                            )}
                        </div>
                    </div>

                    {/* Content Area */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Post Content
                        </label>
                        <div className="relative">
                            <textarea
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="What's on your mind?"
                                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                                maxLength={280}
                            />
                            <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                                {content.length}/280
                            </div>
                        </div>
                    </div>

                    {/* Status Message */}
                    {result && (
                        <div className={`p-3 rounded-lg flex items-center text-sm ${result.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                            }`}>
                            {result.success ? (
                                <CheckCircle2 className="w-4 h-4 mr-2 flex-shrink-0" />
                            ) : (
                                <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                            )}
                            {result.message}
                        </div>
                    )}

                    {/* Footer */}
                    <div className="flex justify-end pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg mr-2 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting || !content.trim() || selectedPlatforms.length === 0}
                            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Posting...
                                </>
                            ) : (
                                <>
                                    <Send className="w-4 h-4 mr-2" />
                                    Post Now
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreatePostModal;
