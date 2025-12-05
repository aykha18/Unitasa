import React from 'react';
import { MessageSquare, Users, TrendingUp, BarChart3 } from 'lucide-react';

const BenefitCardsSection: React.FC = () => {
  const benefits = [
    {
      icon: <MessageSquare className="w-8 h-8 text-blue-600" />,
      title: 'Automated Social Posting',
      description: 'Agents create and schedule posts across X, LinkedIn, Instagram, and more.'
    },
    {
      icon: <Users className="w-8 h-8 text-green-600" />,
      title: 'CRM Follow-Ups',
      description: 'Automatically follow up with leads based on behavior and pipeline stage.'
    },
    {
      icon: <TrendingUp className="w-8 h-8 text-purple-600" />,
      title: 'Ad Optimization',
      description: 'Monitor and adjust campaigns in real time to improve ROAS.'
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-orange-600" />,
      title: 'Unified Analytics',
      description: 'See performance across channels in one dashboard.'
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            What Your AI Marketing Team Does
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Autonomous agents handle the complex work so you can focus on growing your business
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {benefits.map((benefit, index) => (
            <div key={index} className="bg-gray-50 rounded-xl p-6 hover:shadow-lg transition-shadow duration-300">
              <div className="mb-4">
                {benefit.icon}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {benefit.title}
              </h3>
              <p className="text-gray-600">
                {benefit.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BenefitCardsSection;