import React from 'react';
import {
  PenTool,
  Calendar,
  Link,
  BarChart3,
  Users,
  Zap,
  ArrowRight,
  Sparkles,
  Hash,
  Image,
  MessageCircle
} from 'lucide-react';
import { Button } from '../../../components/ui';

interface User {
  subscription_tier: string;
  is_co_creator: boolean;
  is_trial_active: boolean;
}

interface QuickActionsProps {
  user: User;
}

const QuickActions: React.FC<QuickActionsProps> = ({ user }) => {
  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  const handleActionClick = (action: string) => {
    // For now, navigate to placeholder pages
    // In production, these would go to actual feature pages
    navigate(`/${action}`);
  };

  const isFeatureAvailable = (feature: string) => {
    if (user.is_co_creator) return true;
    if (user.subscription_tier === 'pro' || user.subscription_tier === 'enterprise') return true;
    if (user.subscription_tier === 'free_trial' && user.is_trial_active) return true;
    return false;
  };

  const quickActions = [
    {
      id: 'generate-content',
      title: 'Generate AI Content',
      description: 'Create engaging social media posts in seconds',
      icon: PenTool,
      color: 'bg-blue-500 hover:bg-blue-600',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      available: true, // Always available for demo
      popular: true,
    },
    {
      id: 'schedule-posts',
      title: 'Schedule Posts',
      description: 'Plan and schedule your social media content',
      icon: Calendar,
      color: 'bg-green-500 hover:bg-green-600',
      textColor: 'text-green-600',
      bgColor: 'bg-green-50',
      available: isFeatureAvailable('scheduling'),
    },
    {
      id: 'connect-crm',
      title: 'Connect CRM',
      description: 'Integrate with HubSpot, Salesforce, and more',
      icon: Link,
      color: 'bg-purple-500 hover:bg-purple-600',
      textColor: 'text-purple-600',
      bgColor: 'bg-purple-50',
      available: isFeatureAvailable('crm'),
    },
    {
      id: 'view-analytics',
      title: 'View Analytics',
      description: 'Track performance and ROI of your campaigns',
      icon: BarChart3,
      color: 'bg-orange-500 hover:bg-orange-600',
      textColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
      available: isFeatureAvailable('analytics'),
    },
    {
      id: 'invite-team',
      title: 'Invite Team',
      description: 'Collaborate with your marketing team',
      icon: Users,
      color: 'bg-pink-500 hover:bg-pink-600',
      textColor: 'text-pink-600',
      bgColor: 'bg-pink-50',
      available: isFeatureAvailable('team'),
    },
    {
      id: 'ai-insights',
      title: 'AI Insights',
      description: 'Get personalized marketing recommendations',
      icon: Sparkles,
      color: 'bg-indigo-500 hover:bg-indigo-600',
      textColor: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      available: isFeatureAvailable('insights'),
      new: true,
    },
    {
      id: 'smart-hashtags',
      title: 'Smart Hashtags',
      description: 'Generate trending hashtags for your content',
      icon: Hash,
      color: 'bg-cyan-500 hover:bg-cyan-600',
      textColor: 'text-cyan-600',
      bgColor: 'bg-cyan-50',
      available: true, // Always available for demo
      new: true,
    },
    {
      id: 'image-suggestions',
      title: 'Image Suggestions',
      description: 'Find perfect images for your social posts',
      icon: Image,
      color: 'bg-emerald-500 hover:bg-emerald-600',
      textColor: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      available: true, // Always available for demo
      new: true,
    },
    {
      id: 'chat-assistant',
      title: 'AI Content Assistant',
      description: 'Chat with AI for content strategy advice',
      icon: MessageCircle,
      color: 'bg-violet-500 hover:bg-violet-600',
      textColor: 'text-violet-600',
      bgColor: 'bg-violet-50',
      available: true, // Always available for demo
      new: true,
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>
          <p className="text-gray-600 text-sm">Get started with these powerful features</p>
        </div>
        <Zap className="w-6 h-6 text-yellow-500" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {quickActions.map((action) => (
          <div
            key={action.id}
            className={`relative p-4 rounded-lg border-2 transition-all duration-200 ${
              action.available
                ? 'border-gray-200 hover:border-gray-300 cursor-pointer hover:shadow-md'
                : 'border-gray-100 opacity-60 cursor-not-allowed'
            }`}
            onClick={() => action.available && handleActionClick(action.id)}
          >
            {/* Badges */}
            <div className="absolute top-2 right-2 flex space-x-1">
              {action.popular && (
                <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">
                  Popular
                </span>
              )}
              {action.new && (
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                  New
                </span>
              )}
            </div>

            {/* Icon */}
            <div className={`w-12 h-12 ${action.bgColor} rounded-lg flex items-center justify-center mb-3`}>
              <action.icon className={`w-6 h-6 ${action.textColor}`} />
            </div>

            {/* Content */}
            <h3 className={`font-semibold mb-2 ${action.available ? 'text-gray-900' : 'text-gray-500'}`}>
              {action.title}
            </h3>
            <p className={`text-sm mb-4 ${action.available ? 'text-gray-600' : 'text-gray-400'}`}>
              {action.description}
            </p>

            {/* Action Button */}
            {action.available ? (
              <div className="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900">
                Get Started
                <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Upgrade to unlock</span>
                <Button
                  onClick={() => navigate('/upgrade')}
                  variant="outline"
                  size="sm"
                  className="text-xs px-2 py-1 h-auto"
                >
                  Upgrade
                </Button>
              </div>
            )}

            {/* Locked Overlay */}
            {!action.available && (
              <div className="absolute inset-0 bg-gray-50/50 rounded-lg flex items-center justify-center">
                <div className="bg-white rounded-full p-2 shadow-sm">
                  <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* CTA for Free Users */}
      {!user.is_co_creator && user.subscription_tier === 'free' && (
        <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Unlock All Features</h3>
              <p className="text-sm text-gray-600">
                Start your free trial to access all quick actions and advanced features.
              </p>
            </div>
            <Button
              onClick={() => navigate('/signup')}
              variant="primary"
              size="sm"
            >
              Start Free Trial
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickActions;