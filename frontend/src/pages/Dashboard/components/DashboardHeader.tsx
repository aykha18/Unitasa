import React from 'react';
import { Bell, Settings, User, LogOut } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import { Button } from '../../../components/ui';

interface User {
  first_name?: string;
  last_name?: string;
  email?: string;
  subscription_tier: string;
  is_co_creator: boolean;
  is_trial_active: boolean;
}

interface DashboardHeaderProps {
  user: User;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ user }) => {
  const { logout } = useAuth();

  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  const handleLogout = () => {
    logout();
  };

  const getUserDisplayName = () => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user.email || 'User';
  };

  const getSubscriptionBadge = () => {
    if (user.is_co_creator) {
      return { text: 'Co-Creator', color: 'bg-purple-100 text-purple-800' };
    }
    if (user.subscription_tier === 'enterprise') {
      return { text: 'Enterprise', color: 'bg-blue-100 text-blue-800' };
    }
    if (user.subscription_tier === 'pro') {
      return { text: 'Pro', color: 'bg-green-100 text-green-800' };
    }
    if (user.subscription_tier === 'free_trial' && user.is_trial_active) {
      return { text: 'Trial', color: 'bg-orange-100 text-orange-800' };
    }
    return { text: 'Free', color: 'bg-gray-100 text-gray-800' };
  };

  const subscriptionBadge = getSubscriptionBadge();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <div className="bg-primary-600 p-2 rounded-lg mr-3">
              <div className="w-6 h-6 bg-white rounded flex items-center justify-center text-primary-600 text-sm font-bold">
                U
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome back, {getUserDisplayName()}</p>
            </div>
          </div>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {/* Subscription Badge */}
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${subscriptionBadge.color}`}>
              {subscriptionBadge.text}
            </div>

            {/* Notifications */}
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors relative">
              <Bell className="w-5 h-5" />
              {/* Notification dot */}
              <div className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></div>
            </button>

            {/* Settings */}
            <button
              onClick={() => navigate('/settings')}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <Settings className="w-5 h-5" />
            </button>

            {/* User Menu */}
            <div className="relative">
              <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user.first_name?.[0] || user.email?.[0] || 'U'}
                </div>
                <div className="hidden md:block text-left">
                  <div className="text-sm font-medium text-gray-900">{getUserDisplayName()}</div>
                  <div className="text-xs text-gray-500">{subscriptionBadge.text} Plan</div>
                </div>
              </button>
            </div>

            {/* Logout Button */}
            <Button
              onClick={handleLogout}
              variant="outline"
              size="sm"
              className="text-red-600 border-red-200 hover:bg-red-50"
            >
              <LogOut className="w-4 h-4 mr-2" />
              <span className="hidden md:inline">Logout</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;