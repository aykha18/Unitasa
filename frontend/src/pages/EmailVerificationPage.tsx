import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { CheckCircle, Mail, AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui';

const EmailVerificationPage: React.FC = () => {
  const [verificationStatus, setVerificationStatus] = useState<'loading' | 'success' | 'error' | 'expired'>('loading');
  const [message, setMessage] = useState('');
  const [isResending, setIsResending] = useState(false);
  const [email, setEmail] = useState('');

  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
      verifyEmail(token);
    } else {
      setVerificationStatus('error');
      setMessage('No verification token provided');
    }
  }, []);

  const verifyEmail = async (token: string) => {
    try {
      const response = await fetch('/api/v1/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setVerificationStatus('success');
        setMessage(result.message);
      } else {
        if (result.detail?.includes('expired')) {
          setVerificationStatus('expired');
        } else {
          setVerificationStatus('error');
        }
        setMessage(result.detail || result.message || 'Verification failed');
      }
    } catch (error) {
      console.error('Verification error:', error);
      setVerificationStatus('error');
      setMessage('Network error occurred. Please try again.');
    }
  };

  const handleResendVerification = async () => {
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    setIsResending(true);

    try {
      const response = await fetch('/api/v1/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        toast.success('Verification email sent! Please check your inbox.');
      } else {
        toast.error(result.detail || result.message || 'Failed to resend verification email');
      }
    } catch (error) {
      console.error('Resend error:', error);
      toast.error('Network error occurred. Please try again.');
    } finally {
      setIsResending(false);
    }
  };

  const handleBackToHome = () => {
    navigate('/');
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
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          {verificationStatus === 'loading' && (
            <>
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-6"></div>
              <h1 className="text-2xl font-bold text-unitasa-blue mb-4">Verifying Your Email</h1>
              <p className="text-unitasa-gray">Please wait while we verify your email address...</p>
            </>
          )}

          {verificationStatus === 'success' && (
            <>
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-6" />
              <h1 className="text-2xl font-bold text-unitasa-blue mb-4">Email Verified!</h1>
              <p className="text-unitasa-gray mb-6">{message}</p>
              <div className="space-y-3">
                <Button
                  onClick={handleGoToDashboard}
                  variant="primary"
                  size="lg"
                  className="w-full"
                >
                  Access Your Dashboard
                </Button>
                <Button
                  onClick={handleGoToLogin}
                  variant="outline"
                  size="lg"
                  className="w-full"
                >
                  Go to Login
                </Button>
              </div>
            </>
          )}

          {verificationStatus === 'error' && (
            <>
              <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-6" />
              <h1 className="text-2xl font-bold text-unitasa-blue mb-4">Verification Failed</h1>
              <p className="text-unitasa-gray mb-6">{message}</p>
              <Button
                onClick={handleGoToLogin}
                variant="primary"
                size="lg"
                className="w-full"
              >
                Go to Login
              </Button>
            </>
          )}

          {verificationStatus === 'expired' && (
            <>
              <Mail className="w-16 h-16 text-yellow-500 mx-auto mb-6" />
              <h1 className="text-2xl font-bold text-unitasa-blue mb-4">Link Expired</h1>
              <p className="text-unitasa-gray mb-6">
                Your verification link has expired. Enter your email below to receive a new verification link.
              </p>
              
              <div className="space-y-4">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <Button
                  onClick={handleResendVerification}
                  variant="primary"
                  size="lg"
                  className="w-full"
                  disabled={isResending}
                >
                  {isResending ? 'Sending...' : 'Send New Verification Email'}
                </Button>
                <Button
                  onClick={handleGoToLogin}
                  variant="outline"
                  size="lg"
                  className="w-full"
                >
                  Go to Login
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationPage;