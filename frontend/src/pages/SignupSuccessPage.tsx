import React from 'react';
import { CheckCircle, ArrowRight, Mail } from 'lucide-react';
import { Button } from '../components/ui';

const SignupSuccessPage: React.FC = () => {
  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  const handleGoToLogin = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-unitasa-light via-white to-unitasa-light">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate('/')}
              className="flex items-center text-unitasa-gray hover:text-unitasa-blue transition-colors"
            >
              <ArrowRight className="w-5 h-5 mr-2 rotate-180" />
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
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          {/* Success Icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>

          {/* Header */}
          <h1 className="text-3xl font-bold text-unitasa-blue mb-4">
            Welcome to Unitasa!
          </h1>

          <p className="text-unitasa-gray mb-6">
            Your account has been created successfully. You can now access your dashboard and start exploring all the features.
          </p>

          {/* Email Verification Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <Mail className="w-5 h-5 text-blue-500 mt-0.5 mr-3" />
              <div className="text-left">
                <p className="text-blue-800 font-medium text-sm">
                  Check your email
                </p>
                <p className="text-blue-700 text-sm">
                  We've sent you a verification link to confirm your email address and activate your account.
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            <Button
              onClick={handleGoToDashboard}
              variant="primary"
              size="lg"
              className="w-full"
            >
              Go to Dashboard
            </Button>

            <Button
              onClick={handleGoToLogin}
              variant="outline"
              size="lg"
              className="w-full"
            >
              Sign In to Your Account
            </Button>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-unitasa-gray">
              Need help?{' '}
              <a href="/contact" className="text-primary-600 hover:text-primary-500 font-medium">
                Contact our support team
              </a>
            </p>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="mt-8 text-center">
          <div className="flex items-center justify-center space-x-6 text-sm text-unitasa-gray">
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              Secure & encrypted
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              15 days free trial
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              No credit card required
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignupSuccessPage;