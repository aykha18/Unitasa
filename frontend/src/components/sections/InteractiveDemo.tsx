import React, { useState } from 'react';
import { Play, Pause, RotateCcw, Zap, TrendingUp, Users, Target, ArrowRight, CheckCircle } from 'lucide-react';
import { useIndustryDetection } from '../../hooks/useIndustryDetection';

interface DemoScenario {
  id: string;
  industry: string;
  title: string;
  description: string;
  challenge: string;
  solution: string;
  steps: {
    time: string;
    action: string;
    result: string;
  }[];
  metrics: {
    label: string;
    value: string;
    change: string;
  }[];
  cta: string;
}

const InteractiveDemo: React.FC = () => {
  const { industry: detectedIndustry } = useIndustryDetection();
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const demoScenarios: DemoScenario[] = [
    {
      id: 'saas-lead-gen',
      industry: 'saas',
      title: 'SaaS Lead Generation Automation',
      description: 'Watch how AI agents transform cold leads into qualified prospects in real-time',
      challenge: 'Manual lead qualification taking 2 hours per day, 40% of leads going cold',
      solution: 'AI agents automatically score, nurture, and qualify leads 24/7',
      steps: [
        { time: '0:00', action: 'New lead submits contact form', result: 'AI immediately analyzes intent and company data' },
        { time: '0:05', action: 'Lead scoring algorithm runs', result: 'Lead scored 8.5/10 based on job title, company size, and behavior' },
        { time: '0:10', action: 'Personalized nurture sequence starts', result: 'Custom email sequence with relevant case studies sent' },
        { time: '2:00', action: 'Lead engages with content', result: 'AI detects engagement, adjusts messaging strategy' },
        { time: '24:00', action: 'Lead becomes sales-ready', result: 'High-priority notification sent to sales team' }
      ],
      metrics: [
        { label: 'Lead Response Time', value: '< 5 min', change: '95% faster' },
        { label: 'Lead Qualification Rate', value: '85%', change: '+60%' },
        { label: 'Sales-Ready Leads', value: '3x more', change: '200% increase' }
      ],
      cta: 'Start Your Lead Generation Demo'
    },
    {
      id: 'ecommerce-content',
      industry: 'ecommerce',
      title: 'E-commerce Content Automation',
      description: 'See how AI creates viral product content and manages social commerce campaigns',
      challenge: 'Creating product descriptions and social posts for 500+ SKUs manually',
      solution: 'AI generates optimized content and manages multi-platform campaigns',
      steps: [
        { time: '0:00', action: 'New product added to catalog', result: 'AI analyzes product details, target audience, and competitors' },
        { time: '0:02', action: 'Content generation begins', result: 'Creates SEO-optimized descriptions, social posts, and email copy' },
        { time: '0:05', action: 'Multi-platform scheduling', result: 'Posts scheduled across Instagram, Facebook, and Pinterest' },
        { time: '1:00', action: 'Performance monitoring starts', result: 'AI tracks engagement, clicks, and conversions in real-time' },
        { time: '4:00', action: 'Optimization triggers', result: 'Best-performing content gets amplified, underperformers get replaced' }
      ],
      metrics: [
        { label: 'Content Output', value: '50 posts/day', change: '10x increase' },
        { label: 'Engagement Rate', value: '4.2%', change: '+180%' },
        { label: 'Conversion Rate', value: '3.8%', change: '+120%' }
      ],
      cta: 'Launch E-commerce Demo'
    },
    {
      id: 'consulting-thought-leadership',
      industry: 'consulting',
      title: 'Consulting Thought Leadership',
      description: 'Experience how AI builds your expertise and attracts high-value clients',
      challenge: 'Struggling to establish thought leadership with inconsistent content output',
      solution: 'AI creates expert content and manages client relationship automation',
      steps: [
        { time: '0:00', action: 'Industry trend detected', result: 'AI identifies emerging topic in your consulting niche' },
        { time: '0:15', action: 'Expert article generated', result: 'Creates 2,000-word article with data, examples, and actionable insights' },
        { time: '0:30', action: 'Multi-channel distribution', result: 'Published on blog, LinkedIn, and shared with client database' },
        { time: '2:00', action: 'Client engagement tracking', result: 'AI monitors which clients engage with your thought leadership' },
        { time: '24:00', action: 'Follow-up automation', result: 'Personalized outreach to engaged prospects with consultation offers' }
      ],
      metrics: [
        { label: 'Content Quality Score', value: '9.2/10', change: '+45%' },
        { label: 'Client Acquisition', value: '150%', change: '+200%' },
        { label: 'Thought Leadership Reach', value: '10x', change: '+900%' }
      ],
      cta: 'Experience Consulting Demo'
    },
    {
      id: 'healthcare-patient-engagement',
      industry: 'healthcare',
      title: 'Healthcare Patient Engagement',
      description: 'See compliant AI patient communication and appointment optimization',
      challenge: 'Manual patient follow-ups and appointment reminders causing no-shows',
      solution: 'HIPAA-compliant AI manages patient communication and optimizes scheduling',
      steps: [
        { time: '0:00', action: 'Patient books appointment', result: 'AI confirms details and checks for conflicts or optimizations' },
        { time: '0:01', action: 'Automated confirmation sent', result: 'Personalized SMS/email with preparation instructions' },
        { time: '24:00', action: 'Day-before reminder', result: 'Automated reminder with directions and parking info' },
        { time: '2:00', action: 'Post-visit follow-up', result: 'AI sends satisfaction survey and care instructions' },
        { time: '48:00', action: 'Engagement analysis', result: 'AI identifies patients needing additional care or education' }
      ],
      metrics: [
        { label: 'Appointment Show Rate', value: '92%', change: '+25%' },
        { label: 'Patient Satisfaction', value: '4.8/5', change: '+0.6 stars' },
        { label: 'Patient Retention', value: '88%', change: '+15%' }
      ],
      cta: 'View Healthcare Demo'
    }
  ];

  // Filter scenarios based on detected industry
  const relevantScenarios = demoScenarios.filter(scenario => {
    if (detectedIndustry === scenario.industry) return true;
    // Show related scenarios for consulting (works for most industries)
    if (detectedIndustry !== 'consulting' && scenario.industry === 'consulting') return true;
    // Show SaaS demo as fallback
    if (detectedIndustry !== 'saas' && scenario.industry === 'saas') return true;
    return false;
  }).slice(0, 3);

  const selectedDemo = selectedScenario ? demoScenarios.find(s => s.id === selectedScenario) : null;

  const handlePlay = () => {
    if (!selectedDemo) return;

    setIsPlaying(true);
    const playSteps = () => {
      setCurrentStep(prev => {
        if (prev >= selectedDemo.steps.length - 1) {
          setIsPlaying(false);
          return 0;
        }
        return prev + 1;
      });
    };

    // Auto-play through steps
    const interval = setInterval(playSteps, 3000);
    setTimeout(() => clearInterval(interval), selectedDemo.steps.length * 3000);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentStep(0);
  };

  return (
    <section className="py-20 bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Play className="w-4 h-4 mr-2" />
            Interactive Demos
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            See Unitasa in Action
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Experience real-time AI automation scenarios tailored to your industry.
            Watch how our agents transform business processes in minutes.
          </p>
        </div>

        {/* Scenario Selector */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {relevantScenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => {
                setSelectedScenario(scenario.id);
                setCurrentStep(0);
                setIsPlaying(false);
              }}
              className={`p-6 rounded-xl border-2 transition-all ${
                selectedScenario === scenario.id
                  ? 'border-blue-500 bg-blue-50 shadow-lg'
                  : 'border-gray-200 hover:border-blue-300 bg-white hover:shadow-md'
              }`}
            >
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 mb-2">{scenario.title}</h3>
                <p className="text-sm text-gray-600 mb-3">{scenario.description}</p>
                <div className="flex items-center text-blue-600 text-sm font-medium">
                  <Play className="w-4 h-4 mr-1" />
                  Watch Demo
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Interactive Demo Player */}
        {selectedDemo && (
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-12">
            {/* Demo Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{selectedDemo.title}</h3>
                <p className="text-gray-600">{selectedDemo.description}</p>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleReset}
                  className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                  title="Reset Demo"
                >
                  <RotateCcw className="w-5 h-5" />
                </button>
                <button
                  onClick={handlePlay}
                  disabled={isPlaying}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center disabled:opacity-50"
                >
                  {isPlaying ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                  {isPlaying ? 'Playing...' : 'Play Demo'}
                </button>
              </div>
            </div>

            {/* Challenge & Solution */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h4 className="font-semibold text-red-800 mb-3 flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  Challenge
                </h4>
                <p className="text-red-700">{selectedDemo.challenge}</p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <h4 className="font-semibold text-green-800 mb-3 flex items-center">
                  <Zap className="w-5 h-5 mr-2" />
                  AI Solution
                </h4>
                <p className="text-green-700">{selectedDemo.solution}</p>
              </div>
            </div>

            {/* Timeline Visualization */}
            <div className="mb-8">
              <h4 className="font-semibold text-gray-900 mb-4">Demo Timeline</h4>
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-20 top-0 bottom-0 w-0.5 bg-gray-200"></div>

                {/* Timeline steps */}
                <div className="space-y-6">
                  {selectedDemo.steps.map((step, index) => (
                    <div key={index} className="flex items-start">
                      {/* Time indicator */}
                      <div className={`flex-shrink-0 w-16 text-sm font-medium ${
                        index <= currentStep ? 'text-blue-600' : 'text-gray-400'
                      }`}>
                        {step.time}
                      </div>

                      {/* Step circle */}
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full border-4 flex items-center justify-center mr-4 ${
                        index < currentStep
                          ? 'bg-green-500 border-green-500 text-white'
                          : index === currentStep
                          ? 'bg-blue-500 border-blue-500 text-white animate-pulse'
                          : 'bg-white border-gray-300 text-gray-400'
                      }`}>
                        {index < currentStep ? (
                          <CheckCircle className="w-4 h-4" />
                        ) : (
                          <span className="text-xs font-bold">{index + 1}</span>
                        )}
                      </div>

                      {/* Step content */}
                      <div className={`flex-1 p-4 rounded-lg ${
                        index <= currentStep ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'
                      }`}>
                        <div className="font-medium text-gray-900 mb-1">{step.action}</div>
                        <div className={`text-sm ${index <= currentStep ? 'text-blue-700' : 'text-gray-600'}`}>
                          {step.result}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Results Metrics */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {selectedDemo.metrics.map((metric, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-green-600 mb-1">{metric.value}</div>
                  <div className="text-sm text-gray-600 mb-1">{metric.label}</div>
                  <div className="text-sm font-medium text-green-600">{metric.change}</div>
                </div>
              ))}
            </div>

            {/* CTA */}
            <div className="text-center">
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openLeadCapture'));
                }}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200 flex items-center justify-center mx-auto"
              >
                {selectedDemo.cta}
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          </div>
        )}

        {/* Call to Action */}
        {!selectedScenario && (
          <div className="text-center">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
              <h3 className="text-2xl font-bold mb-4">
                Ready to See Your Industry in Action?
              </h3>
              <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
                Choose a demo scenario above to experience how Unitasa transforms business processes with AI automation.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => setSelectedScenario(relevantScenarios[0]?.id || null)}
                  className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
                >
                  Start Demo
                </button>
                <button
                  onClick={() => {
                    window.dispatchEvent(new CustomEvent('openLeadCapture'));
                  }}
                  className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
                >
                  Get Free Assessment
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default InteractiveDemo;