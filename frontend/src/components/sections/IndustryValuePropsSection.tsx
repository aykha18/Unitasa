import React from 'react';
import { Target, TrendingUp, Users, Zap, Building2, ShoppingCart, Briefcase, Heart, DollarSign, GraduationCap, MoreHorizontal } from 'lucide-react';
import { useIndustryDetection, IndustryType } from '../../hooks/useIndustryDetection';

const IndustryValuePropsSection: React.FC = () => {
  const { data, industry, isLoading, updateIndustry } = useIndustryDetection();

  const getIndustryIcon = (industryType: IndustryType) => {
    const icons = {
      saas: <Building2 className="w-8 h-8" />,
      ecommerce: <ShoppingCart className="w-8 h-8" />,
      consulting: <Briefcase className="w-8 h-8" />,
      healthcare: <Heart className="w-8 h-8" />,
      finance: <DollarSign className="w-8 h-8" />,
      education: <GraduationCap className="w-8 h-8" />,
      other: <MoreHorizontal className="w-8 h-8" />
    };
    return icons[industryType] || icons.other;
  };

  const getIndustryColor = (industryType: IndustryType) => {
    const colors = {
      saas: 'blue',
      ecommerce: 'green',
      consulting: 'purple',
      healthcare: 'red',
      finance: 'yellow',
      education: 'indigo',
      other: 'gray'
    };
    return colors[industryType] || colors.other;
  };

  if (isLoading) {
    return (
      <section className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto mb-8"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto mb-12"></div>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="h-32 bg-gray-200 rounded"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </section>
    );
  }

  const color = getIndustryColor(industry);

  return (
    <section className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className={`inline-flex items-center bg-${color}-100 text-${color}-800 px-4 py-2 rounded-full text-sm font-medium mb-4`}>
            {getIndustryIcon(industry)}
            <span className="ml-2 capitalize">{industry.replace('_', ' ')} Industry Focus</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Tailored for Your Industry
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {data.useCase}
          </p>
        </div>

        {/* Value Proposition Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-12">
          <div className="flex items-start">
            <div className={`p-4 bg-${color}-100 rounded-xl text-${color}-600 mr-6`}>
              <Target className="w-8 h-8" />
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Your Industry Value Proposition
              </h3>
              <p className="text-lg text-gray-700 leading-relaxed">
                {data.valueProposition}
              </p>
            </div>
          </div>
        </div>

        {/* Key Benefits Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {data.keyBenefits.map((benefit, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
              <div className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center mb-4`}>
                <TrendingUp className={`w-6 h-6 text-${color}-600`} />
              </div>
              <p className="text-gray-700 font-medium">{benefit}</p>
            </div>
          ))}
        </div>

        {/* Industry Selector */}
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 text-center mb-6">
            Explore Other Industries
          </h3>
          <p className="text-gray-600 text-center mb-8">
            See how Unitasa adapts to different business types
          </p>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
            {Object.entries({
              saas: 'SaaS',
              ecommerce: 'E-commerce',
              consulting: 'Consulting',
              healthcare: 'Healthcare',
              finance: 'Finance',
              education: 'Education',
              other: 'Other'
            }).map(([key, label]) => (
              <button
                key={key}
                onClick={() => updateIndustry(key as IndustryType)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  industry === key
                    ? `border-${color}-500 bg-${color}-50 text-${color}-700`
                    : 'border-gray-200 hover:border-gray-300 text-gray-600 hover:text-gray-800'
                }`}
              >
                <div className="text-center">
                  <div className="mb-2">
                    {getIndustryIcon(key as IndustryType)}
                  </div>
                  <div className="text-sm font-medium">{label}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Ready to Transform Your {industry.charAt(0).toUpperCase() + industry.slice(1)} Business?
            </h3>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Join industry leaders who have automated their marketing and scaled their growth with AI.
            </p>
            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openLeadCapture'));
              }}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Start Your AI Assessment
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default IndustryValuePropsSection;