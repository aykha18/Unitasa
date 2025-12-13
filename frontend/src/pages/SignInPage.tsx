import React, { useState, useEffect } from 'react';
import { ArrowLeft, Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui';
import { config } from '../config/environment';
import { useAuth } from '../context/AuthContext';

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
    rememberMe: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<SignInErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);

  // Load Google OAuth script
  useEffect(() => {
    console.log('🔍 DEBUG: SignInPage useEffect triggered');
    console.log('🔍 DEBUG: config.googleClientId:', config.googleClientId);
    console.log('🔍 DEBUG: config.googleClientId length:', config.googleClientId.length);
    console.log('🔍 DEBUG: window.location.hostname:', window.location.hostname);

    const loadGoogleScript = () => {
      console.log('🔍 DEBUG: loadGoogleScript called');
      if (window.google) {
        console.log('🔍 DEBUG: window.google already exists, calling initializeGoogle');
        initializeGoogle();
        return;
      }

      console.log('🔍 DEBUG: Creating Google script element');
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => {
        console.log('🔍 DEBUG: Google script loaded, calling initializeGoogle');
        initializeGoogle();
      };
      document.head.appendChild(script);
    };

    const initializeGoogle = () => {
      console.log('🔍 DEBUG: initializeGoogle called');
      console.log('🔍 DEBUG: window.google exists:', !!window.google);
      console.log('🔍 DEBUG: config.googleClientId exists:', !!config.googleClientId);

      if (window.google && config.googleClientId) {
        console.log('🔍 DEBUG: Initializing Google OAuth with client_id:', config.googleClientId.substring(0, 20) + '...');
        try {
          window.google.accounts.id.initialize({
            client_id: config.googleClientId,
            callback: handleGoogleSignIn,
          });
          console.log('🔍 DEBUG: Google OAuth initialized successfully');
          setIsGoogleLoaded(true);
        } catch (error) {
          console.error('🔍 DEBUG: Google OAuth initialization failed:', error);
          // Keep button disabled if initialization fails
        }
      } else {
        console.log('🔍 DEBUG: Cannot initialize - window.google or config.googleClientId missing');
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
        // Redirect to dashboard
        navigate('/dashboard');
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

      // For Google OAuth, we still need to make a direct API call since AuthContext doesn't handle OAuth
      const result = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/auth/google-oauth`, {
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
    if (window.google) {
      window.google.accounts.id.prompt();
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  const handleForgotPassword = () => {
    navigate('/forgot-password');
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