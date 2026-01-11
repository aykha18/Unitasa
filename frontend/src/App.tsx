import React, { useEffect, useState } from 'react';
import LandingPage from './pages/LandingPage';
import SignupPage from './pages/SignupPage';
import SignupSuccessPage from './pages/SignupSuccessPage';
import SignInPage from './pages/SignInPage';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import RefundPolicy from './pages/RefundPolicy';
import Contact from './pages/Contact';
import PerformanceDashboard from './components/dev/PerformanceDashboard';

// Import assessment modal for global event handling
import AssessmentModal from './components/assessment/AssessmentModal';

import { Toaster } from 'react-hot-toast';

import { initializeSecurity } from './utils/security';
import './App.css';
import './styles/ai-animations.css';
import { 
  measureWebVitals, 
  monitorBundlePerformance, 
  monitorMemoryUsage, 
  monitorNetworkPerformance 
} from './utils/performanceMonitoring';
import { 
  optimizeMobileViewport, 
  applyMobileOptimizations, 
  inlineCriticalCSS, 
  preconnectExternalDomains 
} from './utils/responsiveUtils';
import { preloadCriticalImages } from './utils/imageOptimization';
import { 
  preloadCriticalChunks, 
  implementResourceHints, 
  monitorBundleLoading, 
  validateTreeShaking,
  optimizeCriticalResourceLoading
} from './utils/bundleOptimization';
import { register as registerSW } from './utils/serviceWorker';
import { runTask11_2Validation } from './utils/performanceValidator';

// Lazy load pages
const UnifiedDashboard = React.lazy(() => import('./pages/Dashboard/UnifiedDashboard'));
const EmailVerificationPage = React.lazy(() => import('./pages/EmailVerificationPage'));
const CoCreatorSignupPage = React.lazy(() => import('./pages/CoCreatorSignupPage'));
const GenerateContentPage = React.lazy(() => import('./pages/GenerateContentPage'));
const SettingsPage = React.lazy(() => import('./pages/SettingsPage'));
const BrandProfilePage = React.lazy(() => import('./pages/BrandProfilePage'));
const AdminDashboard = React.lazy(() => import('./pages/AdminDashboard'));
const SchedulePostsPage = React.lazy(() => import('./pages/SchedulePostsPage'));
const ClientOnboardingPage = React.lazy(() => import('./pages/ClientOnboardingPage'));
const SmartHashtagsPage = React.lazy(() => import('./pages/SmartHashtagsPage'));
const ImageSuggestionsPage = React.lazy(() => import('./pages/ImageSuggestionsPage'));
const ChatAssistantPage = React.lazy(() => import('./pages/ChatAssistantPage'));

function App() {
  const [showPerformanceDashboard, setShowPerformanceDashboard] = useState(false);
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  // Global modal states for cross-page functionality
  const [isAssessmentOpen, setIsAssessmentOpen] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState(null);

  useEffect(() => {
    // Handle browser back/forward and programmatic navigation
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
      window.scrollTo(0, 0); // Scroll to top on navigation
    };

    // Handle programmatic navigation
    const handleNavigation = () => {
      setCurrentPath(window.location.pathname);
    };

    // Global event handlers for modals
    const handleOpenAssessment = () => {
      console.log('🎯 Global openAssessment event received, opening modal');
      setIsAssessmentOpen(true);
    };

    // Check for OAuth callback parameters on page load
    const checkOAuthCallback = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const error = urlParams.get('error');

      if (code || state || error) {
        console.log('🔄 OAUTH CALLBACK DETECTED GLOBALLY:', {
          has_code: !!code,
          has_state: !!state,
          has_error: !!error,
          current_path: window.location.pathname,
          full_url: window.location.href
        });

        // If we're not already on the dashboard, redirect there with the OAuth params
        // The dashboard component will handle the OAuth callback
        if (window.location.pathname !== '/dashboard') {
          console.log('🔀 Redirecting to dashboard for OAuth processing');
          window.location.href = `/dashboard${window.location.search}`;
          return;
        }
        // If we're already on dashboard, let the dashboard component handle it
      }
    };

    // Check for OAuth callback on initial load
    checkOAuthCallback();

    window.addEventListener('popstate', handlePopState);

    // Listen for custom navigation events
    window.addEventListener('navigate', handleNavigation);

    // Listen for global modal events
    window.addEventListener('openAssessment', handleOpenAssessment);

    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('navigate', handleNavigation);
      window.removeEventListener('openAssessment', handleOpenAssessment);
    };
  }, []);

  useEffect(() => {
    // Initialize security measures
    initializeSecurity();
    
    // Initialize performance monitoring
    measureWebVitals().then(metrics => {
      console.log('Web Vitals:', metrics);
      
      // Send metrics to analytics if needed
      if (metrics.lcp && metrics.lcp > 2500) {
        console.warn('LCP is above 2.5s threshold:', metrics.lcp);
      }
      
      if (metrics.fid && metrics.fid > 100) {
        console.warn('FID is above 100ms threshold:', metrics.fid);
      }
      
      if (metrics.cls && metrics.cls > 0.1) {
        console.warn('CLS is above 0.1 threshold:', metrics.cls);
      }
    });

    // Initialize monitoring
    monitorBundlePerformance();
    monitorMemoryUsage();
    monitorNetworkPerformance();

    // Apply mobile optimizations
    optimizeMobileViewport();
    applyMobileOptimizations();
    inlineCriticalCSS();
    preconnectExternalDomains();
    preloadCriticalImages();

    // Apply bundle optimizations
    preloadCriticalChunks();
    implementResourceHints();
    monitorBundleLoading();
    validateTreeShaking();
    optimizeCriticalResourceLoading();

    // Register service worker for PWA features
    registerSW({
      onSuccess: (registration) => {
        console.log('SW registered successfully');
      },
      onUpdate: (registration) => {
        console.log('SW updated');
      },
      onOfflineReady: () => {
        console.log('App ready for offline use');
      },
      onNeedRefresh: () => {
        console.log('New content available');
      }
    });

    // Run performance validation in development
    if (process.env.NODE_ENV === 'development') {
      setTimeout(() => {
        runTask11_2Validation().catch(console.error);
      }, 3000); // Wait 3 seconds for page to fully load

      // Add keyboard shortcut to open performance dashboard (Ctrl+Shift+P)
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.ctrlKey && event.shiftKey && event.key === 'P') {
          event.preventDefault();
          setShowPerformanceDashboard(true);
        }
      };

      window.addEventListener('keydown', handleKeyDown);
      return () => {
        window.removeEventListener('keydown', handleKeyDown);
      };
    }

    // Cleanup function
    return () => {
      // Clean up any intervals or listeners if needed
    };
  }, []);

  // Simple routing based on pathname
  const getPageComponent = () => {
    switch (currentPath) {
      case '/signup':
        return <SignupPage />;
      case '/signup/success':
        return <SignupSuccessPage />;
      case '/login':
        return <SignInPage />;
      case '/dashboard':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <UnifiedDashboard />
          </React.Suspense>
        );
      case '/verify-email':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <EmailVerificationPage />
          </React.Suspense>
        );
      case '/co-creator':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <CoCreatorSignupPage />
          </React.Suspense>
        );
      case '/generate-content':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <GenerateContentPage />
          </React.Suspense>
        );
      case '/settings':
      case '/settings/integrations':
      case '/settings/team':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <SettingsPage />
          </React.Suspense>
        );
      case '/brand-profile':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <BrandProfilePage />
          </React.Suspense>
        );
      case '/privacy-policy':
        return <PrivacyPolicy />;
      case '/terms-of-service':
        return <TermsOfService />;
      case '/refund-policy':
        return <RefundPolicy />;
      case '/contact':
        return <Contact />;
      case '/admin':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <AdminDashboard />
          </React.Suspense>
        );
      case '/schedule-posts':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <SchedulePostsPage />
          </React.Suspense>
        );
      case '/onboarding':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <ClientOnboardingPage />
          </React.Suspense>
        );
      case '/smart-hashtags':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <SmartHashtagsPage />
          </React.Suspense>
        );
      case '/image-suggestions':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <ImageSuggestionsPage />
          </React.Suspense>
        );
      case '/chat-assistant':
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <ChatAssistantPage />
          </React.Suspense>
        );
      default:
        return <LandingPage />;
    }
  };

  const handleAssessmentComplete = (result: any) => {
    setAssessmentResult(result);
    setIsAssessmentOpen(false);
    // Could navigate to co-creator payment or next step
  };

  const closeAssessment = () => {
    setIsAssessmentOpen(false);
  };

  return (
    <div className="App">
      {getPageComponent()}

      {process.env.NODE_ENV === 'development' && (
        <PerformanceDashboard
          isVisible={showPerformanceDashboard}
          onClose={() => setShowPerformanceDashboard(false)}
        />
      )}

      <Toaster position="top-right" />
      {/* Global Assessment Modal */}
      {isAssessmentOpen && (
        <React.Suspense fallback={<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>}>
          <AssessmentModal
            isOpen={isAssessmentOpen}
            onClose={closeAssessment}
            onComplete={handleAssessmentComplete}
            leadData={null} // No lead data for co-creator flow
          />
        </React.Suspense>
      )}
    </div>
  );
}

export default App;
