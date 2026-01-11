import React, { useState, useEffect } from 'react';
import { ArrowLeft, Mail, Lock, Eye, EyeOff, AlertCircle, CheckCircle, Zap, Star } from 'lucide-react';
import { Button } from '../components/ui';
import { config } from '../config/environment';
import { useAuth } from '../context/AuthContext';
import { pricingService, PricingPlan } from '../services/pricingService';

// Google OAuth types
declare global {
  interface Window {
    google: any;
  }
}

interface SignInFormData {
  email: string;
  password: string;
  rememberMe: boolean;
  pricingTier?: 'pro' | 'enterprise';
  billingCycle?: 'monthly' | 'quarterly' | 'annual';
}

interface SignInErrors {
  email?: string;
  password?: string;
  general?: string;
}

const SignInPage: React.FC = () => {
  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  const { login } = useAuth();

  const [formData, setFormData] = useState<SignInFormData>({
    email: '',
    password: '',
    rememberMe: false,
    pricingTier: 'pro',
    billingCycle: 'monthly'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<SignInErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);
  const [showPlanSelection, setShowPlanSelection] = useState(false);
  const [plans, setPlans] = useState<PricingPlan[]>([]);

  // Load Google OAuth script and fetch client ID
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const fetchedPlans = await pricingService.getAllPlans();
        setPlans(fetchedPlans);
      } catch (error) {
        console.error('Failed to fetch pricing plans:', error);
      }
    };
    fetchPlans();

    console.log('🔍 DEBUG: SignInPage useEffect triggered');

    const fetchGoogleClientId = async () => {
      try {
        console.log('🔍 DEBUG: Fetching Google Client ID from API');
        const response = await fetch('/api/v1/config/google-client-id');
        const data = await response.json();
        console.log('🔍 DEBUG: API response:', data);

        if (data.googleClientId) {
          console.log('🔍 DEBUG: Google Client ID received, length:', data.googleClientId.length);
          return data.googleClientId;
        } else {
          console.log('🔍 DEBUG: No Google Client ID in API response');
          return null;
        }
      } catch (error) {
        console.error('🔍 DEBUG: Failed to fetch Google Client ID:', error);
        return null;
      }
    };

    const loadGoogleScript = async () => {
      console.log('🔍 DEBUG: loadGoogleScript called');

      // First fetch the client ID
      const googleClientId = await fetchGoogleClientId();

      if (window.google) {
        console.log('🔍 DEBUG: window.google already exists, calling initializeGoogle');
        initializeGoogle(googleClientId);
        return;
      }

      console.log('🔍 DEBUG: Creating Google script element');
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => {
        console.log('🔍 DEBUG: Google script loaded, calling initializeGoogle');
        initializeGoogle(googleClientId);
      };
      document.head.appendChild(script);
    };

    const initializeGoogle = (googleClientId: string | null) => {
      console.log('🔍 DEBUG: initializeGoogle called');
      console.log('🔍 DEBUG: window.google exists:', !!window.google);
      console.log('🔍 DEBUG: googleClientId exists:', !!googleClientId);

      if (window.google && googleClientId) {
        console.log('🔍 DEBUG: Initializing Google OAuth with client_id:', googleClientId.substring(0, 20) + '...');
        try {
          window.google.accounts.id.initialize({
            client_id: googleClientId,
            callback: handleGoogleSignIn,
          });
          console.log('🔍 DEBUG: Google OAuth initialized successfully');
          setIsGoogleLoaded(true);
        } catch (error) {
          console.error('🔍 DEBUG: Google OAuth initialization failed:', error);
          // Keep button disabled if initialization fails
        }
      } else {
        console.log('🔍 DEBUG: Cannot initialize - window.google or googleClientId missing');
      }
    };

    loadGoogleScript();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[name as keyof SignInErrors]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: SignInErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);
    setErrors({});

    try {
      const success = await login(formData.email, formData.password, formData.rememberMe);

      if (success) {
        // Check if user has selected a plan
        // For now, show plan selection after sign-in
        setShowPlanSelection(true);
      } else {
        setErrors({ general: 'Invalid email or password' });
      }
    } catch (error) {
      console.error('Sign in failed:', error);
      setErrors({ general: 'Network error. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleSignIn = async (response: any) => {
    try {
      setIsSubmitting(true);

      // Get the correct API URL using the same logic as other components
      const getApiBaseUrl = () => {
        if (process.env.REACT_APP_API_URL &&
            !process.env.REACT_APP_API_URL.includes('your-backend-service.railway.app')) {
          return process.env.REACT_APP_API_URL;
        }
        if (process.env.NODE_ENV === 'production' || (typeof window !== 'undefined' && window.location.hostname !== 'localhost')) {
          return '';
        }
        return 'http://localhost:8001';
      };

      const apiBaseUrl = getApiBaseUrl();
      console.log('🔍 DEBUG: Using API base URL for Google OAuth:', apiBaseUrl);

      // For Google OAuth, we still need to make a direct API call since AuthContext doesn't handle OAuth
      const result = await fetch(`${apiBaseUrl}/api/v1/auth/google-oauth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          credential: response.credential,
        }),
      });

      const data = await result.json();

      if (result.ok && data.success) {
        // Store tokens and user data
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        // Trigger auth context update by reloading the page or dispatching an event
        window.location.href = '/dashboard';
      } else {
        setErrors({ general: data.message || 'Google sign in failed' });
      }
    } catch (error) {
      console.error('Google sign in failed:', error);
      setErrors({ general: 'Google sign in failed. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleButtonClick = () => {
    console.log('🔍 DEBUG: SignInPage Google button clicked');

    if (!window.google) {
      console.log('🔍 DEBUG: window.google not available');
      setErrors({ general: 'Google OAuth not loaded. Please refresh the page.' });
      return;
    }

    // First try One Tap prompt
    console.log('🔍 DEBUG: Attempting One Tap prompt');
    window.google.accounts.id.prompt((notification: any) => {
      console.log('🔍 DEBUG: One Tap notification:', notification);

      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        console.log('🔍 DEBUG: One Tap not displayed, trying manual trigger');
        renderGoogleButton();
      }
    });
  };

  const renderGoogleButton = () => {
    console.log('🔍 DEBUG: Attempting to render Google button programmatically');
    try {
      // Create a visible container for the button
      const buttonContainer = document.createElement('div');
      buttonContainer.id = 'google-signin-button-signin-page';
      buttonContainer.style.position = 'fixed';
      buttonContainer.style.top = '-1000px';
      buttonContainer.style.left = '-1000px';
      buttonContainer.style.zIndex = '-1';

      document.body.appendChild(buttonContainer);
      console.log('🔍 DEBUG: Created button container');

      window.google.accounts.id.renderButton(buttonContainer, {
        theme: 'outline',
        size: 'large',
        text: 'continue_with',
        shape: 'rectangular',
        logo_alignment: 'left'
      });

      console.log('🔍 DEBUG: Rendered Google button');

      // Trigger click on the rendered button after a short delay
      setTimeout(() => {
        const renderedButton = buttonContainer.querySelector('div[role="button"]') as HTMLElement;
        console.log('🔍 DEBUG: Looking for rendered button element:', renderedButton);
        if (renderedButton) {
          console.log('🔍 DEBUG: Found rendered button, clicking it');
          renderedButton.click();
          console.log('🔍 DEBUG: Clicked rendered Google button');
        } else {
          console.log('🔍 DEBUG: Could not find rendered button element');
          // Try alternative selectors
          const altButton = buttonContainer.querySelector('button') as HTMLElement;
          if (altButton) {
            console.log('🔍 DEBUG: Found button with alt selector, clicking');
            altButton.click();
          } else {
            console.log('🔍 DEBUG: No button found with any selector');
            console.log('🔍 DEBUG: Container HTML:', buttonContainer.innerHTML);
          }
        }

        // Clean up
        setTimeout(() => {
          document.body.removeChild(buttonContainer);
          console.log('🔍 DEBUG: Cleaned up button container');
        }, 1000);
      }, 200);
    } catch (error) {
      console.error('🔍 DEBUG: Error rendering Google button:', error);
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  const handleForgotPassword = () => {
    navigate('/forgot-password');
  };

  // Calculate dynamic prices
  const getPrice = (planName: string, cycle: 'monthly' | 'quarterly' | 'annual') => {
    const plan = plans.find(p => p.name === planName);
    const basePrice = plan ? plan.price_inr : (planName === 'pro' ? 4999 : 19999);
    
    let multiplier = 1;
    let months = 1;
    
    if (cycle === 'quarterly') {
      multiplier = 0.9; // 10% discount
      months = 3;
    } else if (cycle === 'annual') {
      multiplier = 0.85; // 15% discount
      months = 12;
    }
    
    const total = Math.round(basePrice * months * multiplier);
    const monthly = Math.round(total / months);
    
    return {
      total: pricingService.formatPrice(total, 'INR'),
      monthly: pricingService.formatPrice(monthly, 'INR')
    };
  };

  const proPrices = getPrice('pro', formData.billingCycle || 'monthly');
  const enterprisePrices = getPrice('enterprise', formData.billingCycle || 'monthly');

  return (
    <div className="min-h-screen bg-gradient-to-br from-unitasa-light via-white to-unitasa-light">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={handleBackToHome}
              className="flex items-center text-unitasa-gray hover:text-unitasa-blue transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Home
            </button>
            <div className="flex items-center space-x-2">
              <div className="bg-primary-600 p-2 rounded-lg">
                <div className="w-6 h-6 bg-white rounded flex items-center justify-center text-primary-600 text-sm font-bold">
                  U
                </div>
              </div>
              <span className="text-xl font-bold text-unitasa-blue">Unitasa</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-unitasa-blue mb-2">Welcome Back</h1>
            <p className="text-unitasa-gray">
              Sign in to your Unitasa account
            </p>
          </div>

          {/* Error Message */}
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
              <span className="text-red-700">{errors.general}</span>
            </div>
          )}

          {/* Google OAuth Button */}
          <div className="mb-6">
            <Button
              type="button"
              onClick={handleGoogleButtonClick}
              variant="outline"
              size="lg"
              className="w-full flex items-center justify-center space-x-3 border-gray-300 hover:border-gray-400"
              disabled={!isGoogleLoaded || isSubmitting}
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span>Continue with Google</span>
            </Button>
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or sign in with email</span>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="your@email.com"
                />
              </div>
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`w-full pl-10 pr-10 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Remember me</span>
              </label>
              <button
                type="button"
                onClick={handleForgotPassword}
                className="text-sm text-primary-600 hover:text-primary-500"
              >
                Forgot password?
              </button>
            </div>

            {/* Submit Button */}
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Signing In...' : 'Sign In'}
              </Button>
            </form>
  
            {/* Plan Selection Section */}
            {showPlanSelection && (
              <div className="mt-8 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl border border-blue-200">
                <div className="text-center mb-6">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome back!</h3>
                  <p className="text-gray-600">Choose your plan to continue</p>
                </div>
  
                {/* Billing Cycle Selection */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-4">
                    Billing Cycle
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {(['monthly', 'quarterly', 'annual'] as const).map((cycle) => (
                      <button
                        key={cycle}
                        onClick={() => setFormData(prev => ({ ...prev, billingCycle: cycle }))}
                        className={`p-3 border-2 rounded-lg text-center transition-all ${
                          formData.billingCycle === cycle
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-blue-300'
                        }`}
                      >
                        <div className="font-semibold text-sm capitalize">{cycle}</div>
                        {cycle !== 'monthly' && (
                          <div className="text-xs text-green-600 mt-1">
                            Save {cycle === 'quarterly' ? '10%' : '15%'}
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
  
                {/* Pricing Tier Selection */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-4">
                    Choose Your Plan
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button
                      onClick={() => setFormData(prev => ({ ...prev, pricingTier: 'pro' }))}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        formData.pricingTier === 'pro'
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:border-green-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">Pro Plan</h4>
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          formData.pricingTier === 'pro' ? 'border-green-500 bg-green-500' : 'border-gray-300'
                        }`}>
                          {formData.pricingTier === 'pro' && <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>}
                        </div>
                      </div>
                      <div className="mb-2">
                        {formData.billingCycle === 'monthly' && <p className="text-2xl font-bold text-green-600">{proPrices.total}<span className="text-sm font-normal">/month</span></p>}
                        {formData.billingCycle === 'quarterly' && <p className="text-2xl font-bold text-green-600">{proPrices.total}<span className="text-sm font-normal">/quarter</span><span className="text-sm text-green-600 ml-2">({proPrices.monthly}/mo)</span></p>}
                        {formData.billingCycle === 'annual' && <p className="text-2xl font-bold text-green-600">{proPrices.total}<span className="text-sm font-normal">/year</span><span className="text-sm text-green-600 ml-2">({proPrices.monthly}/mo)</span></p>}
                      </div>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• 5 CRM integrations</li>
                        <li>• Unlimited leads</li>
                        <li>• Advanced AI features</li>
                      </ul>
                    </button>
  
                    <button
                      onClick={() => setFormData(prev => ({ ...prev, pricingTier: 'enterprise' }))}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        formData.pricingTier === 'enterprise'
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">Enterprise Plan</h4>
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          formData.pricingTier === 'enterprise' ? 'border-purple-500 bg-purple-500' : 'border-gray-300'
                        }`}>
                          {formData.pricingTier === 'enterprise' && <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>}
                        </div>
                      </div>
                      <div className="mb-2">
                        {formData.billingCycle === 'monthly' && <p className="text-2xl font-bold text-purple-600">{enterprisePrices.total}<span className="text-sm font-normal">/month</span></p>}
                        {formData.billingCycle === 'quarterly' && <p className="text-2xl font-bold text-purple-600">{enterprisePrices.total}<span className="text-sm font-normal">/quarter</span><span className="text-sm text-purple-600 ml-2">({enterprisePrices.monthly}/mo)</span></p>}
                        {formData.billingCycle === 'annual' && <p className="text-2xl font-bold text-purple-600">{enterprisePrices.total}<span className="text-sm font-normal">/year</span><span className="text-sm text-purple-600 ml-2">({enterprisePrices.monthly}/mo)</span></p>}
                      </div>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• Unlimited CRM integrations</li>
                        <li>• White-label solution</li>
                        <li>• Custom AI training</li>
                      </ul>
                    </button>
                  </div>
                </div>
  
                {/* Continue Button */}
                <Button
                  onClick={() => navigate('/dashboard')}
                  variant="primary"
                  size="lg"
                  className="w-full"
                  disabled={!formData.pricingTier || !formData.billingCycle}
                >
                  Continue to Dashboard
                </Button>
              </div>
            )}

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-unitasa-gray">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/signup')}
                className="text-primary-600 hover:text-primary-500 font-medium"
              >
                Start your free trial
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignInPage;