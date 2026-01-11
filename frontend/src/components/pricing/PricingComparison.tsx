import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Check, X, Crown, Zap, Star, CheckCircle, Calendar } from 'lucide-react';
import Button from '../ui/Button';
import RazorpayCheckout from '../payment/RazorpayCheckout';
import { pricingService, PricingPlan } from '../../services/pricingService';

interface PricingTier {
  name: string;
  basePriceUSD: number;
  basePriceINR: number;
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
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  
  const [currency, setCurrency] = useState({ currency: 'INR', symbol: '₹' });
  
  // Co-creator plan for checkout
  const [coCreatorPlan, setCoCreatorPlan] = useState<PricingPlan | null>(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const data = await pricingService.getAllPlans();
        setPlans(data);
        const ccPlan = data.find(p => p.name === 'co_creator');
        if (ccPlan) setCoCreatorPlan(ccPlan);
      } catch (error) {
        console.error('Failed to fetch pricing plans:', error);
      }
    };
    fetchPlans();
  }, []);

  // Calculate discounted price based on billing cycle
  const getDiscountedPrice = (price: number, cycle: BillingCycle) => {
    const discounts = {
      monthly: 1,
      quarterly: 0.9, // 10% off
      annual: 0.85    // 15% off
    };
    return Math.round(price * discounts[cycle]);
  };

  // Format price with currency symbol
  const formatDisplayPrice = (amount: number, currencyCode: string) => {
    return pricingService.formatPrice(amount, currencyCode as 'USD' | 'INR');
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

  const getPlanPrice = (planName: string, type: 'USD' | 'INR') => {
    const name = planName.toLowerCase();
    const plan = plans.find(p => p.name === name);
    // Fallback values if plan not found
    if (!plan) return type === 'USD' ? (name === 'pro' ? 49 : 149) : (name === 'pro' ? 4999 : 19999);
    return type === 'USD' ? plan.price_usd : plan.price_inr;
  };

  const pricingTiers: PricingTier[] = [
    {
      name: 'Pro',
      basePriceUSD: getPlanPrice('Pro', 'USD'),
      basePriceINR: getPlanPrice('Pro', 'INR'),
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
      basePriceUSD: getPlanPrice('Enterprise', 'USD'),
      basePriceINR: getPlanPrice('Enterprise', 'INR'),
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

  // Logic to calculate savings - updated to be dynamic if needed, or kept simple
  const getFounderPrice = (type: 'USD' | 'INR') => {
    if (coCreatorPlan) return type === 'USD' ? coCreatorPlan.price_usd : coCreatorPlan.price_inr;
    return type === 'USD' ? 497 : 29999;
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
            const isINR = currency.currency === 'INR';
            const basePrice = isINR ? tier.basePriceINR : tier.basePriceUSD;
            const discountedPrice = getDiscountedPrice(basePrice, billingCycle);

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
                          {formatDisplayPrice(discountedPrice, 'INR')}
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
              Only 12 founding spots remaining. Price increases to {pricingService.formatPrice(167000, 'INR')}+ after founding phase.
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
                  
                  // Show success message
                  toast.success(`Welcome to the Co-Creator Program! Transaction ID: ${paymentData.transactionId}`, {
                    duration: 6000
                  });
                  toast.success("You'll receive onboarding instructions via email shortly.", {
                    duration: 6000,
                    icon: '📧'
                  });
                }}
                onError={(error) => {
                  console.error('Payment failed:', error);
                  toast.error(`Payment failed: ${error}`);
                  toast.error('Please try again or contact support@unitasa.in');
                }}
                onCancel={() => {
                  setShowPaymentModal(false);
                }}
                customerEmail=""
                customerName=""
                priceInr={coCreatorPlan?.price_inr}
                priceUsd={coCreatorPlan?.price_usd}
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
