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

function App() {
  const [showPerformanceDashboard, setShowPerformanceDashboard] = useState(false);
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

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

    window.addEventListener('popstate', handlePopState);
    
    // Listen for custom navigation events
    window.addEventListener('navigate', handleNavigation);
    
    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('navigate', handleNavigation);
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
        const UnifiedDashboard = React.lazy(() => import('./pages/Dashboard/UnifiedDashboard'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <UnifiedDashboard />
          </React.Suspense>
        );
      case '/verify-email':
        const EmailVerificationPage = React.lazy(() => import('./pages/EmailVerificationPage'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <EmailVerificationPage />
          </React.Suspense>
        );
      case '/co-creator':
        const CoCreatorSignupPage = React.lazy(() => import('./pages/CoCreatorSignupPage'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <CoCreatorSignupPage />
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
        // Lazy load admin dashboard
        const AdminDashboard = React.lazy(() => import('./pages/AdminDashboard'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <AdminDashboard />
          </React.Suspense>
        );
      case '/schedule-posts':
        // Lazy load schedule posts page
        const SchedulePostsPage = React.lazy(() => import('./pages/SchedulePostsPage'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <SchedulePostsPage />
          </React.Suspense>
        );
      case '/smart-hashtags':
        // Lazy load smart hashtags page
        const SmartHashtagsPage = React.lazy(() => import('./pages/SmartHashtagsPage'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <SmartHashtagsPage />
          </React.Suspense>
        );
      case '/image-suggestions':
        // Lazy load image suggestions page
        const ImageSuggestionsPage = React.lazy(() => import('./pages/ImageSuggestionsPage'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <ImageSuggestionsPage />
          </React.Suspense>
        );
      case '/chat-assistant':
        // Lazy load chat assistant page
        const ChatAssistantPage = React.lazy(() => import('./pages/ChatAssistantPage'));
        return (
          <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <ChatAssistantPage />
          </React.Suspense>
        );
      default:
        return <LandingPage />;
    }
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
    </div>
  );
}

export default App;
