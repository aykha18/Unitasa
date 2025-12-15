import React from 'react';
import { Brain, Search, Zap, ArrowRight, CheckCircle } from 'lucide-react';

const AgentWorkflowSection: React.FC = () => {
  const workflowSteps = [
    {
      step: 1,
      title: 'Analyze',
      description: 'Crawls your website, analyzes competitors, builds comprehensive business profile',
      icon: <Search className="w-8 h-8" />,
      color: 'blue',
      details: [
        'Website content analysis',
        'Competitor research',
        'Audience profiling',
        'Market positioning assessment'
      ]
    },
    {
      step: 2,
      title: 'Learn',
      description: 'Creates knowledge base, identifies patterns, optimizes strategies autonomously',
      icon: <Brain className="w-8 h-8" />,
      color: 'purple',
      details: [
        'Pattern recognition',
        'Performance analysis',
        'Strategy optimization',
        'Continuous learning'
      ]
    },
    {
      step: 3,
      title: 'Execute',
      description: 'Autonomous posting, engagement, lead nurturing 24/7 without human intervention',
      icon: <Zap className="w-8 h-8" />,
      color: 'green',
      details: [
        'Automated content posting',
        'Real-time engagement',
        'Lead qualification',
        'Performance optimization'
      ]
    }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        text: 'text-blue-600',
        icon: 'text-blue-600'
      },
      purple: {
        bg: 'bg-purple-50',
        border: 'border-purple-200',
        text: 'text-purple-600',
        icon: 'text-purple-600'
      },
      green: {
        bg: 'bg-green-50',
        border: 'border-green-200',
        text: 'text-green-600',
        icon: 'text-green-600'
      }
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-unitasa-electric/10 text-unitasa-blue px-4 py-2 rounded-full text-sm font-medium mb-6 border border-unitasa-electric/20">
            <Brain className="w-4 h-4 mr-2" />
            How Our AI Agents Work
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-unitasa-blue mb-4 font-display">
            Intelligent Automation That Actually Learns
          </h2>
          <p className="text-xl text-unitasa-gray max-w-3xl mx-auto">
            Unlike basic rule-based automation, our AI agents analyze, learn from data, and continuously
            optimize your marketing strategies for maximum results.
          </p>
        </div>

        {/* Workflow Visualization */}
        <div className="relative mb-16">
          {/* Connection Line */}
          <div className="hidden lg:block absolute top-24 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-200 via-purple-200 to-green-200 z-0"></div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10">
            {workflowSteps.map((step, index) => {
              const colors = getColorClasses(step.color);
              return (
                <div key={step.step} className="relative">
                  {/* Step Number */}
                  <div className="flex justify-center mb-6">
                    <div className={`w-16 h-16 ${colors.bg} border-2 ${colors.border} rounded-full flex items-center justify-center`}>
                      <span className={`text-2xl font-bold ${colors.text}`}>{step.step}</span>
                    </div>
                  </div>

                  {/* Step Card */}
                  <div className={`bg-white rounded-xl p-8 shadow-lg border ${colors.border} hover:shadow-xl transition-all duration-300`}>
                    {/* Icon */}
                    <div className={`inline-flex p-3 ${colors.bg} rounded-lg ${colors.icon} mb-6`}>
                      {step.icon}
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">
                      {step.title}
                    </h3>

                    {/* Description */}
                    <p className="text-gray-600 mb-6">
                      {step.description}
                    </p>

                    {/* Details */}
                    <div className="space-y-3">
                      {step.details.map((detail, detailIndex) => (
                        <div key={detailIndex} className="flex items-center">
                          <CheckCircle className={`w-4 h-4 ${colors.icon} mr-3 flex-shrink-0`} />
                          <span className="text-sm text-gray-700">{detail}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Arrow for desktop */}
                  {index < workflowSteps.length - 1 && (
                    <div className="hidden lg:flex justify-center mt-8">
                      <ArrowRight className="w-6 h-6 text-gray-400" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Technical Credibility */}
        <div className="bg-gradient-to-r from-slate-50 to-blue-50 rounded-2xl p-8">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Built with Enterprise-Grade AI Architecture
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Our agents use advanced AI models with intelligent routing, ensuring cost-effective,
              high-performance automation that scales with your business.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="text-2xl font-bold text-blue-600 mb-2">OpenRouter + Groq</div>
                <div className="text-sm text-gray-600">Cost-optimized AI routing</div>
                <div className="text-xs text-gray-500 mt-2">60-80% cheaper than GPT-4</div>
              </div>
            </div>
            <div className="text-center">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="text-2xl font-bold text-purple-600 mb-2">RAG Technology</div>
                <div className="text-sm text-gray-600">Context-aware knowledge base</div>
                <div className="text-xs text-gray-500 mt-2">Business-specific insights</div>
              </div>
            </div>
            <div className="text-center">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="text-2xl font-bold text-green-600 mb-2">24/7 Operation</div>
                <div className="text-sm text-gray-600">Autonomous decision making</div>
                <div className="text-xs text-gray-500 mt-2">No human intervention required</div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <h3 className="text-2xl font-bold text-unitasa-blue mb-4 font-display">
            Experience Intelligent Marketing Automation
          </h3>
          <p className="text-unitasa-gray mb-8 max-w-2xl mx-auto">
            See how our AI agents analyze your business, learn from your data, and execute
            winning marketing strategies autonomously.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              className="bg-gradient-primary text-white px-8 py-4 rounded-lg text-lg font-semibold hover:shadow-brand transition-all duration-200"
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openAssessment'));
              }}
            >
              Start Free AI Assessment
            </button>
            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openDemo'));
              }}
              className="border-2 border-unitasa-electric text-unitasa-electric px-8 py-4 rounded-lg text-lg font-semibold hover:bg-unitasa-electric hover:text-white transition-all duration-200"
            >
              Watch AI in Action
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AgentWorkflowSection;