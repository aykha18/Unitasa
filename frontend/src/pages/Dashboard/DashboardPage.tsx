import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import WelcomeSection from './components/WelcomeSection';
import TrialStatus from './components/TrialStatus';
import QuickActions from './components/QuickActions';
import AnalyticsOverview from './components/AnalyticsOverview';
import OnboardingChecklist from './components/OnboardingChecklist';
import AIContentHub from './components/AIContentHub';
import DashboardHeader from './components/DashboardHeader';

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
const DashboardPage: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    analytics: {
      totalLeads: 0,
      campaignsActive: 0,
      engagementRate: 0,
      conversionRate: 0,
    },
    recentActivity: [],
    onboardingProgress: {
      profileComplete: false,
      crmConnected: false,
      firstCampaign: false,
      teamInvited: false,
    },
  });

  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      navigate('/signin');
      return;
    }

    if (user) {
      // Load dashboard data
      loadDashboardData();
    }
  }, [user, isAuthenticated, isLoading]);

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');

      // Load analytics data - fallback to mock data if endpoint doesn't exist
      try {
        const analyticsResponse = await fetch(`${getApiBaseUrl()}/api/v1/dashboard/analytics`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (analyticsResponse.ok) {
          const analytics = await analyticsResponse.json();
          setDashboardData(prev => ({
            ...prev,
            analytics,
          }));
        }
      } catch (error) {
        console.log('Analytics endpoint not available, using mock data');
        // Keep default mock data
      }

      // Load onboarding progress - fallback to mock data if endpoint doesn't exist
      try {
        const onboardingResponse = await fetch(`${getApiBaseUrl()}/api/v1/dashboard/onboarding`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (onboardingResponse.ok) {
          const onboarding = await onboardingResponse.json();
          setDashboardData(prev => ({
            ...prev,
            onboardingProgress: onboarding,
          }));
        }
      } catch (error) {
        console.log('Onboarding endpoint not available, using mock data');
        // Keep default mock data
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Will redirect to signin
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Dashboard Header */}
      <DashboardHeader user={user} />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Top Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Welcome Section */}
          <div className="lg:col-span-2">
            <WelcomeSection user={user} />
          </div>
          
          {/* Trial Status */}
          <div>
            <TrialStatus user={user} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <QuickActions user={user} />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Analytics & AI Hub */}
          <div className="lg:col-span-2 space-y-6">
            <AnalyticsOverview analytics={dashboardData.analytics} />
            <AIContentHub user={user} />
          </div>

          {/* Right Column - Onboarding */}
          <div>
            <OnboardingChecklist 
              progress={dashboardData.onboardingProgress}
              user={user}
              onProgressUpdate={loadDashboardData}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;