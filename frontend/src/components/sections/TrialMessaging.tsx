import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, Star, Zap, Shield, TrendingUp, Users, Award, Gift, ArrowRight } from 'lucide-react';

export {};

const TrialMessaging: React.FC = () => {
  const [timeLeft, setTimeLeft] = useState({ hours: 24, minutes: 0, seconds: 0 });

  // Countdown timer for urgency
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 };
        } else if (prev.minutes > 0) {
          return { ...prev, minutes: prev.minutes - 1, seconds: 59 };
        } else if (prev.hours > 0) {
          return { hours: prev.hours - 1, minutes: 59, seconds: 59 };
        }
        return prev;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const trialBenefits = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Instant AI Assessment',
      description: 'Get a comprehensive analysis of your current marketing performance in under 5 minutes',
      highlight: 'Free & Instant'
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: 'Personalized Growth Plan',
      description: 'Receive a custom roadmap showing exactly how to achieve your business goals',
      highlight: 'Custom Strategy'
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: 'Expert AI Recommendations',
      description: 'Access cutting-edge AI insights that typically cost $5,000+ from consultants',
      highlight: 'Enterprise Value'
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Risk-Free Trial',
      description: 'No credit card required, no obligations, just pure value for your business',
      highlight: '100% Free'
    }
  ];

  const socialProof = [
    { number: '25+', label: 'Founders Already Using Unitasa' },
    { number: '$2M+', label: 'Revenue Generated for Clients' },
    { number: '300%', label: 'Average ROI Improvement' },
    { number: '24/7', label: 'AI Support Available' }
  ];

  const urgencyMessages = [
    '⏰ Limited time: Free AI assessment expires in ' + timeLeft.hours + ' hours',
    '🎯 Only 100 founding members get lifetime access at ₹29,999',
    '🚀 Join successful founders who increased revenue by 300%',
    '⚡ Don\'t miss out on enterprise AI marketing from ₹4,999/month'
  ];

  const [currentUrgencyMessage, setCurrentUrgencyMessage] = useState(0);

  useEffect(() => {
    const messageTimer = setInterval(() => {
      setCurrentUrgencyMessage(prev => (prev + 1) % urgencyMessages.length);
    }, 4000);

    return () => clearInterval(messageTimer);
  }, []);

  return (
    <section className="py-20 bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        {/* Urgency Banner */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center bg-yellow-400 text-yellow-900 px-6 py-3 rounded-full font-bold text-sm animate-pulse">
            <Clock className="w-4 h-4 mr-2" />
            {urgencyMessages[currentUrgencyMessage]}
          </div>
        </div>

        {/* Main CTA Section */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Gift className="w-4 h-4 mr-2" />
            Founding Member Offer
          </div>

          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Get Your <span className="text-yellow-400">FREE</span> AI Marketing Assessment
          </h2>

          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Discover exactly how Unitasa can transform your marketing results.
            Get a personalized growth plan worth ₹4-8 lakh - completely free.
          </p>

          {/* Countdown Timer */}
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 inline-block mb-8">
            <div className="text-white/80 text-sm mb-2">Assessment expires in:</div>
            <div className="flex gap-4 text-center">
              <div className="bg-white/20 rounded-lg p-3 min-w-[60px]">
                <div className="text-2xl font-bold text-white">{timeLeft.hours.toString().padStart(2, '0')}</div>
                <div className="text-xs text-white/70">Hours</div>
              </div>
              <div className="bg-white/20 rounded-lg p-3 min-w-[60px]">
                <div className="text-2xl font-bold text-white">{timeLeft.minutes.toString().padStart(2, '0')}</div>
                <div className="text-xs text-white/70">Minutes</div>
              </div>
              <div className="bg-white/20 rounded-lg p-3 min-w-[60px]">
                <div className="text-2xl font-bold text-white">{timeLeft.seconds.toString().padStart(2, '0')}</div>
                <div className="text-xs text-white/70">Seconds</div>
              </div>
            </div>
          </div>

          {/* Main CTA Button */}
          <button
            onClick={() => {
              window.dispatchEvent(new CustomEvent('openAssessment'));
            }}
            className="bg-yellow-400 hover:bg-yellow-500 text-yellow-900 px-12 py-4 rounded-full font-bold text-lg shadow-2xl transform hover:scale-105 transition-all duration-200 mb-4"
          >
            🚀 Get My FREE AI Assessment Now
          </button>

          <p className="text-blue-200 text-sm">
            No credit card required • Takes only 5 minutes • Get results immediately
          </p>
        </div>

        {/* Benefits Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {trialBenefits.map((benefit, index) => (
            <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
              <div className="text-yellow-400 mb-4 flex justify-center">
                {benefit.icon}
              </div>
              <h3 className="text-white font-bold mb-2">{benefit.title}</h3>
              <p className="text-blue-100 text-sm mb-3">{benefit.description}</p>
              <div className="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-xs font-bold inline-block">
                {benefit.highlight}
              </div>
            </div>
          ))}
        </div>

        {/* Social Proof Numbers */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {socialProof.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-yellow-400 mb-2">
                {stat.number}
              </div>
              <div className="text-blue-100 text-sm">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Value Proposition */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 mb-12">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-white mb-4">
              Why Founders Choose Unitasa
            </h3>
            <p className="text-blue-100">
              Join the exclusive group of founding members getting lifetime access
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-yellow-400 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Award className="w-8 h-8 text-yellow-900" />
              </div>
              <h4 className="text-white font-bold mb-2">Flexible Pricing</h4>
              <p className="text-blue-100 text-sm">
                Choose from ₹4,999/mo to ₹29,999 one-time based on your needs
              </p>
            </div>

            <div className="text-center">
              <div className="bg-yellow-400 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-yellow-900" />
              </div>
              <h4 className="text-white font-bold mb-2">Founding Community</h4>
              <p className="text-blue-100 text-sm">
                Join India's first AI marketing founding community with exclusive benefits
              </p>
            </div>

            <div className="text-center">
              <div className="bg-yellow-400 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Star className="w-8 h-8 text-yellow-900" />
              </div>
              <h4 className="text-white font-bold mb-2">Local Support</h4>
              <p className="text-blue-100 text-sm">
                Priority support in Hindi/English with dedicated account management
              </p>
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="text-center">
          <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Transform Your Marketing?
            </h3>
            <p className="text-gray-600 mb-6">
              Join 25 successful founders who discovered their path to marketing success with Unitasa.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200 flex items-center justify-center"
              >
                Start FREE Assessment
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>

              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openDemo'));
                }}
                className="border-2 border-purple-600 text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-all duration-200"
              >
                Watch Live Demo
              </button>
            </div>

            <div className="mt-6 flex items-center justify-center gap-4 text-sm text-gray-500">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                No credit card required
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                Cancel anytime
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                30-day money-back guarantee
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TrialMessaging;