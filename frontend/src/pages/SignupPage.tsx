import React, { useState, useEffect } from 'react';
import { ArrowLeft, CheckCircle, Mail, Lock, User, Building } from 'lucide-react';
import { Button } from '../components/ui';
import { config } from '../config/environment';
// Removed React Router dependency - using custom navigation

// Google OAuth types
declare global {
  interface Window {
    google: any;
  }
}

interface SignupFormData {
  firstName: string;
  lastName: string;
  email: string;
  company: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
  pricingTier: 'pro' | 'enterprise';
}

interface SignupErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  company?: string;
  password?: string;
  confirmPassword?: string;
  agreeToTerms?: string;
  pricingTier?: string;
}

const SignupPage: React.FC = () => {
  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  // Load Google OAuth script and fetch client ID
  useEffect(() => {
    console.log('🔍 DEBUG: SignupPage useEffect triggered');

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
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: handleGoogleSignup,
        });
        console.log('🔍 DEBUG: Google OAuth initialized successfully');
        setIsGoogleLoaded(true);
      } else {
        console.log('🔍 DEBUG: Cannot initialize - window.google or googleClientId missing');
      }
    };

    loadGoogleScript();
  }, []);

  const handleGoogleSignup = async (response: any) => {
    console.log('🔍 DEBUG: handleGoogleSignup called');
    console.log('🔍 DEBUG: Google response:', response);
    console.log('🔍 DEBUG: response.credential exists:', !!response.credential);

    try {
      setIsSubmitting(true);
      console.log('🔍 DEBUG: Starting Google signup API call');

      const result = await fetch('/api/v1/auth/google-oauth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          credential: response.credential,
          company: formData.company || undefined,
        }),
      });

      console.log('🔍 DEBUG: API response status:', result.status);
      const data = await result.json();
      console.log('🔍 DEBUG: API response data:', data);

      if (result.ok && data.success) {
        console.log('🔍 DEBUG: Google signup successful, storing tokens');
        // Store tokens and user data
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        alert(`🎉 ${data.message}`);
        console.log('🔍 DEBUG: Navigating to dashboard');
        navigate('/dashboard');
      } else {
        console.log('🔍 DEBUG: Google signup failed with API error');
        throw new Error(data.message || 'Google signup failed');
      }
    } catch (error) {
      console.error('🔍 DEBUG: Google signup failed with exception:', error);
      setErrors({ email: 'Google signup failed. Please try again.' });
    } finally {
      setIsSubmitting(false);
      console.log('🔍 DEBUG: handleGoogleSignup completed');
    }
  };

  const handleGoogleButtonClick = () => {
    console.log('🔍 DEBUG: Google button clicked');
    console.log('🔍 DEBUG: window.google exists:', !!window.google);
    console.log('🔍 DEBUG: isGoogleLoaded state:', isGoogleLoaded);

    if (window.google && isGoogleLoaded) {
      console.log('🔍 DEBUG: Attempting to show Google One Tap');
      try {
        // Try the One Tap prompt first
        window.google.accounts.id.prompt((notification: any) => {
          console.log('🔍 DEBUG: One Tap notification:', notification);
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            console.log('🔍 DEBUG: One Tap not displayed, trying manual trigger');
            // If One Tap doesn't work, we might need to use a different approach
            // For now, let's try to render a button programmatically
            renderGoogleButton();
          }
        });
        console.log('🔍 DEBUG: window.google.accounts.id.prompt() called successfully');
      } catch (error) {
        console.error('🔍 DEBUG: Error with One Tap, trying button render:', error);
        renderGoogleButton();
      }
    } else {
      console.log('🔍 DEBUG: window.google not available or not loaded');
    }
  };

  const renderGoogleButton = () => {
    console.log('🔍 DEBUG: Attempting to render Google button programmatically');
    try {
      // Create a visible container for the button
      const buttonContainer = document.createElement('div');
      buttonContainer.id = 'google-signin-button-programmatic';
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
  const [formData, setFormData] = useState<SignupFormData>({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
    pricingTier: 'pro'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<SignupErrors>({});
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[name as keyof SignupFormData]) {
      setErrors((prev: SignupErrors) => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: SignupErrors = {};

    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email is invalid';
    if (!formData.company.trim()) newErrors.company = 'Company name is required';
    if (!formData.password) newErrors.password = 'Password is required';
    else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
    if (!formData.agreeToTerms) newErrors.agreeToTerms = 'You must agree to the terms';
    if (!formData.pricingTier) newErrors.pricingTier = 'Please select a pricing plan';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      // Call the user registration API
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          pricingTier: formData.pricingTier // Ensure pricing tier is included
        }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        console.log('Registration successful:', result);
        
        // Show success message
        alert(`🎉 ${result.message}`);
        
        // Redirect to success page or dashboard
        navigate('/signup/success');
      } else {
        throw new Error(result.message || 'Registration failed');
      }

    } catch (error) {
      console.error('Signup failed:', error);
      setErrors({ email: 'Signup failed. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

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
            <div className="inline-flex items-center bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
              <CheckCircle className="w-4 h-4 mr-2" />
              15 Days Free Trial
            </div>
            <h1 className="text-3xl font-bold text-unitasa-blue mb-2">Start Your Free Trial</h1>
            <p className="text-unitasa-gray">
              Get full access to Unitasa for 15 days - No credit card required
            </p>
          </div>

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
              <span className="px-2 bg-white text-gray-500">Or sign up with email</span>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name Fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                  First Name *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    id="firstName"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    className={`w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                      errors.firstName ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="John"
                  />
                </div>
                {errors.firstName && <p className="text-red-500 text-sm mt-1">{errors.firstName}</p>}
              </div>

              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    id="lastName"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    className={`w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                      errors.lastName ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Doe"
                  />
                </div>
                {errors.lastName && <p className="text-red-500 text-sm mt-1">{errors.lastName}</p>}
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Work Email *
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
                  placeholder="john@company.com"
                />
              </div>
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>

            {/* Company */}
            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                Company Name *
              </label>
              <div className="relative">
                <Building className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  id="company"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  className={`w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.company ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Acme Corp"
                />
              </div>
              {errors.company && <p className="text-red-500 text-sm mt-1">{errors.company}</p>}
            </div>

            {/* Pricing Tier Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4">
                Choose Your Plan *
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  type="button"
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
                  <p className="text-2xl font-bold text-green-600 mb-2">₹4,999<span className="text-sm font-normal">/month</span></p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• 5 CRM integrations</li>
                    <li>• Unlimited leads</li>
                    <li>• Advanced AI features</li>
                  </ul>
                </button>

                <button
                  type="button"
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
                  <p className="text-2xl font-bold text-purple-600 mb-2">₹19,999<span className="text-sm font-normal">/month</span></p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Unlimited CRM integrations</li>
                    <li>• White-label solution</li>
                    <li>• Custom AI training</li>
                  </ul>
                </button>
              </div>
              {errors.pricingTier && <p className="text-red-500 text-sm mt-1">{errors.pricingTier}</p>}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="At least 8 characters"
                />
              </div>
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className={`w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                    errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Confirm your password"
                />
              </div>
              {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
            </div>

            {/* Terms Agreement */}
            <div>
              <label className="flex items-start">
                <input
                  type="checkbox"
                  name="agreeToTerms"
                  checked={formData.agreeToTerms}
                  onChange={handleInputChange}
                  className="mt-1 mr-3 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  I agree to the{' '}
                  <a href="/terms-of-service" className="text-primary-600 hover:text-primary-500">
                    Terms of Service
                  </a>{' '}
                  and{' '}
                  <a href="/privacy-policy" className="text-primary-600 hover:text-primary-500">
                    Privacy Policy
                  </a>
                </span>
              </label>
              {errors.agreeToTerms && <p className="text-red-500 text-sm mt-1">{errors.agreeToTerms}</p>}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating Account...' : 'Start My Free Trial'}
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-unitasa-gray">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                className="text-primary-600 hover:text-primary-500 font-medium"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="mt-8 text-center">
          <div className="flex items-center justify-center space-x-6 text-sm text-unitasa-gray">
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              15 days free access
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              No credit card required
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              Cancel anytime
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;