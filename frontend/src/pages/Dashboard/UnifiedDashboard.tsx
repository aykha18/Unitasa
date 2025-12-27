import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import SidebarNavigation from './components/SidebarNavigation';
import DashboardHeader from './components/DashboardHeader';

// Import business dashboard components
import WelcomeSection from './components/WelcomeSection';
import TrialStatus from './components/TrialStatus';
import QuickActions from './components/QuickActions';
import AnalyticsOverview from './components/AnalyticsOverview';
import OnboardingChecklist from './components/OnboardingChecklist';
import AIContentHub from './components/AIContentHub';

// Import social dashboard (lazy load for performance)
const SocialDashboard = React.lazy(() => import('../SocialDashboard'));

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

const UnifiedDashboard: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [activeModule, setActiveModule] = useState('business');
  const [businessData, setBusinessData] = useState({
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
    // Check for OAuth callback parameters FIRST - allow processing even if not authenticated
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const error = urlParams.get('error');

    if (code || state || error) {
      console.log('🔄 OAuth parameters detected in dashboard, switching to social module');
      setActiveModule('social');
      return; // Don't redirect to login, allow OAuth processing
    }

    if (!isAuthenticated && !isLoading) {
      navigate('/login');
      return;
    }

    if (user && activeModule === 'business') {
      // Load business dashboard data
      loadBusinessData();
    }
  }, [user, isAuthenticated, isLoading, activeModule]);

  const loadBusinessData = async () => {
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
          setBusinessData(prev => ({
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
          setBusinessData(prev => ({
            ...prev,
            onboardingProgress: onboarding,
          }));
        }
      } catch (error) {
        console.log('Onboarding endpoint not available, using mock data');
        // Keep default mock data
      }
    } catch (error) {
      console.error('Failed to load business dashboard data:', error);
    }
  };

  const handleModuleChange = (module: string) => {
    setActiveModule(module);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Will redirect to login
  }

  const renderBusinessContent = () => (
    <div className="space-y-6 md:space-y-8">
      {/* Top Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
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
      <div className="mb-6 md:mb-8">
        <QuickActions user={user} />
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Left Column - Analytics & AI Hub */}
        <div className="lg:col-span-2 space-y-4 md:space-y-6">
          <AnalyticsOverview analytics={businessData.analytics} />
          <AIContentHub user={user} />
        </div>

        {/* Right Column - Onboarding */}
        <div>
          <OnboardingChecklist
            progress={businessData.onboardingProgress}
            user={user}
            onProgressUpdate={loadBusinessData}
          />
        </div>
      </div>
    </div>
  );

  const renderSocialContent = () => (
    <React.Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    }>
      <SocialDashboard />
    </React.Suspense>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar Navigation */}
      <SidebarNavigation
        activeModule={activeModule}
        onModuleChange={handleModuleChange}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col md:ml-0">
        {/* Dashboard Header */}
        <DashboardHeader user={user} />

        {/* Module Content */}
        <div className="flex-1 p-4 md:p-8">
          {activeModule === 'business' && renderBusinessContent()}
          {activeModule === 'social' && renderSocialContent()}
        </div>
      </div>
    </div>
  );
};

export default UnifiedDashboard;