import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, MessageCircle } from 'lucide-react';
import { Button } from '../components/ui';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

const ChatAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! I'm your AI Content Assistant. I can help you with content strategy, social media ideas, hashtag suggestions, and more. What would you like to know?",
      role: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const mockAIResponse = (userMessage: string): string => {
    const responses = [
      "That's a great idea! For optimal engagement, consider posting this during peak hours for your target audience.",
      "I recommend using a mix of popular and niche hashtags. Popular ones get visibility, while niche ones attract the right audience.",
      "Based on current trends, content about [topic] is performing well. You might want to create a series around this theme.",
      "Try using storytelling in your captions - it increases engagement by 20-30% according to recent studies.",
      "Consider collaborating with micro-influencers in your niche. They often have higher engagement rates than larger accounts.",
      "A/B testing different post times and caption styles can help you understand what works best for your audience.",
      "User-generated content is gold! Encourage your followers to share their experiences with your brand.",
      "Video content is king right now. Short, authentic videos perform much better than polished ones.",
      "Don't forget about the power of questions in your captions - they boost comments and interaction.",
      "Consistency is key, but quality over quantity. Focus on creating valuable content that serves your audience.",
    ];

    // Simple keyword matching for more relevant responses
    if (userMessage.toLowerCase().includes('hashtag')) {
      return "For hashtags, aim for a mix of 5-10 per post. Include 2-3 popular hashtags (1M+ posts) and the rest niche-specific. Tools like Instagram's search can help you find trending ones in your niche.";
    }
    if (userMessage.toLowerCase().includes('time') || userMessage.toLowerCase().includes('schedule')) {
      return "Best posting times vary by platform and audience. Generally: Instagram & TikTok work well 7-9 PM weekdays, Facebook 1-3 PM weekdays, Twitter anytime but especially 8-10 AM and 5-7 PM. Test and analyze what works for your specific audience!";
    }
    if (userMessage.toLowerCase().includes('engagement')) {
      return "To boost engagement: Ask questions, respond to comments within 24 hours, use relevant emojis, collaborate with others, and post consistently. Stories and Reels often get more interaction than feed posts.";
    }

    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response delay
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: mockAIResponse(userMessage.content),
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1000 + Math.random() * 2000); // 1-3 second delay
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-full">
              <MessageCircle className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Content Assistant</h1>
          <p className="text-gray-600">Get expert advice on content strategy, social media, and marketing</p>
        </div>

        {/* Chat Interface */}
        <div className="h-[600px] flex flex-col border rounded-lg bg-white shadow-sm">
          <div className="border-b p-4">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <Sparkles className="w-5 h-5 text-blue-500" />
              Content Strategy Chat
            </h2>
          </div>

          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 p-4 overflow-y-auto" ref={scrollAreaRef}>
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="bg-blue-100 p-2 rounded-full">
                        <Bot className="w-4 h-4 text-blue-600" />
                      </div>
                    )}

                    <div
                      className={`max-w-[70%] rounded-lg px-4 py-2 ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>

                    {message.role === 'user' && (
                      <div className="bg-blue-500 p-2 rounded-full">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <Bot className="w-4 h-4 text-blue-600" />
                    </div>
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me about content strategy, hashtags, posting times..."
                  className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!input.trim() || isLoading}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Press Enter to send • AI responses are generated for demonstration
              </p>
            </div>
          </div>
        </div>

        {/* Quick Suggestions */}
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Quick Questions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "What's the best time to post on Instagram?",
              "How do I create engaging captions?",
              "What hashtags should I use for my niche?",
              "How can I improve my engagement rate?",
            ].map((question, index) => (
              <Button
                key={index}
                variant="outline"
                className="text-left justify-start h-auto p-3"
                onClick={() => setInput(question)}
                disabled={isLoading}
              >
                {question}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatAssistantPage;