import React, { useState } from 'react';
import { Shield, Clock, CheckCircle, Star, ArrowRight, Zap, TrendingUp, Users, Award } from 'lucide-react';
import { useCurrency } from '../../hooks/useCurrency';

const TrialEnhancementSection: React.FC = () => {
  const currency = useCurrency(497);
  const [selectedPlan, setSelectedPlan] = useState<'pro' | 'enterprise'>('pro');

  const trialFeatures = [
    {
      icon: <Zap className="w-5 h-5" />,
      title: 'Instant Setup',
      description: 'Get started in under 5 minutes with guided onboarding'
    },
    {
      icon: <Shield className="w-5 h-5" />,
      title: 'No Credit Card Required',
      description: 'Start your trial without payment information'
    },
    {
      icon: <Users className="w-5 h-5" />,
      title: 'Full Feature Access',
      description: 'Experience all premium features during your trial'
    },
    {
      icon: <TrendingUp className="w-5 h-5" />,
      title: 'Real Data Integration',
      description: 'Connect your actual CRM and social accounts'
    },
    {
      icon: <Clock className="w-5 h-5" />,
      title: '14-Day Full Access',
      description: 'Two full weeks to see real results'
    },
    {
      icon: <Award className="w-5 h-5" />,
      title: 'Expert Support',
      description: 'Dedicated onboarding specialist during trial'
    }
  ];

  const trialSteps = [
    {
      step: 1,
      title: 'Sign Up & Connect',
      description: 'Create your account and connect your CRM/social accounts',
      time: '2 minutes',
      status: 'completed' as const
    },
    {
      step: 2,
      title: 'AI Assessment',
      description: 'Our AI analyzes your current marketing setup',
      time: '5 minutes',
      status: 'in-progress' as const
    },
    {
      step: 3,
      title: 'Custom Strategy',
      description: 'Receive personalized automation recommendations',
      time: '10 minutes',
      status: 'pending' as const
    },
    {
      step: 4,
      title: 'Live Demo',
      description: 'See your first AI agents in action',
      time: '15 minutes',
      status: 'pending' as const
    },
    {
      step: 5,
      title: 'Go Live',
      description: 'Start automating with confidence',
      time: 'Ongoing',
      status: 'pending' as const
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      company: 'TechFlow',
      rating: 5,
      text: 'The trial convinced me in 3 days. Unitasa delivered more qualified leads than our entire sales team.',
      results: '300% more leads in first week'
    },
    {
      name: 'Marcus Rodriguez',
      company: 'HealthFirst',
      rating: 5,
      text: 'Risk-free trial meant we could test without commitment. The results spoke for themselves.',
      results: '92% patient engagement increase'
    },
    {
      name: 'Priya Patel',
      company: 'FinSecure',
      rating: 5,
      text: 'Started as a trial, now it\'s our core marketing engine. The ROI was undeniable.',
      results: '150% client acquisition growth'
    }
  ];

  const getPlanDetails = (plan: 'pro' | 'enterprise') => {
    if (plan === 'pro') {
      return {
        name: 'Pro Plan',
        price: currency.currency === 'INR' ? '₹4,999' : '$65',
        period: '/month',
        features: [
          'Up to 5 CRM integrations',
          'Unlimited leads processing',
          'Advanced AI content generation',
          'Real-time analytics dashboard',
          'Priority email support',
          'Custom automation workflows'
        ]
      };
    } else {
      return {
        name: 'Enterprise Plan',
        price: currency.currency === 'INR' ? '₹19,999' : '$250',
        period: '/month',
        features: [
          'Unlimited CRM integrations',
          'White-label solution',
          'Custom AI model training',
          'Dedicated success manager',
          'API access & webhooks',
          'Advanced reporting & insights'
        ]
      };
    }
  };

  const selectedPlanDetails = getPlanDetails(selectedPlan);

  return (
    <section className="py-20 bg-gradient-to-br from-green-50 to-emerald-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Shield className="w-4 h-4 mr-2" />
            Risk-Free Trial
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Try Unitasa Risk-Free for 14 Days
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Experience the full power of AI marketing automation. No setup fees, no credit card required,
            and cancel anytime. See real results in your business within days.
          </p>
        </div>

        {/* Trial Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {trialFeatures.map((feature, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="flex items-start">
                <div className="p-2 bg-green-100 rounded-lg text-green-600 mr-4">
                  {feature.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Trial Onboarding Flow */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-16">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Your 15-Minute Trial Journey
          </h3>

          <div className="relative">
            {/* Progress line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

            {/* Steps */}
            <div className="space-y-8">
              {trialSteps.map((step, index) => (
                <div key={index} className="flex items-start">
                  {/* Step number */}
                  <div className={`flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center text-sm font-bold mr-6 ${
                    step.status === 'completed'
                      ? 'bg-green-500 text-white'
                      : step.status === 'in-progress'
                      ? 'bg-blue-500 text-white animate-pulse'
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {step.status === 'completed' ? <CheckCircle className="w-6 h-6" /> : step.step}
                  </div>

                  {/* Step content */}
                  <div className="flex-1 pb-8">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-lg font-semibold text-gray-900">{step.title}</h4>
                      <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                        {step.time}
                      </span>
                    </div>
                    <p className="text-gray-600">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Plan Selection */}
        <div className="grid lg:grid-cols-2 gap-8 mb-16">
          {/* Plan Comparison */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Choose Your Trial Plan</h3>

            <div className="space-y-4">
              {(['pro', 'enterprise'] as const).map((plan) => {
                const details = getPlanDetails(plan);
                return (
                  <button
                    key={plan}
                    onClick={() => setSelectedPlan(plan)}
                    className={`w-full p-4 rounded-lg border-2 transition-all ${
                      selectedPlan === plan
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="text-left">
                        <h4 className="font-semibold text-gray-900">{details.name}</h4>
                        <p className="text-sm text-gray-600">
                          {details.price}{details.period}
                        </p>
                      </div>
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        selectedPlan === plan ? 'border-green-500 bg-green-500' : 'border-gray-300'
                      }`}>
                        {selectedPlan === plan && <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Selected Plan Features */}
            <div className="mt-6">
              <h4 className="font-semibold text-gray-900 mb-4">What's Included:</h4>
              <ul className="space-y-2">
                {selectedPlanDetails.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Trial CTA */}
          <div className="bg-gradient-to-br from-green-600 to-emerald-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">Start Your Risk-Free Trial</h3>
            <p className="text-green-100 mb-6">
              Join 500+ companies that started with our trial and never looked back.
              Your first 14 days are completely free.
            </p>

            <div className="bg-white/10 rounded-lg p-4 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold mb-1">
                  {selectedPlanDetails.price}
                  <span className="text-lg font-normal">{selectedPlanDetails.period}</span>
                </div>
                <div className="text-sm text-green-100">After trial (cancel anytime)</div>
              </div>
            </div>

            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openLeadCapture'));
              }}
              className="w-full bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors flex items-center justify-center mb-4"
            >
              Start Free Trial
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>

            <div className="text-center text-sm text-green-100">
              No credit card required • 14-day full access • Cancel anytime
            </div>
          </div>
        </div>

        {/* Trial Success Stories */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-16">
          <h3 className="text-xl font-bold text-gray-900 text-center mb-8">
            Trial Success Stories
          </h3>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-3">
                  {Array.from({ length: testimonial.rating }, (_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-gray-700 mb-4 italic">
                  "{testimonial.text}"
                </blockquote>
                <div className="font-semibold text-gray-900">{testimonial.name}</div>
                <div className="text-sm text-gray-600 mb-2">{testimonial.company}</div>
                <div className="inline-block bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full">
                  {testimonial.results}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Guarantee Section */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <Shield className="w-16 h-16 mx-auto mb-4 text-blue-200" />
            <h3 className="text-2xl font-bold mb-4">Our 30-Day Money-Back Guarantee</h3>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              We're so confident in Unitasa's results that if you don't see measurable improvements
              in your marketing performance within 30 days, we'll refund every penny.
            </p>
            <div className="grid md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-2xl font-bold mb-2">30 Days</div>
                <div className="text-sm text-blue-100">Full Refund Period</div>
              </div>
              <div>
                <div className="text-2xl font-bold mb-2">No Questions</div>
                <div className="text-sm text-blue-100">Asked</div>
              </div>
              <div>
                <div className="text-2xl font-bold mb-2">100%</div>
                <div className="text-sm text-blue-100">Money Back</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TrialEnhancementSection;