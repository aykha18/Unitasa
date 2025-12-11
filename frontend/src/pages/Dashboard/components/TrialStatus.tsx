import React from 'react';
import { Clock, Crown, Zap, ArrowRight, CheckCircle } from 'lucide-react';
import { Button } from '../../../components/ui';

interface User {
  subscription_tier: string;
  is_co_creator: boolean;
  trial_days_remaining: number;
  is_trial_active: boolean;
  trial_end_date: string | null;
}

interface TrialStatusProps {
  user: User;
}

const TrialStatus: React.FC<TrialStatusProps> = ({ user }) => {
  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  const handleUpgradeClick = () => {
    navigate('/upgrade');
  };

  const handleCoCreatorClick = () => {
    navigate('/co-creator');
  };

  // Co-Creator Status
  if (user.is_co_creator) {
    return (
      <div className="bg-gradient-to-br from-purple-500 to-blue-600 text-white rounded-xl shadow-lg p-6">
        <div className="flex items-center mb-4">
          <Crown className="w-6 h-6 mr-2" />
          <h3 className="text-lg font-bold">Co-Creator Status</h3>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-300" />
            <span className="text-sm">Lifetime Access</span>
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-300" />
            <span className="text-sm">Priority Support</span>
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-300" />
            <span className="text-sm">All Features Unlocked</span>
          </div>
        </div>

        <div className="mt-4 p-3 bg-white/20 rounded-lg">
          <p className="text-sm text-white/90">
            Thank you for being a founding member! You have unlimited access to all current and future features.
          </p>
        </div>
      </div>
    );
  }

  // Paid Subscription Status
  if (user.subscription_tier === 'pro' || user.subscription_tier === 'enterprise') {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-6">
        <div className="flex items-center mb-4">
          <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
          <h3 className="text-lg font-bold text-green-900">Active Subscription</h3>
        </div>
        
        <p className="text-green-700 text-sm mb-4">
          Your {user.subscription_tier} plan is active. Enjoy unlimited access to all features!
        </p>

        <Button
          onClick={() => navigate('/billing')}
          variant="outline"
          size="sm"
          className="w-full border-green-300 text-green-700 hover:bg-green-100"
        >
          Manage Billing
        </Button>
      </div>
    );
  }

  // Free Trial Status
  if (user.subscription_tier === 'free_trial' && user.is_trial_active) {
    const daysLeft = user.trial_days_remaining;
    const isUrgent = daysLeft <= 3;
    const isLastDay = daysLeft <= 1;

    return (
      <div className={`rounded-xl shadow-lg p-6 ${
        isLastDay 
          ? 'bg-gradient-to-br from-red-500 to-pink-600 text-white' 
          : isUrgent 
            ? 'bg-gradient-to-br from-orange-500 to-red-500 text-white'
            : 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
      }`}>
        <div className="flex items-center mb-4">
          <Clock className="w-6 h-6 mr-2" />
          <h3 className="text-lg font-bold">
            {isLastDay ? 'Trial Expires Today!' : `${daysLeft} Days Left`}
          </h3>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span>Trial Progress</span>
            <span>{15 - daysLeft}/15 days</span>
          </div>
          <div className="w-full bg-white/30 rounded-full h-2">
            <div 
              className="bg-white rounded-full h-2 transition-all duration-300"
              style={{ width: `${((15 - daysLeft) / 15) * 100}%` }}
            />
          </div>
        </div>

        <div className="space-y-3 mb-4">
          <p className="text-sm opacity-90">
            {isLastDay 
              ? "Don't lose access! Upgrade now to continue using all features."
              : isUrgent
                ? "Your trial is ending soon. Upgrade now to avoid losing access."
                : "You're making great progress! Upgrade anytime to unlock unlimited access."
            }
          </p>

          {/* Trial Benefits */}
          <div className="text-xs space-y-1 opacity-80">
            <div>✓ AI Content Generation</div>
            <div>✓ CRM Integration</div>
            <div>✓ Analytics Dashboard</div>
            <div>✓ Email Support</div>
          </div>
        </div>

        {/* Upgrade Buttons */}
        <div className="space-y-2">
          <Button
            onClick={handleUpgradeClick}
            variant="secondary"
            size="sm"
            className={`w-full font-semibold ${
              isLastDay || isUrgent 
                ? 'bg-white text-red-600 hover:bg-gray-100' 
                : 'bg-white text-blue-600 hover:bg-gray-100'
            }`}
          >
            <Zap className="w-4 h-4 mr-2" />
            Upgrade Now - Save 50%
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>

          <Button
            onClick={handleCoCreatorClick}
            variant="outline"
            size="sm"
            className="w-full border-white/50 text-white hover:bg-white/10"
          >
            <Crown className="w-4 h-4 mr-2" />
            Join Co-Creators (Lifetime)
          </Button>
        </div>

        {/* Urgency Message */}
        {isUrgent && (
          <div className="mt-3 p-2 bg-white/20 rounded text-xs text-center">
            {isLastDay 
              ? "⚠️ Trial expires at midnight tonight!"
              : "⏰ Limited time: 50% off first month!"
            }
          </div>
        )}
      </div>
    );
  }

  // Expired Trial
  if (user.subscription_tier === 'free_trial' && !user.is_trial_active) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-center mb-4">
          <Clock className="w-6 h-6 text-red-600 mr-2" />
          <h3 className="text-lg font-bold text-red-900">Trial Expired</h3>
        </div>
        
        <p className="text-red-700 text-sm mb-4">
          Your free trial has ended. Upgrade now to regain access to all features and continue your marketing automation journey.
        </p>

        <div className="space-y-2">
          <Button
            onClick={handleUpgradeClick}
            variant="primary"
            size="sm"
            className="w-full bg-red-600 hover:bg-red-700"
          >
            <Zap className="w-4 h-4 mr-2" />
            Reactivate Account
          </Button>

          <Button
            onClick={handleCoCreatorClick}
            variant="outline"
            size="sm"
            className="w-full border-red-300 text-red-700 hover:bg-red-50"
          >
            <Crown className="w-4 h-4 mr-2" />
            Lifetime Access
          </Button>
        </div>
      </div>
    );
  }

  // Free Plan
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
      <div className="flex items-center mb-4">
        <Zap className="w-6 h-6 text-gray-600 mr-2" />
        <h3 className="text-lg font-bold text-gray-900">Free Plan</h3>
      </div>
      
      <p className="text-gray-600 text-sm mb-4">
        You're on the free plan with limited features. Upgrade to unlock the full power of AI marketing automation.
      </p>

      <Button
        onClick={handleUpgradeClick}
        variant="primary"
        size="sm"
        className="w-full"
      >
        <Zap className="w-4 h-4 mr-2" />
        Upgrade Now
      </Button>
    </div>
  );
};

export default TrialStatus;