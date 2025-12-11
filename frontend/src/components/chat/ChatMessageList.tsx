import React from 'react';
import { ChatMessage } from '../../types';
import ChatMessageBubble from './ChatMessageBubble';

interface ChatMessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

const ChatMessageList: React.FC<ChatMessageListProps> = ({ messages, isLoading }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {(!messages || messages.length === 0) && !isLoading && (
        <div className="text-center text-gray-500 py-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="font-semibold text-gray-700 mb-2">Welcome to Unitasa!</h3>
          <p className="text-sm text-gray-500 mb-4">
            I'm here to help you with CRM integrations and marketing automation questions.
          </p>
          <div className="space-y-2 text-sm">
            <div className="bg-gray-50 rounded-lg p-3 text-left">
              <p className="font-medium text-gray-700 mb-1">Try asking:</p>
              <ul className="text-gray-600 space-y-1">
                <li>• "How does Unitasa integrate with Salesforce?"</li>
                <li>• "What CRM features do you support?"</li>
                <li>• "Help me choose the right integration"</li>
                <li>• "Tell me about the co-creator program"</li>
              </ul>
            </div>
          </div>
        </div>
      )}
      
      {messages && messages.map((message) => (
        <ChatMessageBubble key={message.id} message={message} />
      ))}
      
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 rounded-lg p-3 max-w-xs">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessageList;
