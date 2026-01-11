import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { config } from '../../config/environment';
import { CoCreatorProgramStatus } from '../../types';
import LandingPageAPI from '../../services/landingPageApi';
import Button from '../ui/Button';
import RazorpayCheckout from '../payment/RazorpayCheckout';
import { pricingService } from '../../services/pricingService';
import { Crown, Users, Zap, Clock, CheckCircle, X } from 'lucide-react';

interface CoCreatorProgramOfferProps {
  readinessLevel: string;
  score: number;
}

const CoCreatorProgramOffer: React.FC<CoCreatorProgramOfferProps> = ({
  readinessLevel,
  score,
}) => {
  const { updateUser } = useAuth();
  const navigate = useNavigate();
  const [programStatus, setProgramStatus] = useState<CoCreatorProgramStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPaymentFlow, setShowPaymentFlow] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [pricing, setPricing] = useState<{ priceInr: number }>({ priceInr: 29000 });
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([loadProgramStatus(), loadPricing()]);
      setLoading(false);
    };
    init();
  }, []);

  const loadPricing = async () => {
    try {
      const plans = await pricingService.getAllPlans();
      const coCreatorPlan = plans.find(p => p.name === 'co_creator');
      if (coCreatorPlan) {
        setPricing({
          priceInr: coCreatorPlan.price_inr
        });
      }
    } catch (error) {
      console.error('Failed to load pricing:', error);
    }
  };

  // Auto-hide success toast after 8 seconds
  useEffect(() => {
    if (showSuccessToast) {
      const timer = setTimeout(() => {
        setShowSuccessToast(false);
      }, 8000);
      return () => clearTimeout(timer);
    }
  }, [showSuccessToast]);

  const loadProgramStatus = async () => {
    try {
      const status = await LandingPageAPI.getCoCreatorStatus();
      setProgramStatus(status);
    } catch (error) {
      console.error('Failed to load co-creator status:', error);
    }
  };

  const getOfferTitle = () => {
    if (readinessLevel === 'priority_integration') {
      return 'Exclusive Priority Integration Partnership';
    }
    return 'Join the Co-Creator Program';
  };

  const getOfferDescription = () => {
    if (readinessLevel === 'priority_integration') {
      return 'Your high readiness score qualifies you for our priority integration program with direct founder support.';
    }
    return 'Your assessment shows you\'re ready to be part of our exclusive co-creator community.';
  };

  const getUrgencyLevel = () => {
    if (!programStatus) return 'medium';
    if (programStatus.seatsRemaining <= 5) return 'high';
    if (programStatus.seatsRemaining <= 10) return 'medium';
    return 'low';
  };

  const getUrgencyMessage = () => {
    if (!programStatus) return '';
    const urgency = getUrgencyLevel();
    
    switch (urgency) {
      case 'high':
        return `Only ${programStatus.seatsRemaining} seats left! Secure your spot now.`;
      case 'medium':
        return `${programStatus.seatsRemaining} seats remaining out of ${programStatus.totalSeats}.`;
      case 'low':
        return `${programStatus.seatsRemaining} seats available out of ${programStatus.totalSeats}.`;
      default:
        return '';
    }
  };

  const benefits = [
    'Lifetime AI platform access with all future features (Value: ₹41,500+/month)',
    'Personal AI strategy audit and custom setup (Value: ₹66,400)',
    'Direct influence on AI product roadmap and development',
    'Priority support and integration assistance (Value: ₹49,800)',
    'Early access to new AI features (3-6 months early)',
    'Exclusive founder mastermind community access',
    'Monthly AI strategy sessions and exclusive webinars',
    'Custom AI agent configuration for your business',
  ];

  if (loading) {
    return (
      <div className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-xl p-8 text-white">
        <div className="animate-pulse">
          <div className="h-8 bg-white/20 rounded mb-4"></div>
          <div className="h-4 bg-white/20 rounded mb-2"></div>
          <div className="h-4 bg-white/20 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-xl p-8 text-white relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full -translate-y-32 translate-x-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white rounded-full translate-y-24 -translate-x-24"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center mb-4">
          <Crown className="w-8 h-8 text-yellow-300 mr-3" />
          <h2 className="text-3xl font-bold">{getOfferTitle()}</h2>
        </div>

        <p className="text-xl mb-6 opacity-90">
          {getOfferDescription()}
        </p>

        {/* Urgency Message */}
        {programStatus && (
          <div className={`inline-flex items-center px-4 py-2 rounded-full mb-6 ${
            getUrgencyLevel() === 'high' ? 'bg-red-500/20 border border-red-300' :
            getUrgencyLevel() === 'medium' ? 'bg-yellow-500/20 border border-yellow-300' :
            'bg-green-500/20 border border-green-300'
          }`}>
            <Clock className="w-4 h-4 mr-2" />
            <span className="font-semibold">{getUrgencyMessage()}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Benefits */}
          <div>
            <h3 className="text-xl font-bold mb-4 flex items-center">
              <Zap className="w-5 h-5 mr-2" />
              Co-Creator Benefits
            </h3>
            <div className="space-y-3">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-300 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="opacity-90">{benefit}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Call to Action */}
          <div className="flex flex-col justify-center">
            <div className="bg-white/10 rounded-lg p-6 mb-6">
              <div className="text-center">
                <div className="text-sm opacity-75 line-through mb-1">
                  Regular Price: {pricingService.formatPrice(167000, 'INR')}+
                </div>
                <div className="text-5xl font-bold mb-2">{pricingService.formatPrice(pricing.priceInr, 'INR')}</div>
                <div className="text-lg opacity-90 mt-2">Founding Member Price</div>
                <div className="text-sm opacity-75 bg-red-500/20 px-3 py-1 rounded-full mt-2 inline-block animate-pulse">
                  🔥 75% Founder Discount - Limited Time
                </div>
                <div className="text-xs opacity-60 mt-2">
                  Pays for itself in first month of AI optimization
                </div>
              </div>
            </div>

            <Button
              variant="secondary"
              size="lg"
              className="w-full bg-white text-primary-600 hover:bg-gray-100"
              icon={Users}
              iconPosition="left"
              onClick={() => setShowPaymentFlow(true)}
            >
              {readinessLevel === 'priority_integration' ? 'Claim Priority Spot' : 'Join Co-Creator Program'}
            </Button>

            <p className="text-center text-sm opacity-75 mt-3">
              30-day money-back guarantee
            </p>
          </div>
        </div>
      </div>

      {/* Razorpay Payment Modal */}
      {showPaymentFlow && !paymentSuccess && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="relative">
            <RazorpayCheckout
              onSuccess={async (paymentData) => {
                console.log('Payment successful:', paymentData);
                
                // Refresh user data to reflect new subscription status
                try {
                  const token = localStorage.getItem('access_token');
                  if (token) {
                    const response = await fetch(`${config.apiBaseUrl}/api/v1/auth/me`, {
                      headers: {
                        'Authorization': `Bearer ${token}`
                      }
                    });
                    
                    if (response.ok) {
                      const updatedUser = await response.json();
                      updateUser(updatedUser);
                      console.log('User profile updated with new subscription:', updatedUser.subscription_tier);
                    }
                  }
                } catch (error) {
                  console.error('Failed to refresh user profile:', error);
                }

                setPaymentSuccess(true);
                setShowPaymentFlow(false);
                // Show success message with modern toast
                setSuccessMessage(`Payment successful! Welcome to the Co-Creator Program!\n\nTransaction ID: ${paymentData.transactionId}\n\nYou'll receive a confirmation email shortly.`);
                setShowSuccessToast(true);
                
                // Redirect to profile after a short delay to allow user to see success message
                setTimeout(() => {
                   navigate('/profile');
                }, 3000);
              }}
              onError={(error) => {
                console.error('Payment error:', error);
                alert(`Payment failed: ${error}\n\nPlease try again or contact support@unitasa.in`);
              }}
              onCancel={() => {
                setShowPaymentFlow(false);
              }}
              customerEmail=""
              customerName=""
              priceInr={pricing.priceInr}
            />
          </div>
        </div>
      )}

      {/* Success State */}
      {paymentSuccess && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-auto text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to the Co-Creator Program!</h3>
            <p className="text-gray-600 mb-6">
              Your payment was successful. You'll receive onboarding instructions via email shortly.
            </p>
            <Button
              onClick={() => {
                setPaymentSuccess(false);
                setShowPaymentFlow(false);
                navigate('/profile');
              }}
              className="w-full"
            >
              Continue to Profile
            </Button>
          </div>
        </div>
      )}

      {/* Modern Success Toast */}
      {showSuccessToast && (
        <div className="fixed top-4 right-4 z-50 max-w-md">
          <div className="bg-green-50 border border-green-200 rounded-lg shadow-lg p-4 transform transition-all duration-300 ease-in-out">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <CheckCircle className="w-6 h-6 text-green-500" />
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-gray-900">
                  Payment Successful!
                </h3>
                <p className="mt-1 text-sm text-gray-600 whitespace-pre-line">
                  {successMessage}
                </p>
              </div>
              <div className="ml-4 flex-shrink-0">
                <button
                  onClick={() => setShowSuccessToast(false)}
                  className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CoCreatorProgramOffer;
