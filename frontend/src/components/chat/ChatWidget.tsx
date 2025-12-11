import React, { useState, useEffect, useRef } from 'react';
import { ChatSession, ChatMessage, VoiceRecognitionState } from '../../types';
import ChatMessageList from './ChatMessageList';
import ChatInput from './ChatInput';
import VoiceInput from './VoiceInput';
import ChatHeader from './ChatHeader';

interface ChatWidgetProps {
  isOpen: boolean;
  onToggle: () => void;
  onMinimize: () => void;
  isMinimized: boolean;
  unreadCount: number;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({
  isOpen,
  onToggle,
  onMinimize,
  isMinimized,
  unreadCount
}) => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [voiceState, setVoiceState] = useState<VoiceRecognitionState>({
    isListening: false,
    isSupported: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
    transcript: '',
    confidence: 0
  });
  
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat session and WebSocket connection
  useEffect(() => {
    if (isOpen && !session) {
      initializeChat();
    }
  }, [isOpen]);

  // WebSocket connection management
  useEffect(() => {
    if (session && !wsRef.current) {
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [session]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [session?.messages]);

  const initializeChat = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/chat/initialize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context: {
            currentPage: window.location.pathname,
            userProgress: {
              assessmentCompleted: localStorage.getItem('assessmentCompleted') === 'true',
              crmSelected: localStorage.getItem('selectedCRM'),
              readinessScore: localStorage.getItem('readinessScore') ? 
                parseInt(localStorage.getItem('readinessScore')!) : undefined
            }
          }
        })
      });

      if (response.ok) {
        const chatSession = await response.json();
        // Validate that the response is a valid ChatSession object
        if (chatSession && typeof chatSession === 'object' && !Array.isArray(chatSession) && 'id' in chatSession && 'messages' in chatSession) {
          setSession(chatSession);
        } else {
          console.error('Invalid chat session response:', chatSession);
          // Don't set session, will show error message
        }
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const connectWebSocket = () => {
    if (!session) return;
    
    // Skip WebSocket connection if disabled
    if (process.env.REACT_APP_DISABLE_WEBSOCKET === 'true') {
      console.log('Chat WebSocket disabled via environment variable');
      return;
    }

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/chat/ws/${session.id}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setIsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Only add actual chat messages, not system messages
      if (data.sender && (data.sender === 'user' || data.sender === 'agent')) {
        const message: ChatMessage = data;
        setSession(prev => prev ? {
          ...prev,
          messages: [...prev.messages, message]
        } : null);
      } else if (data.type === 'connected') {
        console.log('WebSocket connected:', data.message);
      } else if (data.type === 'pong') {
        console.log('WebSocket pong received');
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.message);
      }
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (session && isOpen) {
          connectWebSocket();
        }
      }, 3000);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  const sendMessage = async (content: string, type: 'text' | 'voice' = 'text') => {
    if (!session || !content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: content.trim(),
      sender: 'user',
      timestamp: new Date(),
      type
    };

    // Add user message immediately
    setSession(prev => prev ? {
      ...prev,
      messages: [...prev.messages, userMessage]
    } : null);

    // Always try HTTP first for reliability, then WebSocket as enhancement
    try {
      const response = await fetch(`/api/v1/chat/${session.id}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content.trim(),
          type: type
        })
      });

      if (response.ok) {
        const aiMessage = await response.json();
        // Validate that the response is a valid ChatMessage object
        if (aiMessage && typeof aiMessage === 'object' && !Array.isArray(aiMessage) && 'id' in aiMessage && 'content' in aiMessage && 'sender' in aiMessage) {
          // Add AI response to chat
          setSession(prev => prev ? {
            ...prev,
            messages: [...prev.messages, aiMessage]
          } : null);
        } else {
          console.error('Invalid AI message response:', aiMessage);
          // Add error message
          const errorMessage: ChatMessage = {
            id: Date.now().toString() + '_error',
            content: 'Sorry, I encountered an error. Please try again.',
            sender: 'agent',
            timestamp: new Date(),
            type: 'text'
          };
          setSession(prev => prev ? {
            ...prev,
            messages: [...prev.messages, errorMessage]
          } : null);
        }
      } else {
        console.error('Failed to get response:', response.status);
        // Add error message
        const errorMessage: ChatMessage = {
          id: Date.now().toString() + '_error',
          content: 'Sorry, I encountered an error. Please try again.',
          sender: 'agent',
          timestamp: new Date(),
          type: 'text'
        };
        setSession(prev => prev ? {
          ...prev,
          messages: [...prev.messages, errorMessage]
        } : null);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message
      const errorMessage: ChatMessage = {
        id: Date.now().toString() + '_error',
        content: 'Connection error. Please check your internet connection and try again.',
        sender: 'agent',
        timestamp: new Date(),
        type: 'text'
      };
      setSession(prev => prev ? {
        ...prev,
        messages: [...prev.messages, errorMessage]
      } : null);
    }
  };

  const handleVoiceInput = (transcript: string) => {
    if (transcript.trim()) {
      sendMessage(transcript, 'voice');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={onToggle}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 hover:scale-105 relative"
          aria-label="Open chat"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          {unreadCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ${
      isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'
    }`}>
      {/* Modern chat container with gradient background */}
      <div className="h-full bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl shadow-2xl border border-blue-200 overflow-hidden backdrop-blur-sm">
        <ChatHeader
          isConnected={isConnected}
          onMinimize={onMinimize}
          onClose={onToggle}
          isMinimized={isMinimized}
        />
        
        {!isMinimized && (
          <div className="flex flex-col h-[536px]">
            {/* Messages area with modern styling */}
            <div className="flex-1 overflow-y-auto bg-white/70 backdrop-blur-sm">
              {isLoading ? (
                <div className="flex-1 flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-blue-600 font-medium">Connecting to Unitasa Assistant...</p>
                  </div>
                </div>
              ) : session ? (
                <>
                  <ChatMessageList 
                    messages={session.messages} 
                    isLoading={false}
                  />
                  <div ref={messagesEndRef} />
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-gray-500 h-full">
                  <div className="text-center p-6">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="text-gray-600 font-medium">Failed to initialize chat</p>
                    <p className="text-sm text-gray-500 mt-1">Please refresh and try again</p>
                  </div>
                </div>
              )}
            </div>
            
            {/* Input area with modern styling - always show */}
            <div className="bg-white/90 backdrop-blur-sm border-t border-blue-200 p-4">
              {voiceState.isSupported && (
                <div className="mb-3">
                  <VoiceInput
                    voiceState={voiceState}
                    onVoiceStateChange={setVoiceState}
                    onTranscript={handleVoiceInput}
                  />
                </div>
              )}
              
              {/* Always show input, just disable if no session */}
              <div className="relative">
                <ChatInput
                  onSendMessage={sendMessage}
                  disabled={!session}
                  placeholder={
                    !session 
                      ? "Initializing chat..." 
                      : isConnected 
                        ? "Ask about CRM integrations..." 
                        : "Type your message..."
                  }
                />
                
                {/* Connection status indicator */}
                <div className="flex items-center justify-between mt-2 text-xs">
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      isConnected ? 'bg-green-400' : 'bg-yellow-400'
                    }`}></div>
                    <span className="text-gray-500">
                      {isConnected ? 'Connected' : 'Connecting...'}
                    </span>
                  </div>
                  <span className="text-gray-400">
                    Powered by Unitasa AI
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatWidget;
