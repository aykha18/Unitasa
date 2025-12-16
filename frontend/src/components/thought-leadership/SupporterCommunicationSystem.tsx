import React, { useState } from 'react';

interface SupporterMessage {
  id: string;
  title: string;
  content: string;
  date: Date;
  type: 'update' | 'milestone' | 'feedback_request' | 'announcement';
  priority: 'low' | 'medium' | 'high';
  readStatus: boolean;
  attachments?: {
    name: string;
    url: string;
    type: 'document' | 'image' | 'video';
  }[];
}

interface FeedbackRequest {
  id: string;
  title: string;
  description: string;
  type: 'feature_vote' | 'survey' | 'beta_test' | 'design_review';
  deadline?: Date;
  responses: number;
  maxResponses?: number;
  status: 'open' | 'closed' | 'draft';
}

interface SupporterCommunicationSystemProps {
  messages: SupporterMessage[];
  feedbackRequests: FeedbackRequest[];
  isCoCreator: boolean;
  className?: string;
  onJoinProgram?: () => void;
}

const SupporterCommunicationSystem: React.FC<SupporterCommunicationSystemProps> = ({
  messages,
  feedbackRequests,
  isCoCreator,
  className = '',
  onJoinProgram
}) => {
  const [activeTab, setActiveTab] = useState<'messages' | 'feedback' | 'community'>('messages');
  const [selectedMessage, setSelectedMessage] = useState<SupporterMessage | null>(null);
  const [filter, setFilter] = useState<'all' | 'unread' | 'important'>('all');

  const filteredMessages = messages.filter(message => {
    if (filter === 'unread') return !message.readStatus;
    if (filter === 'important') return message.priority === 'high';
    return true;
  });

  const getMessageTypeIcon = (type: SupporterMessage['type']) => {
    switch (type) {
      case 'update': return '📢';
      case 'milestone': return '🎯';
      case 'feedback_request': return '💭';
      case 'announcement': return '📣';
      default: return '📝';
    }
  };

  const getPriorityColor = (priority: SupporterMessage['priority']) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getFeedbackTypeColor = (type: FeedbackRequest['type']) => {
    switch (type) {
      case 'feature_vote': return 'text-blue-600 bg-blue-100';
      case 'survey': return 'text-green-600 bg-green-100';
      case 'beta_test': return 'text-purple-600 bg-purple-100';
      case 'design_review': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!isCoCreator) {
    return (
      <div className={`bg-white rounded-xl shadow-lg border ${className}`}>
        <div className="p-8 text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Co-Creator Exclusive</h3>
          <p className="text-gray-600 mb-6">
            This communication system is exclusively available to our founding co-creators.
          </p>
          <button
            onClick={() => {
              if (onJoinProgram) {
                onJoinProgram();
              } else {
                // Fallback: dispatch event
                window.dispatchEvent(new CustomEvent('openLeadCapture'));
              }
            }}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Join Co-Creator Program
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg border ${className}`}>
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">Co-Creator Hub</h3>
            <p className="text-gray-600">Exclusive updates and collaboration space</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
              👑 Co-Creator
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { key: 'messages', label: 'Updates', icon: '📬', count: messages.filter(m => !m.readStatus).length },
            { key: 'feedback', label: 'Feedback', icon: '💭', count: feedbackRequests.filter(f => f.status === 'open').length },
            { key: 'community', label: 'Community', icon: '👥', count: 0 }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors relative ${
                activeTab === tab.key
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.count > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {tab.count > 9 ? '9+' : tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {activeTab === 'messages' && (
          <div className="space-y-6">
            {/* Message Filters */}
            <div className="flex space-x-2">
              {[
                { key: 'all', label: 'All Messages' },
                { key: 'unread', label: 'Unread' },
                { key: 'important', label: 'Important' }
              ].map((filterOption) => (
                <button
                  key={filterOption.key}
                  onClick={() => setFilter(filterOption.key as any)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === filterOption.key
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {filterOption.label}
                </button>
              ))}
            </div>

            {/* Messages List */}
            <div className="space-y-3">
              {filteredMessages.map((message) => (
                <div
                  key={message.id}
                  onClick={() => setSelectedMessage(message)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                    !message.readStatus ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'
                  } ${selectedMessage?.id === message.id ? 'ring-2 ring-blue-500' : ''}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{getMessageTypeIcon(message.type)}</span>
                      <div>
                        <h4 className={`font-semibold ${!message.readStatus ? 'text-blue-900' : 'text-gray-900'}`}>
                          {message.title}
                        </h4>
                        <p className="text-sm text-gray-600">
                          {message.date.toLocaleDateString()} • {message.type.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(message.priority)}`}>
                        {message.priority}
                      </span>
                      {!message.readStatus && (
                        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      )}
                    </div>
                  </div>
                  
                  {selectedMessage?.id === message.id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="prose prose-sm max-w-none">
                        <p className="text-gray-700">{message.content}</p>
                      </div>
                      
                      {message.attachments && message.attachments.length > 0 && (
                        <div className="mt-4">
                          <h5 className="font-medium text-gray-900 mb-2">Attachments:</h5>
                          <div className="space-y-2">
                            {message.attachments.map((attachment, index) => (
                              <a
                                key={index}
                                href={attachment.url}
                                className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 text-sm"
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <span>📎</span>
                                <span>{attachment.name}</span>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'feedback' && (
          <div className="space-y-4">
            {feedbackRequests.map((request) => (
              <div key={request.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-semibold text-gray-900">{request.title}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFeedbackTypeColor(request.type)}`}>
                        {request.type.replace('_', ' ')}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        request.status === 'open' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {request.status}
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{request.description}</p>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{request.responses} responses</span>
                      {request.maxResponses && (
                        <span>• Target: {request.maxResponses}</span>
                      )}
                      {request.deadline && (
                        <span>• Deadline: {request.deadline.toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  
                  {request.status === 'open' && (
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                      Participate
                    </button>
                  )}
                </div>

                {request.maxResponses && (
                  <div className="mt-3">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Response Progress</span>
                      <span>{Math.round((request.responses / request.maxResponses) * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min((request.responses / request.maxResponses) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'community' && (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">👥</span>
            </div>
            <h4 className="text-lg font-semibold text-gray-900 mb-2">Community Features Coming Soon</h4>
            <p className="text-gray-600 mb-4">
              Connect with other co-creators, share insights, and collaborate on feature ideas.
            </p>
            <div className="bg-purple-50 rounded-lg p-4 text-left">
              <h5 className="font-medium text-purple-900 mb-2">Planned Features:</h5>
              <ul className="text-sm text-purple-800 space-y-1">
                <li>• Direct messaging with other co-creators</li>
                <li>• Feature discussion forums</li>
                <li>• Collaborative roadmap planning</li>
                <li>• Success story sharing</li>
                <li>• Monthly virtual meetups</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SupporterCommunicationSystem;
