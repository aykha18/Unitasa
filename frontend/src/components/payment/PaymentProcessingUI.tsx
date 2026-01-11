import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { PaymentIntent, PaymentForm, PaymentResult } from '../../types';
import Button from '../ui/Button';
import TrustBadges, { InlineTrustBadges, PaymentMethodBadges } from './TrustBadges';
import { categorizeStripeError } from './PaymentErrorHandler';
import { pricingService } from '../../services/pricingService';
import {
  CreditCard,
  AlertCircle,
  Loader,
  ArrowLeft,
  Mail,
  User,
  Building,
  Phone,
  Crown
} from 'lucide-react';

// Initialize Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || '');

interface PaymentProcessingUIProps {
  onPaymentSuccess: (result: PaymentResult) => void;
  onBack: () => void;
  className?: string;
}

interface PaymentFormComponentProps {
  onPaymentSuccess: (result: PaymentResult) => void;
  onBack: () => void;
}

const PaymentFormComponent: React.FC<PaymentFormComponentProps> = ({ onPaymentSuccess, onBack }) => {
  const stripe = useStripe();
  const elements = useElements();
  
  const [formData, setFormData] = useState<PaymentForm>({
    email: '',
    name: '',
    businessName: '',
    phone: ''
  });
  
  const [paymentIntent, setPaymentIntent] = useState<PaymentIntent | null>(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Partial<PaymentForm>>({});
  const [retryCount, setRetryCount] = useState(0);
  const [showRetryOptions, setShowRetryOptions] = useState(false);

  useEffect(() => {
    createPaymentIntent();
  }, []);

  const createPaymentIntent = async () => {
    try {
      // First, reserve a co-creator seat
      const reservationResponse = await fetch('/api/v1/landing/co-creator-program/reserve-seat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email || 'temp@example.com',
          name: formData.name || 'Temporary User',
          company: formData.businessName
        }),
      });

      if (!reservationResponse.ok) {
        const errorData = await reservationResponse.json().catch(() => ({}));
        throw new Error(errorData.message || 'Failed to reserve co-creator seat');
      }

      const reservation = await reservationResponse.json();
      
      if (!reservation.success) {
        throw new Error(reservation.message || 'Failed to reserve seat');
      }

      // Create payment intent with the reserved co-creator ID
      const paymentResponse = await fetch('/api/v1/landing/payments/create-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          co_creator_id: reservation.seat_number, // Using seat_number as co_creator_id
          customer_email: formData.email || 'temp@example.com',
          customer_name: formData.name || 'Temporary User'
        }),
      });

      if (!paymentResponse.ok) {
        const errorData = await paymentResponse.json().catch(() => ({}));
        throw new Error(errorData.message || 'Failed to create payment intent');
      }

      const intent = await paymentResponse.json();
      
      if (!intent.success) {
        throw new Error(intent.message || 'Failed to create payment intent');
      }

      setPaymentIntent({
        id: intent.payment_intent_id,
        clientSecret: intent.client_secret,
        amount: intent.amount,
        currency: intent.currency,
        status: 'requires_payment_method'
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize payment. Please try again.');
      console.error('Payment intent creation failed:', err);
    }
  };

  const validateForm = (): boolean => {
    const errors: Partial<PaymentForm> = {};
    
    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    // Name validation
    if (!formData.name) {
      errors.name = 'Full name is required';
    } else if (formData.name.trim().length < 2) {
      errors.name = 'Please enter your full name';
    }
    
    // Phone validation (if provided)
    if (formData.phone && formData.phone.trim()) {
      const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
      if (!phoneRegex.test(formData.phone.replace(/[\s\-\(\)]/g, ''))) {
        errors.phone = 'Please enter a valid phone number';
      }
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!stripe || !elements || !paymentIntent) {
      setError('Payment system not ready. Please try again.');
      return;
    }

    if (!validateForm()) {
      return;
    }

    setProcessing(true);
    setError(null);

    const cardElement = elements.getElement(CardElement);
    if (!cardElement) {
      setError('Card information is required');
      setProcessing(false);
      return;
    }

    try {
      // Confirm payment with Stripe
      const { error: stripeError, paymentIntent: confirmedPayment } = await stripe.confirmCardPayment(
        paymentIntent.clientSecret,
        {
          payment_method: {
            card: cardElement,
            billing_details: {
              name: formData.name,
              email: formData.email,
              phone: formData.phone || undefined,
            },
          },
        }
      );

      if (stripeError) {
        const categorizedError = categorizeStripeError(stripeError);
        throw new Error(categorizedError.message);
      }

      if (confirmedPayment?.status === 'succeeded') {
        // Confirm payment status with backend
        const statusResponse = await fetch(`/api/v1/landing/payments/${confirmedPayment.id}/status`);
        
        if (!statusResponse.ok) {
          throw new Error('Failed to verify payment status. Please contact support with payment ID: ' + confirmedPayment.id);
        }

        const paymentStatus = await statusResponse.json();
        
        if (paymentStatus.status !== 'succeeded') {
          throw new Error('Payment verification failed. Status: ' + paymentStatus.status);
        }

        // Get co-creator ID from payment transaction
        const coCreatorId = paymentStatus.transaction_id;
        
        // Trigger onboarding sequence
        try {
          const onboardingResponse = await fetch(`/api/v1/landing/co-creator-program/${coCreatorId}/start-onboarding`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            }
          });

          if (!onboardingResponse.ok) {
            console.warn('Onboarding trigger failed, but payment succeeded');
          }
        } catch (onboardingError) {
          console.warn('Onboarding trigger failed, but payment succeeded:', onboardingError);
        }
        
        onPaymentSuccess({
          success: true,
          paymentIntentId: confirmedPayment.id,
          coCreatorId: coCreatorId?.toString(),
        });
      } else {
        throw new Error('Payment was not completed successfully. Status: ' + (confirmedPayment?.status || 'unknown'));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Payment failed';
      setError(errorMessage);
      setRetryCount(prev => prev + 1);
      
      if (retryCount >= 2) {
        setShowRetryOptions(true);
      }
      
      console.error('Payment error:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setRetryCount(0);
    setShowRetryOptions(false);
    createPaymentIntent();
  };

  const handleInputChange = (field: keyof PaymentForm, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#ffffff',
        '::placeholder': {
          color: '#9ca3af',
        },
        backgroundColor: 'transparent',
      },
      invalid: {
        color: '#ef4444',
      },
    },
    hidePostalCode: false,
  };

  const formattedPrice = paymentIntent 
    ? new Intl.NumberFormat('en-US', { style: 'currency', currency: paymentIntent.currency.toUpperCase() }).format(paymentIntent.amount / 100)
    : pricingService.formatPrice(29999, 'INR');

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <Crown className="w-8 h-8 text-yellow-400 mr-3" />
          <h2 className="text-3xl font-bold text-white">Secure Your Co-Creator Spot</h2>
        </div>
        <p className="text-gray-300">Join 25 exclusive co-creators shaping the future of AI marketing automation</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Customer Information */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <User className="w-5 h-5 mr-2" />
            Your Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                Email Address *
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className={`w-full px-4 py-3 bg-white/10 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                  formErrors.email ? 'border-red-500' : 'border-white/20'
                }`}
                placeholder="your@email.com"
                required
              />
              {formErrors.email && (
                <p className="text-red-400 text-sm mt-1">{formErrors.email}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <User className="w-4 h-4 inline mr-1" />
                Full Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className={`w-full px-4 py-3 bg-white/10 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                  formErrors.name ? 'border-red-500' : 'border-white/20'
                }`}
                placeholder="John Doe"
                required
              />
              {formErrors.name && (
                <p className="text-red-400 text-sm mt-1">{formErrors.name}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Building className="w-4 h-4 inline mr-1" />
                Business Name
              </label>
              <input
                type="text"
                value={formData.businessName}
                onChange={(e) => handleInputChange('businessName', e.target.value)}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Your Company"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Phone className="w-4 h-4 inline mr-1" />
                Phone Number
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                className={`w-full px-4 py-3 bg-white/10 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                  formErrors.phone ? 'border-red-500' : 'border-white/20'
                }`}
                placeholder="+1 (555) 123-4567"
              />
              {formErrors.phone && (
                <p className="text-red-400 text-sm mt-1">{formErrors.phone}</p>
              )}
            </div>
          </div>
        </div>

        {/* Payment Information */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <CreditCard className="w-5 h-5 mr-2" />
            Payment Information
          </h3>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Card Details
            </label>
            <div className="p-4 bg-white/10 border border-white/20 rounded-lg">
              <CardElement options={cardElementOptions} />
            </div>
          </div>

          {/* Security Indicators */}
          <InlineTrustBadges className="mb-4" />
        </div>

        {/* Order Summary */}
        <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-xl p-6 border border-yellow-400/30">
          <h3 className="text-xl font-semibold text-white mb-4">Order Summary</h3>
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-300">Co-Creator Program (Lifetime)</span>
            <span className="text-white font-semibold">{formattedPrice}</span>
          </div>
          <div className="flex justify-between items-center mb-4 text-sm text-gray-400">
            <span>Processing Fee</span>
            <span>Included</span>
          </div>
          <div className="border-t border-white/20 pt-4">
            <div className="flex justify-between items-center text-xl font-bold text-white">
              <span>Total</span>
              <span>{formattedPrice}</span>
            </div>
            <p className="text-sm text-gray-300 mt-2">One-time payment • Lifetime value: $6,000+ • 75% founder discount</p>
          </div>
        </div>

        {/* Enhanced Error Display with Comprehensive Retry Mechanisms */}
        {error && (
          <div className="bg-red-500/20 border border-red-400 rounded-lg p-6">
            <div className="flex items-start">
              <AlertCircle className="w-6 h-6 text-red-400 mr-3 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-200 mb-2">Payment Failed</h3>
                <p className="text-red-200 mb-4">{error}</p>
                
                {retryCount > 0 && (
                  <div className="bg-red-600/20 rounded-lg p-3 mb-4">
                    <p className="text-red-300 text-sm">
                      Attempt {retryCount} of 3 failed. 
                      {retryCount >= 3 ? ' Please try alternative payment methods below.' : ' You can try again or contact support.'}
                    </p>
                  </div>
                )}
                
                <div className="space-y-3">
                  {/* Primary Actions */}
                  <div className="flex flex-wrap gap-2">
                    {retryCount < 3 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRetry}
                        className="text-red-200 border-red-400 hover:bg-red-400/10"
                      >
                        Try Again ({3 - retryCount} attempts left)
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open('mailto:support@unitasa.in?subject=Payment Issue&body=Payment ID: ' + paymentIntent?.id, '_blank')}
                      className="text-red-200 border-red-400 hover:bg-red-400/10"
                    >
                      Contact Support
                    </Button>
                  </div>
                  
                  {/* Alternative Payment Methods */}
                  {retryCount >= 2 && (
                    <div className="border-t border-red-400/30 pt-4">
                      <h4 className="text-red-200 font-medium mb-3">Alternative Payment Options:</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open('tel:+91-9876543210', '_self')}
                          className="text-red-200 border-red-400 hover:bg-red-400/10 justify-start"
                        >
                          📞 Call to Pay
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open('mailto:payments@unitasa.in?subject=Alternative Payment Request', '_blank')}
                          className="text-red-200 border-red-400 hover:bg-red-400/10 justify-start"
                        >
                          💳 Request Bank Transfer
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={onBack}
            className="flex-1"
            icon={ArrowLeft}
            iconPosition="left"
          >
            Back to Program Details
          </Button>
          
          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="flex-1 bg-gradient-to-r from-yellow-400 to-orange-400 text-black hover:from-yellow-300 hover:to-orange-300"
            disabled={!stripe || processing || !paymentIntent}
            icon={processing ? Loader : Crown}
            iconPosition="left"
          >
            {processing ? 'Processing...' : 'Complete Payment'}
          </Button>
        </div>

        {/* Enhanced Payment Methods and Security Trust Indicators */}
        <div className="space-y-6">
          <PaymentMethodBadges />
          <TrustBadges variant="horizontal" size="sm" />
          
          {/* Enhanced Security Assurance */}
          <div className="bg-green-500/10 border border-green-400/30 rounded-lg p-4">
            <div className="text-center">
              <h4 className="text-green-200 font-semibold mb-3 flex items-center justify-center">
                🛡️ Your Security is Our Priority
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-green-400">🔒</span>
                  <span className="text-gray-300">256-bit SSL Encryption</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-green-400">🏛️</span>
                  <span className="text-gray-300">PCI DSS Level 1 Compliant</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-green-400">⚡</span>
                  <span className="text-gray-300">Stripe Secure Processing</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-green-400">🔐</span>
                  <span className="text-gray-300">3D Secure Authentication</span>
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-3">
                We never store your card details. All payments are processed securely by Stripe with bank-level security.
              </p>
            </div>
          </div>
          
          {/* Money Back Guarantee */}
          <div className="text-center bg-blue-500/10 border border-blue-400/30 rounded-lg p-3">
            <p className="text-blue-200 text-sm font-medium">
              💯 30-Day Money-Back Guarantee
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Not satisfied? Get a full refund within 30 days, no questions asked.
            </p>
          </div>
        </div>
      </form>
    </div>
  );
};

const PaymentProcessingUI: React.FC<PaymentProcessingUIProps> = ({
  onPaymentSuccess,
  onBack,
  className = '',
}) => {
  return (
    <div className={`bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 rounded-2xl p-8 ${className}`}>
      <Elements stripe={stripePromise}>
        <PaymentFormComponent onPaymentSuccess={onPaymentSuccess} onBack={onBack} />
      </Elements>
    </div>
  );
};

export default PaymentProcessingUI;
