import React, { useState, useEffect } from 'react';
import { CreditCard, Smartphone, Building, Globe, ArrowLeft, Loader } from 'lucide-react';
import Button from '../ui/Button';
import { config } from '../../config/environment';

interface RazorpayCheckoutProps {
  onSuccess: (paymentData: any) => void;
  onError: (error: string) => void;
  onCancel: () => void;
  customerEmail?: string;
  customerName?: string;
  amount?: number; // Optional amount override for testing (USD)
  priceInr?: number; // Exact INR price
  priceUsd?: number; // Exact USD price
}

interface CurrencyInfo {
  currency: string;
  amount: number;
  symbol: string;
  country: string;
  displayAmount: string;
}

declare global {
  interface Window {
    Razorpay: any;
  }
}

const RazorpayCheckout: React.FC<RazorpayCheckoutProps> = ({
  onSuccess,
  onError,
  onCancel,
  customerEmail = '',
  customerName = '',
  amount,
  priceInr,
  priceUsd
}) => {
  const [selectedCurrency, setSelectedCurrency] = useState<string>('INR');
  const [selectedCountry, setSelectedCountry] = useState<string>('IN');
  const [customerDetails, setCustomerDetails] = useState({
    name: customerName,
    email: customerEmail
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [razorpayLoaded, setRazorpayLoaded] = useState(false);

  // Exchange rates and currency info
  const defaultAmountUSD = 497;
  const targetUsd = priceUsd || amount || defaultAmountUSD;
  const exchangeRate = 83; // Fallback USD to INR if priceInr not provided
  
  // Prioritize priceInr if available and currency is INR
  const currentAmount = selectedCurrency === 'INR' && priceInr
    ? priceInr 
    : (selectedCurrency === 'INR' ? targetUsd * exchangeRate : targetUsd);

  const currencyInfo: CurrencyInfo = {
    currency: selectedCurrency,
    amount: currentAmount,
    symbol: selectedCurrency === 'INR' ? '₹' : '$',
    country: selectedCountry,
    displayAmount: selectedCurrency === 'INR' 
      ? `₹${currentAmount.toLocaleString()}` 
      : `$${currentAmount}`
  };

  // Load Razorpay script
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => {
      setRazorpayLoaded(true);
      console.log('✅ Razorpay script loaded successfully');
    };
    script.onerror = () => {
      console.error('❌ Failed to load Razorpay script');
      onError('Failed to load Razorpay. Please refresh and try again.');
    };
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [onError]);

  // Auto-detect user's location
  useEffect(() => {
    // Default to INR for everyone as per requirement
    setSelectedCurrency('INR');
    setSelectedCountry('IN');
  }, []);

  const handleCurrencyChange = (currency: string, country: string) => {
    setSelectedCurrency(currency);
    setSelectedCountry(country);
  };

  const createRazorpayOrder = async () => {
    try {
      const apiUrl = config.apiBaseUrl;
      const token = localStorage.getItem('access_token');
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${apiUrl}/api/v1/payments/razorpay/create-order`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          amount: currentAmount,
          customer_email: customerDetails.email,
          customer_name: customerDetails.name,
          currency: selectedCurrency,
          customer_country: selectedCountry,
          program_type: 'co_creator'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create payment order');
      }

      const orderData = await response.json();
      
      if (!orderData.success) {
        throw new Error(orderData.message || 'Failed to create order');
      }

      return orderData;
    } catch (error) {
      console.error('Order creation error:', error);
      throw error;
    }
  };

  const handlePayment = async () => {
    if (!customerDetails.name || !customerDetails.email) {
      onError('Please fill in all required fields');
      return;
    }

    if (!razorpayLoaded) {
      onError('Payment system is still loading. Please wait a moment and try again.');
      return;
    }

    setIsProcessing(true);

    try {
      const orderData = await createRazorpayOrder();

      const options = {
        key: orderData.key_id,
        amount: Math.round(currencyInfo.amount * 100), // Convert to smallest currency unit
        currency: selectedCurrency,
        name: 'Unitasa',
        description: 'Co-Creator Program Access',
        order_id: orderData.order_id,
        prefill: {
          name: customerDetails.name,
          email: customerDetails.email
        },
        theme: {
          color: '#3b82f6'
        },
        handler: function(response: any) {
          handlePaymentSuccess(response, orderData);
        },
        modal: {
          ondismiss: function() {
            setIsProcessing(false);
            onCancel();
          }
        }
      };

      console.log('🔑 Razorpay options:', {
        key: options.key,
        amount: options.amount,
        currency: options.currency,
        order_id: options.order_id
      });

      const rzp = new window.Razorpay(options);
      
      // Add error handling for Razorpay initialization
      rzp.on('payment.failed', function (response: any) {
        console.error('❌ Razorpay payment failed:', response.error);
        setIsProcessing(false);
        onError(`Payment failed: ${response.error.description || 'Unknown error'}`);
      });

      rzp.open();
    } catch (error) {
      setIsProcessing(false);
      onError(error instanceof Error ? error.message : 'Payment initialization failed');
    }
  };

  const handlePaymentSuccess = async (razorpayResponse: any, orderData: any) => {
    try {
      // Use the same API URL logic as AdminDashboard
      const getApiUrl = () => {
        // In production (not localhost), always use relative URLs
        if (window.location.hostname !== 'localhost' &&
            window.location.hostname !== '127.0.0.1') {
          console.log('Production detected, using relative URLs');
          return ''; // Relative URLs will use the same domain
        }

        // If REACT_APP_API_URL is set and it's not the placeholder, use it
        if (process.env.REACT_APP_API_URL &&
            !process.env.REACT_APP_API_URL.includes('your-backend-service.railway.app') &&
            !process.env.REACT_APP_API_URL.includes('railway.app')) {
          console.log('Using REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
          return process.env.REACT_APP_API_URL;
        }

        // Development default
        console.log('Using localhost default');
        return 'http://localhost:8000';
      };

      const apiUrl = getApiUrl();
      // Verify payment on backend
      const verifyResponse = await fetch(`${apiUrl}/api/v1/payments/razorpay/verify-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          razorpay_order_id: razorpayResponse.razorpay_order_id,
          razorpay_payment_id: razorpayResponse.razorpay_payment_id,
          razorpay_signature: razorpayResponse.razorpay_signature
        })
      });

      const verifyData = await verifyResponse.json();

      if (verifyData.success && verifyData.verified) {
        onSuccess({
          transactionId: razorpayResponse.razorpay_payment_id,
          orderId: razorpayResponse.razorpay_order_id,
          amount: currencyInfo.amount,
          currency: selectedCurrency,
          customerEmail: customerDetails.email,
          customerName: customerDetails.name,
          paymentMethod: 'razorpay'
        });
      } else {
        onError('Payment verification failed. Please contact support.');
      }
    } catch (error) {
      onError('Payment verification failed. Please contact support.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-2xl max-w-2xl mx-auto overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Join Co-Creator Program</h2>
            <p className="opacity-90">Secure payment powered by Razorpay</p>
          </div>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-white/10 rounded-full transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Currency Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Select Your Currency</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => handleCurrencyChange('INR', 'IN')}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                selectedCurrency === 'INR'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-2">🇮🇳</span>
                <span className="font-semibold">Indian Rupees</span>
              </div>
              <div className="text-2xl font-bold text-green-600">₹{(priceInr || targetUsd * exchangeRate).toLocaleString()}</div>
              <div className="text-sm text-gray-600 flex items-center mt-1">
                <Smartphone className="w-4 h-4 mr-1" />
                UPI, Cards, Net Banking
              </div>
            </button>

            <button
              onClick={() => handleCurrencyChange('USD', 'US')}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                selectedCurrency === 'USD'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-2">🌍</span>
                <span className="font-semibold">US Dollars</span>
              </div>
              <div className="text-2xl font-bold text-green-600">${targetUsd}</div>
              <div className="text-sm text-gray-600 flex items-center mt-1">
                <CreditCard className="w-4 h-4 mr-1" />
                International Cards
              </div>
            </button>
          </div>
        </div>

        {/* Customer Details */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Your Details</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                value={customerDetails.name}
                onChange={(e) => setCustomerDetails(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your full name"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <input
                type="email"
                value={customerDetails.email}
                onChange={(e) => setCustomerDetails(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your email address"
                required
              />
            </div>
          </div>
        </div>

        {/* Payment Summary */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">Co-Creator Program</span>
            <span className="font-semibold">{currencyInfo.displayAmount}</span>
          </div>
          <div className="flex justify-between items-center text-sm text-gray-500">
            <span>One-time payment</span>
            <span>Lifetime access</span>
          </div>
          {selectedCurrency === 'INR' && (
            <div className="text-xs text-gray-500 mt-1">
              Equivalent to ${targetUsd} USD
            </div>
          )}
        </div>

        {/* Payment Methods Preview */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Available Payment Methods:</h4>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            {selectedCurrency === 'INR' ? (
              <>
                <div className="flex items-center">
                  <Smartphone className="w-4 h-4 mr-1" />
                  UPI
                </div>
                <div className="flex items-center">
                  <CreditCard className="w-4 h-4 mr-1" />
                  Cards
                </div>
                <div className="flex items-center">
                  <Building className="w-4 h-4 mr-1" />
                  Net Banking
                </div>
              </>
            ) : (
              <div className="flex items-center">
                <Globe className="w-4 h-4 mr-1" />
                International Cards (Visa, Mastercard, Amex)
              </div>
            )}
          </div>
        </div>

        {/* Pay Button */}
        <Button
          onClick={handlePayment}
          disabled={isProcessing || !razorpayLoaded}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-4 text-lg font-semibold"
        >
          {isProcessing ? (
            <>
              <Loader className="w-5 h-5 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              Pay {currencyInfo.displayAmount}
            </>
          )}
        </Button>

        {/* Security Note */}
        <div className="text-center mt-4">
          <p className="text-xs text-gray-500">
            🔒 Secure payment powered by Razorpay • 256-bit SSL encryption
          </p>
          <p className="text-xs text-gray-500 mt-1">
            30-day money-back guarantee • Support: support@unitasa.in
          </p>
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-700">
              <p>🧪 Development Mode: If payment fails with 401 error, the Razorpay test keys may need domain configuration.</p>
              <p>Contact support@unitasa.in for payment assistance.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RazorpayCheckout;