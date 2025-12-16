import React from 'react';
import { CheckCircle, X, Zap, Users, TrendingUp, Shield, Clock, DollarSign } from 'lucide-react';

export {};

interface CompetitorData {
  name: string;
  logo: string;
  monthlyCost: string;
  setupTime: string;
  features: {
    aiAutomation: boolean;
    costReduction: boolean;
    realTimeAnalytics: boolean;
    multiPlatform: boolean;
    customStrategy: boolean;
    dedicatedSupport: boolean;
  };
  limitations: string[];
}

const CompetitorComparison: React.FC = () => {
  const competitors: CompetitorData[] = [
    {
      name: 'Traditional Marketing Agency',
      logo: '🏢',
      monthlyCost: '$5,000+',
      setupTime: '2-4 weeks',
      features: {
        aiAutomation: false,
        costReduction: false,
        realTimeAnalytics: false,
        multiPlatform: true,
        customStrategy: true,
        dedicatedSupport: true
      },
      limitations: [
        'High fixed costs',
        'Manual content creation',
        'Limited scalability',
        'Slow response times',
        'No real-time optimization'
      ]
    },
    {
      name: 'Social Media Tools Stack',
      logo: '🛠️',
      monthlyCost: '$500+',
      setupTime: '1-2 weeks',
      features: {
        aiAutomation: false,
        costReduction: false,
        realTimeAnalytics: true,
        multiPlatform: true,
        customStrategy: false,
        dedicatedSupport: false
      },
      limitations: [
        'Multiple subscriptions needed',
        'No unified strategy',
        'Manual content scheduling',
        'Limited AI capabilities',
        'Fragmented analytics'
      ]
    },
    {
      name: 'Basic AI Content Tools',
      logo: '🤖',
      monthlyCost: '$200+',
      setupTime: '3-5 days',
      features: {
        aiAutomation: true,
        costReduction: false,
        realTimeAnalytics: false,
        multiPlatform: false,
        customStrategy: false,
        dedicatedSupport: false
      },
      limitations: [
        'Generic content output',
        'No strategy optimization',
        'Limited platform integration',
        'No performance tracking',
        'Basic AI capabilities'
      ]
    }
  ];

  const unitasaFeatures = {
    aiAutomation: true,
    costReduction: true,
    realTimeAnalytics: true,
    multiPlatform: true,
    customStrategy: true,
    dedicatedSupport: true
  };

  const unitasaAdvantages = [
    '60-80% cost reduction vs agencies',
    'Intelligent AI content creation',
    'Real-time performance optimization',
    'Unified multi-platform management',
    'Custom strategy development',
    '24/7 AI-powered support'
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-red-100 text-red-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <TrendingUp className="w-4 h-4 mr-2" />
            Market Comparison
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Why Founders Choose Unitasa Over Traditional Solutions
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See how Unitasa delivers enterprise-level AI marketing at a fraction of the cost of traditional agencies and tools.
          </p>
        </div>

        {/* Comparison Table */}
        <div className="overflow-x-auto mb-12">
          <div className="min-w-full bg-white border border-gray-200 rounded-2xl shadow-lg">
            <div className="grid grid-cols-5 gap-0">
              {/* Header Row */}
              <div className="bg-gray-50 p-6 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900">Features</h3>
              </div>
              {competitors.map((competitor, index) => (
                <div key={index} className="bg-gray-50 p-6 border-b border-l border-gray-200 text-center">
                  <div className="text-2xl mb-2">{competitor.logo}</div>
                  <h4 className="font-semibold text-gray-900 text-sm">{competitor.name}</h4>
                  <div className="text-xs text-gray-500 mt-1">
                    {competitor.monthlyCost}/mo
                  </div>
                </div>
              ))}
              <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 border-b border-l border-gray-200 text-center">
                <div className="text-2xl mb-2">🚀</div>
                <h4 className="font-bold text-blue-600">Unitasa</h4>
                <div className="text-xs text-green-600 font-medium mt-1">
                  ₹4,999 - ₹19,999/mo
                </div>
                <div className="text-xs text-blue-500 mt-1">
                  (Founding: ₹29,999 one-time)
                </div>
              </div>

              {/* Feature Rows */}
              {[
                { key: 'aiAutomation', label: 'AI-Powered Automation', icon: <Zap className="w-4 h-4" /> },
                { key: 'costReduction', label: '60-80% Cost Reduction', icon: <DollarSign className="w-4 h-4" /> },
                { key: 'realTimeAnalytics', label: 'Real-Time Analytics', icon: <TrendingUp className="w-4 h-4" /> },
                { key: 'multiPlatform', label: 'Multi-Platform Support', icon: <Users className="w-4 h-4" /> },
                { key: 'customStrategy', label: 'Custom Strategy', icon: <Shield className="w-4 h-4" /> },
                { key: 'dedicatedSupport', label: '24/7 AI Support', icon: <Clock className="w-4 h-4" /> }
              ].map((feature, rowIndex) => (
                <React.Fragment key={feature.key}>
                  <div className={`p-4 border-b border-gray-100 ${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                    <div className="flex items-center">
                      <span className="text-blue-600 mr-2">{feature.icon}</span>
                      <span className="text-sm font-medium text-gray-900">{feature.label}</span>
                    </div>
                  </div>
                  {competitors.map((competitor, colIndex) => (
                    <div key={colIndex} className={`p-4 border-b border-l border-gray-100 text-center ${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                      {competitor.features[feature.key as keyof typeof competitor.features] ? (
                        <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-red-400 mx-auto" />
                      )}
                    </div>
                  ))}
                  <div className={`p-4 border-b border-l border-gray-100 text-center ${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                    <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                  </div>
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>

        {/* Key Advantages */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Limitations of Competitors */}
          <div className="bg-red-50 rounded-2xl p-8 border border-red-200">
            <h3 className="text-xl font-bold text-red-800 mb-6 flex items-center">
              <X className="w-6 h-6 mr-3" />
              Common Pain Points with Traditional Solutions
            </h3>
            <div className="space-y-4">
              {competitors.flatMap(comp => comp.limitations).slice(0, 6).map((limitation, index) => (
                <div key={index} className="flex items-start">
                  <X className="w-4 h-4 text-red-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-red-700 text-sm">{limitation}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Unitasa Advantages */}
          <div className="bg-green-50 rounded-2xl p-8 border border-green-200">
            <h3 className="text-xl font-bold text-green-800 mb-6 flex items-center">
              <CheckCircle className="w-6 h-6 mr-3" />
              Why Founders Choose Unitasa
            </h3>
            <div className="space-y-4">
              {unitasaAdvantages.map((advantage, index) => (
                <div key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-green-700 text-sm">{advantage}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Cost Savings Calculator */}
        <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-2xl p-8 text-white text-center">
          <h3 className="text-2xl font-bold mb-4">
            Calculate Your Potential Savings
          </h3>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Most founders we work with save ₹3-8 lakh monthly by switching from traditional agencies to Unitasa's AI-powered marketing platform.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-2xl font-bold">₹4-8 lakh</div>
              <div className="text-sm text-blue-100">Average Agency Cost</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-2xl font-bold">₹4,999-19,999</div>
              <div className="text-sm text-blue-100">Unitasa Cost</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold text-yellow-300">₹3-6 lakh</div>
              <div className="text-sm text-blue-100">Monthly Savings</div>
            </div>
          </div>
          <button
            onClick={() => {
              window.dispatchEvent(new CustomEvent('openLeadCapture'));
            }}
            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            Get Your Free AI Assessment
          </button>
        </div>

        {/* Social Proof */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-8">
            Join 25+ founders who switched from expensive agencies to AI-powered marketing
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            <div className="text-sm text-gray-500">Previously used:</div>
            {['HubSpot', 'Hootsuite', 'Canva', 'Buffer', 'Later'].map((tool, index) => (
              <div key={index} className="text-sm font-medium text-gray-700">
                {tool}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default CompetitorComparison;