import React from 'react';
import { Search, Brain, Zap, ArrowRight, TrendingUp, Target, Lightbulb } from 'lucide-react';

const AgentWorkflowSection: React.FC = () => {
  const workflowSteps = [
    {
      id: 'analyze',
      title: 'Analyze',
      description: 'AI agents continuously monitor your marketing performance, customer behavior, and market trends',
      icon: <Search className="w-8 h-8" />,
      color: 'blue',
      metrics: [
        'Real-time data collection',
        'Performance pattern recognition',
        'Competitive intelligence gathering'
      ]
    },
    {
      id: 'learn',
      title: 'Learn',
      description: 'Machine learning algorithms identify patterns and optimize strategies based on historical data',
      icon: <Brain className="w-8 h-8" />,
      color: 'purple',
      metrics: [
        'Predictive modeling',
        'A/B testing automation',
        'Strategy optimization'
      ]
    },
    {
      id: 'execute',
      title: 'Execute',
      description: 'Autonomous execution of optimized marketing campaigns across all channels',
      icon: <Zap className="w-8 h-8" />,
      color: 'green',
      metrics: [
        'Automated content creation',
        'Dynamic budget allocation',
        'Real-time campaign adjustments'
      ]
    }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: {
        bg: 'bg-blue-100',
        text: 'text-blue-600',
        border: 'border-blue-200',
        arrow: 'text-blue-400'
      },
      purple: {
        bg: 'bg-purple-100',
        text: 'text-purple-600',
        border: 'border-purple-200',
        arrow: 'text-purple-400'
      },
      green: {
        bg: 'bg-green-100',
        text: 'text-green-600',
        border: 'border-green-200',
        arrow: 'text-green-400'
      }
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            How AI Agents Transform Your Marketing
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our autonomous AI agents follow a proven 3-step process to continuously improve
            your marketing performance without human intervention.
          </p>
        </div>

        {/* Workflow Visualization */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {workflowSteps.map((step, index) => {
            const colors = getColorClasses(step.color);
            return (
              <div key={step.id} className="relative">
                {/* Step Card */}
                <div className={`bg-white rounded-xl p-8 shadow-lg border-2 ${colors.border} hover:shadow-xl transition-all duration-300`}>
                  {/* Step Number */}
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full ${colors.bg} ${colors.text} font-bold text-lg mb-6`}>
                    {index + 1}
                  </div>

                  {/* Icon */}
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${colors.bg} ${colors.text} mb-6`}>
                    {step.icon}
                  </div>

                  {/* Content */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{step.title}</h3>
                  <p className="text-gray-600 mb-6">{step.description}</p>

                  {/* Metrics */}
                  <div className="space-y-2">
                    {step.metrics.map((metric, metricIndex) => (
                      <div key={metricIndex} className="flex items-center">
                        <div className={`w-2 h-2 rounded-full ${colors.bg} mr-3`} />
                        <span className="text-sm text-gray-700">{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Arrow (not on last item) */}
                {index < workflowSteps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                    <ArrowRight className={`w-8 h-8 ${colors.arrow}`} />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Benefits Section */}
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Why This Process Works
          </h3>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Continuous Improvement</h4>
              <p className="text-gray-600 text-sm">AI learns from every campaign, getting smarter with each iteration</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Data-Driven Decisions</h4>
              <p className="text-gray-600 text-sm">Every action is backed by real performance data and predictive analytics</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Lightbulb className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Autonomous Optimization</h4>
              <p className="text-gray-600 text-sm">24/7 optimization without human intervention or oversight</p>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="mt-16 grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">15%</div>
            <div className="text-sm text-gray-600">Monthly Performance Improvement</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">10K+</div>
            <div className="text-sm text-gray-600">Decisions Per Hour</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">24/7</div>
            <div className="text-sm text-gray-600">Autonomous Operation</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">0</div>
            <div className="text-sm text-gray-600">Human Intervention Required</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AgentWorkflowSection;