import React from 'react';
import { Sparkles, TrendingUp, Users, Zap } from 'lucide-react';

interface User {
  first_name: string;
  full_name: string;
  subscription_tier: string;
  is_co_creator: boolean;
}

interface WelcomeSectionProps {
  user: User;
}

const WelcomeSection: React.FC<WelcomeSectionProps> = ({ user }) => {
  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getWelcomeMessage = () => {
    if (user.is_co_creator) {
      return "Welcome back to your Co-Creator dashboard! You have lifetime access to all features.";
    }
    
    if (user.subscription_tier === 'free_trial') {
      return "Welcome to your free trial! Let's get you set up to see the power of AI marketing automation.";
    }
    
    return "Welcome back! Ready to supercharge your marketing with AI?";
  };

  const getQuickStats = () => {
    // These would come from real data in production
    return [
      {
        icon: TrendingUp,
        label: 'Campaigns Active',
        value: '3',
        change: '+2 this week',
        color: 'text-green-600'
      },
      {
        icon: Users,
        label: 'Leads Generated',
        value: '127',
        change: '+23 today',
        color: 'text-blue-600'
      },
      {
        icon: Zap,
        label: 'Content Created',
        value: '45',
        change: '+12 this week',
        color: 'text-purple-600'
      }
    ];
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {getTimeOfDay()}, {user.first_name || user.full_name}! 
            <Sparkles className="inline-block w-6 h-6 text-yellow-500 ml-2" />
          </h1>
          <p className="text-gray-600 max-w-2xl">
            {getWelcomeMessage()}
          </p>
        </div>
        
        {user.is_co_creator && (
          <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium">
            Co-Creator Access
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {getQuickStats().map((stat, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
              <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
            </div>
            <div className="text-sm text-gray-600 mb-1">{stat.label}</div>
            <div className={`text-xs ${stat.color} font-medium`}>{stat.change}</div>
          </div>
        ))}
      </div>

      {/* Action Hint */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Zap className="w-5 h-5 text-blue-600" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-800">
              <strong>Pro Tip:</strong> Start by creating your first AI-generated social media post. 
              It takes less than 2 minutes and shows immediate value!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeSection;