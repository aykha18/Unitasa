import React, { useState } from 'react';
import { Check, X, Crown, Zap, Star, CheckCircle, Calendar } from 'lucide-react';
import Button from '../ui/Button';
import RazorpayCheckout from '../payment/RazorpayCheckout';
import { useCurrency } from '../../hooks/useCurrency';

interface PricingTier {
  name: string;
  basePriceUSD: number;
  description: string;
  features: string[];
  limitations?: string[];
  highlighted?: boolean;
  badge?: string;
  icon?: React.ReactNode;
}

type BillingCycle = 'monthly' | 'quarterly' | 'annual';

const PricingComparison: React.FC = () => {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [billingCycle, setBillingCycle] = useState<BillingCycle>('monthly');
  const currency = useCurrency(49);

  // Base pricing in USD
  const BASE_PRICING = {
    pro: {
      monthly: 49,
      quarterly: 132, // 10% discount
      annual: 499     // 15% discount
    },
    enterprise: {
      monthly: 149,
      quarterly: 402, // 10% discount
      annual: 1519    // 15% discount
    }
  };

  // Currency conversion rates
  const getConversionRate = (currency: string) => {
    switch (currency) {
      case 'INR': return 83;
      case 'EUR': return 0.85;
      default: return 1;
    }
  };

  // Calculate discounted price based on billing cycle
  const getDiscountedPrice = (monthlyPrice: number, cycle: BillingCycle) => {
    const discounts = {
      monthly: 1,
      quarterly: 0.9, // 10% off
      annual: 0.85    // 15% off
    };
    return Math.round(monthlyPrice * discounts[cycle]);
  };

  // Convert USD to current currency
  const convertPrice = (usdPrice: number) => {
    const rate = getConversionRate(currency.currency);
    return Math.round(usdPrice * rate);
  };

  // Format price with currency symbol
  const formatPrice = (amount: number) => {
    if (currency.currency === 'INR') {
      return `₹${amount.toLocaleString('en-IN')}`;
    } else if (currency.currency === 'EUR') {
      return `€${amount}`;
    } else {
      return `$${amount}`;
    }
  };

  // Get billing cycle label
  const getBillingLabel = (cycle: BillingCycle) => {
    switch (cycle) {
      case 'monthly': return 'Monthly';
      case 'quarterly': return '3 Months';
      case 'annual': return 'Annual';
    }
  };

  // Get discount percentage for display
  const getDiscountText = (cycle: BillingCycle) => {
    switch (cycle) {
      case 'monthly': return '';
      case 'quarterly': return 'Save 10%';
      case 'annual': return 'Save 15%';
    }
  };

  const pricingTiers: PricingTier[] = [
    {
      name: 'Pro',
      basePriceUSD: BASE_PRICING.pro[billingCycle],
      description: 'Complete AI marketing automation for growing businesses',
      features: [
        'Unlimited AI content generation',
        'All CRM integrations',
        'Advanced analytics & reporting',
        'Priority email support',
        'API access',
        'Custom AI training'
      ],
      highlighted: true,
      badge: getDiscountText(billingCycle) || 'Most Popular',
      icon: <Zap className="w-6 h-6" />
    },
    {
      name: 'Enterprise',
      basePriceUSD: BASE_PRICING.enterprise[billingCycle],
      description: 'Advanced AI solutions for large organizations',
      features: [
        'Everything in Pro',
        'White-label options',
        'Dedicated account manager',
        'Custom integrations',
        'Advanced security',
        'SLA guarantees'
      ],
      icon: <Star className="w-6 h-6" />
    }
  ];

  const calculateAnnualSavings = () => {
    const standardAnnual = 99 * 12; // $1,188
    const founderPrice = 497;
    return standardAnnual - founderPrice; // $691 first year savings
  };

  const calculateLifetimeValue = () => {
    const standardMonthly = 99;
    const yearsOfUse = 5; // Conservative estimate
    const totalStandardCost = standardMonthly * 12 * yearsOfUse; // $5,940
    const founderPrice = 497;
    return totalStandardCost - founderPrice; // $5,443 lifetime savings
  };

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Choose Your Plan
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Powerful AI marketing automation with flexible billing options.
            All plans include a 14-day free trial.
          </p>

          {/* Billing Cycle Selector */}
          <div className="flex justify-center mb-8">
            <div className="bg-white rounded-lg p-1 shadow-sm border">
              {(['monthly', 'quarterly', 'annual'] as BillingCycle[]).map((cycle) => (
                <button
                  key={cycle}
                  onClick={() => setBillingCycle(cycle)}
                  className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                    billingCycle === cycle
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {getBillingLabel(cycle)}
                  {cycle !== 'monthly' && (
                    <span className="ml-1 text-xs opacity-75">
                      ({getDiscountText(cycle)})
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-16 max-w-5xl mx-auto">
          {pricingTiers.map((tier, index) => {
            const convertedPrice = convertPrice(tier.basePriceUSD);
            const discountedPrice = getDiscountedPrice(convertedPrice, billingCycle);

            return (
              <div
                key={index}
                className={`bg-white rounded-2xl shadow-lg overflow-hidden relative ${
                  tier.highlighted
                    ? 'ring-4 ring-blue-500 transform scale-105'
                    : 'hover:shadow-xl transition-shadow'
                }`}
              >
                {/* Badge */}
                {tier.badge && (
                  <div className="absolute top-4 left-4 right-4 z-10">
                    <div className={`text-white text-xs font-bold px-3 py-1 rounded-full text-center ${
                      billingCycle === 'monthly' ? 'bg-blue-600' : 'bg-green-600'
                    }`}>
                      {tier.badge}
                    </div>
                  </div>
                )}

                <div className={`p-8 ${tier.highlighted ? 'bg-gradient-to-br from-blue-50 to-purple-50' : ''}`}>
                  {/* Header */}
                  <div className="text-center mb-8">
                    <div className="flex items-center justify-center mb-4">
                      {tier.icon}
                      <h3 className="text-2xl font-bold text-gray-900 ml-2">{tier.name}</h3>
                    </div>

                    <div className="mb-4">
                      <div className="flex items-baseline justify-center">
                        <span className={`text-5xl font-bold ${
                          tier.highlighted ? 'text-blue-600' : 'text-gray-900'
                        }`}>
                          {formatPrice(discountedPrice)}
                        </span>
                        <span className="text-xl text-gray-600 ml-1">
                          /{billingCycle === 'monthly' ? 'month' : billingCycle === 'quarterly' ? '3 months' : 'year'}
                        </span>
                      </div>
                      {billingCycle !== 'monthly' && (
                        <div className="text-sm text-green-600 mt-1">
                          {getDiscountText(billingCycle)}
                        </div>
                      )}
                    </div>

                    <p className="text-gray-600">{tier.description}</p>
                  </div>

                  {/* Features */}
                  <div className="space-y-4 mb-8">
                    {tier.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Button */}
                  <Button
                    className={`w-full ${
                      tier.highlighted
                        ? 'bg-blue-600 hover:bg-blue-700'
                        : 'bg-gray-800 hover:bg-gray-900'
                    }`}
                    size="lg"
                    onClick={() => {
                      if (tier.highlighted) {
                        setShowPaymentModal(true);
                      } else {
                        console.log(`${tier.name} button clicked`);
                      }
                    }}
                  >
                    {tier.highlighted ? 'Start Free Trial' : 'Contact Sales'}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Value Comparison */}
        <div className="bg-white rounded-2xl p-8 shadow-lg">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Why Choose Unitasa?
          </h3>

          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div className="bg-green-50 rounded-lg p-6">
              <div className="text-3xl font-bold text-green-600 mb-2">
                60-80%
              </div>
              <div className="text-sm text-gray-600">Cost Savings</div>
              <div className="text-xs text-gray-500 mt-1">vs traditional marketing tools</div>
            </div>

            <div className="bg-blue-50 rounded-lg p-6">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                24/7
              </div>
              <div className="text-sm text-gray-600">AI Automation</div>
              <div className="text-xs text-gray-500 mt-1">Never stops working</div>
            </div>

            <div className="bg-purple-50 rounded-lg p-6">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                300%
              </div>
              <div className="text-sm text-gray-600">Average ROI</div>
              <div className="text-xs text-gray-500 mt-1">Based on customer results</div>
            </div>
          </div>

          <div className="text-center mt-8">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 max-w-2xl mx-auto">
              <h4 className="font-bold text-gray-900 mb-2">
                🚀 Start Your Free Trial Today
              </h4>
              <p className="text-gray-600 text-sm">
                Experience the power of AI-driven marketing automation with our 14-day free trial.
                No credit card required to get started.
              </p>
            </div>
          </div>
        </div>

        {/* Urgency Section */}
        <div className="text-center mt-16">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-lg mx-auto">
            <h4 className="font-bold text-red-800 mb-2">⏰ Founder Pricing Ends Soon</h4>
            <p className="text-red-700 text-sm mb-4">
              Only 12 founding spots remaining. Price increases to $2,000+ after founding phase.
            </p>
            <Button 
              className="bg-red-600 hover:bg-red-700"
              onClick={() => setShowPaymentModal(true)}
            >
              Secure Your Spot Now
            </Button>
          </div>
        </div>

        {/* Payment Modal */}
        {showPaymentModal && !paymentSuccess && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="relative">
              <RazorpayCheckout
                onSuccess={(paymentData) => {
                  console.log('Payment successful:', paymentData);
                  setPaymentSuccess(true);
                  setShowPaymentModal(false);
                  alert(`🎉 Payment successful! Welcome to the Co-Creator Program!\n\nTransaction ID: ${paymentData.transactionId}\n\nYou'll receive onboarding instructions via email shortly.`);
                }}
                onError={(error) => {
                  console.error('Payment error:', error);
                  alert(`❌ Payment failed: ${error}\n\nPlease try again or contact support@unitasa.in`);
                }}
                onCancel={() => {
                  setShowPaymentModal(false);
                }}
                customerEmail=""
                customerName=""
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
                  setShowPaymentModal(false);
                }}
                className="w-full"
              >
                Continue
              </Button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default PricingComparison;
