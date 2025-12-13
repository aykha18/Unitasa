import React, { useState } from 'react';
import { Sparkles, PenTool, Image, MessageSquare, Zap, Loader2, Calendar } from 'lucide-react';
import { Button } from '../../../components/ui';

interface User {
  subscription_tier: string;
  is_co_creator: boolean;
  is_trial_active: boolean;
}

interface AIContentHubProps {
  user: User;
}

const AIContentHub: React.FC<AIContentHubProps> = ({ user }) => {
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});
  const [generatedContent, setGeneratedContent] = useState<{[key: string]: any[]}>({});

  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  // API Configuration - Use environment variable or detect environment
  const getApiBaseUrl = () => {
    // If REACT_APP_API_URL is set and it's not the placeholder, use it
    if (process.env.REACT_APP_API_URL &&
        !process.env.REACT_APP_API_URL.includes('your-backend-service.railway.app')) {
      return process.env.REACT_APP_API_URL;
    }

    // If we're in production (Railway), use relative URLs for same-service deployment
    if (process.env.NODE_ENV === 'production' || window.location.hostname !== 'localhost') {
      // Backend and frontend are on the same Railway service
      return ''; // Relative URLs will use the same domain
    }

    // Development default
    return 'http://localhost:8001';
  };

  const handleGenerateContent = async (featureKey: string, platform: string) => {
    setLoading(prev => ({ ...prev, [`${featureKey}_${platform}`]: true }));

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/content/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          feature_key: featureKey,
          platform: platform,
          content_type: 'educational'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedContent(prev => ({
          ...prev,
          [`${featureKey}_${platform}`]: data.content || []
        }));
        alert(`Generated ${data.content?.length || 0} content pieces for ${platform}!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to generate content'}`);
      }
    } catch (error) {
      console.error('Content generation error:', error);
      alert('Failed to generate content. Please try again.');
    } finally {
      setLoading(prev => ({ ...prev, [`${featureKey}_${platform}`]: false }));
    }
  };

  const aiFeatures = [
    {
      title: 'AI Content Generator',
      description: 'Generate engaging social media posts with AI',
      icon: PenTool,
      action: 'generate-content',
      color: 'bg-blue-500 hover:bg-blue-600',
      available: true,
    },
    {
      title: 'Schedule Posts',
      description: 'Schedule your content for optimal posting times',
      icon: Calendar,
      action: 'schedule-posts',
      color: 'bg-indigo-500 hover:bg-indigo-600',
      available: true,
    },
    {
      title: 'Smart Hashtags',
      description: 'Get trending and relevant hashtags for your posts',
      icon: Sparkles,
      action: 'hashtags',
      color: 'bg-purple-500 hover:bg-purple-600',
      available: user.is_co_creator || user.subscription_tier !== 'free',
    },
    {
      title: 'Image Suggestions',
      description: 'AI-powered image recommendations for your content',
      icon: Image,
      action: 'images',
      color: 'bg-green-500 hover:bg-green-600',
      available: user.is_co_creator || user.subscription_tier !== 'free',
    },
    {
      title: 'Chat Assistant',
      description: 'Get help with content strategy and marketing advice',
      icon: MessageSquare,
      action: 'chat',
      color: 'bg-orange-500 hover:bg-orange-600',
      available: user.is_co_creator || user.subscription_tier !== 'free',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">AI Content Hub</h2>
          <p className="text-gray-600 text-sm">Supercharge your content creation with AI</p>
        </div>
        <div className="flex items-center space-x-2">
          <Sparkles className="w-6 h-6 text-purple-500" />
          <span className="text-sm font-medium text-purple-600">AI Powered</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {aiFeatures.map((feature, index) => (
          <div
            key={index}
            className={`relative p-4 rounded-lg border-2 transition-all duration-200 ${
              feature.available
                ? 'border-gray-200 hover:border-gray-300 cursor-pointer hover:shadow-md'
                : 'border-gray-100 opacity-60 cursor-not-allowed'
            }`}
            onClick={() => feature.available && navigate(`/${feature.action}`)}
          >
            <div className={`w-10 h-10 ${feature.color} rounded-lg flex items-center justify-center mb-3`}>
              <feature.icon className="w-5 h-5 text-white" />
            </div>

            <h3 className={`font-semibold mb-2 ${feature.available ? 'text-gray-900' : 'text-gray-500'}`}>
              {feature.title}
            </h3>
            <p className={`text-sm mb-4 ${feature.available ? 'text-gray-600' : 'text-gray-400'}`}>
              {feature.description}
            </p>

            {feature.available ? (
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => {
                  if (feature.action === 'generate-content') {
                    handleGenerateContent('automated_social_posting', 'twitter');
                  } else {
                    navigate(`/${feature.action}`);
                  }
                }}
                disabled={loading[`automated_social_posting_twitter`]}
              >
                {loading[`automated_social_posting_twitter`] ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Zap className="w-4 h-4 mr-2" />
                )}
                {loading[`automated_social_posting_twitter`] ? 'Generating...' : 'Try Now'}
              </Button>
            ) : (
              <div className="text-center">
                <span className="text-sm text-gray-400">Upgrade to unlock</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Upgrade CTA */}
      {!user.is_co_creator && user.subscription_tier === 'free' && (
        <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Unlock AI Features</h3>
              <p className="text-sm text-gray-600">
                Get access to all AI-powered content tools and supercharge your marketing.
              </p>
            </div>
            <Button
              onClick={() => navigate('/upgrade')}
              variant="primary"
              size="sm"
            >
              Upgrade Now
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIContentHub;