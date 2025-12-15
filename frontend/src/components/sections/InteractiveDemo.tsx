import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Zap, Target, TrendingUp, Users, MessageSquare, Image, Hash, BarChart3, CheckCircle } from 'lucide-react';

export {};

interface DemoScenario {
  id: string;
  title: string;
  description: string;
  industry: string;
  challenge: string;
  steps: DemoStep[];
  results: DemoResult[];
}

interface DemoStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  duration: number; // in seconds
  status: 'pending' | 'active' | 'completed';
}

interface DemoResult {
  metric: string;
  value: string;
  icon: React.ReactNode;
}

const InteractiveDemo: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState<string>('tech-startup');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const demoScenarios: Record<string, DemoScenario> = {
    'tech-startup': {
      id: 'tech-startup',
      title: 'Tech Startup Growth',
      description: 'AI-powered marketing automation for a SaaS company',
      industry: 'Technology',
      challenge: 'Struggling with consistent lead generation and brand awareness',
      steps: [
        {
          id: 'analyze',
          title: 'AI Analysis',
          description: 'Analyzing your industry, competitors, and target audience',
          icon: <BarChart3 className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        },
        {
          id: 'content',
          title: 'Content Creation',
          description: 'Generating viral content and social media posts',
          icon: <MessageSquare className="w-5 h-5" />,
          duration: 4,
          status: 'pending'
        },
        {
          id: 'hashtags',
          title: 'Smart Hashtags',
          description: 'AI-curated hashtags for maximum reach and engagement',
          icon: <Hash className="w-5 h-5" />,
          duration: 2,
          status: 'pending'
        },
        {
          id: 'images',
          title: 'Image Optimization',
          description: 'Creating and optimizing visuals for social platforms',
          icon: <Image className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        },
        {
          id: 'posting',
          title: 'Automated Posting',
          description: 'Strategic scheduling and posting across all platforms',
          icon: <Zap className="w-5 h-5" />,
          duration: 2,
          status: 'pending'
        },
        {
          id: 'engagement',
          title: 'Engagement Optimization',
          description: 'Real-time engagement and conversation management',
          icon: <Users className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        }
      ],
      results: [
        { metric: 'Content Generated', value: '50 posts/week', icon: <MessageSquare className="w-4 h-4" /> },
        { metric: 'Reach Increase', value: '300%', icon: <TrendingUp className="w-4 h-4" /> },
        { metric: 'Lead Generation', value: '5x more', icon: <Target className="w-4 h-4" /> },
        { metric: 'Time Saved', value: '15 hours/week', icon: <Zap className="w-4 h-4" /> }
      ]
    },
    'healthcare': {
      id: 'healthcare',
      title: 'Healthcare Practice Growth',
      description: 'Patient engagement and reputation management',
      industry: 'Healthcare',
      challenge: 'Building trust and patient engagement online',
      steps: [
        {
          id: 'analyze',
          title: 'Patient Analysis',
          description: 'Understanding patient demographics and healthcare needs',
          icon: <BarChart3 className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        },
        {
          id: 'education',
          title: 'Health Education',
          description: 'Creating informative content about health topics',
          icon: <MessageSquare className="w-5 h-5" />,
          duration: 4,
          status: 'pending'
        },
        {
          id: 'compliance',
          title: 'Compliance Check',
          description: 'Ensuring all content meets healthcare regulations',
          icon: <Target className="w-5 h-5" />,
          duration: 2,
          status: 'pending'
        },
        {
          id: 'community',
          title: 'Community Building',
          description: 'Building patient community and support groups',
          icon: <Users className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        },
        {
          id: 'reviews',
          title: 'Review Management',
          description: 'Monitoring and responding to patient reviews',
          icon: <TrendingUp className="w-5 h-5" />,
          duration: 2,
          status: 'pending'
        }
      ],
      results: [
        { metric: 'Patient Engagement', value: '250% increase', icon: <Users className="w-4 h-4" /> },
        { metric: 'Review Rating', value: '4.8/5 stars', icon: <TrendingUp className="w-4 h-4" /> },
        { metric: 'New Patients', value: '40% more', icon: <Target className="w-4 h-4" /> },
        { metric: 'Response Time', value: '< 1 hour', icon: <Zap className="w-4 h-4" /> }
      ]
    },
    'ecommerce': {
      id: 'ecommerce',
      title: 'E-commerce Sales Boost',
      description: 'Product promotion and customer acquisition',
      industry: 'Retail',
      challenge: 'Driving product sales and customer loyalty',
      steps: [
        {
          id: 'analyze',
          title: 'Market Analysis',
          description: 'Analyzing product trends and customer preferences',
          icon: <BarChart3 className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        },
        {
          id: 'product',
          title: 'Product Content',
          description: 'Creating compelling product descriptions and features',
          icon: <MessageSquare className="w-5 h-5" />,
          duration: 4,
          status: 'pending'
        },
        {
          id: 'visuals',
          title: 'Visual Marketing',
          description: 'Generating product images and promotional graphics',
          icon: <Image className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        },
        {
          id: 'campaigns',
          title: 'Campaign Creation',
          description: 'Designing targeted marketing campaigns',
          icon: <Target className="w-5 h-5" />,
          duration: 3,
          status: 'pending'
        },
        {
          id: 'automation',
          title: 'Sales Automation',
          description: 'Automated customer nurturing and follow-ups',
          icon: <Zap className="w-5 h-5" />,
          duration: 2,
          status: 'pending'
        }
      ],
      results: [
        { metric: 'Sales Conversion', value: '180% increase', icon: <TrendingUp className="w-4 h-4" /> },
        { metric: 'Customer Acquisition', value: '3x faster', icon: <Target className="w-4 h-4" /> },
        { metric: 'Marketing ROI', value: '5x return', icon: <BarChart3 className="w-4 h-4" /> },
        { metric: 'Time to Sale', value: '60% faster', icon: <Zap className="w-4 h-4" /> }
      ]
    }
  };

  const currentScenario = demoScenarios[selectedScenario];

  // Auto-play functionality
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isPlaying && currentStep < currentScenario.steps.length) {
      const stepDuration = currentScenario.steps[currentStep].duration * 1000; // Convert to milliseconds
      const progressInterval = 50; // Update progress every 50ms
      const totalUpdates = stepDuration / progressInterval;
      let currentUpdate = 0;

      interval = setInterval(() => {
        currentUpdate++;
        const stepProgress = (currentUpdate / totalUpdates) * 100;
        setProgress(stepProgress);

        if (currentUpdate >= totalUpdates) {
          // Move to next step
          setCurrentStep(prev => {
            const nextStep = prev + 1;
            if (nextStep >= currentScenario.steps.length) {
              setIsPlaying(false);
              setProgress(100);
              return prev;
            }
            return nextStep;
          });
          setProgress(0);
        }
      }, progressInterval);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, currentStep, currentScenario.steps]);

  const handlePlay = () => {
    if (currentStep >= currentScenario.steps.length) {
      // Reset demo
      setCurrentStep(0);
      setProgress(0);
    }
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentStep(0);
    setProgress(0);
  };

  const handleScenarioChange = (scenarioId: string) => {
    setSelectedScenario(scenarioId);
    setIsPlaying(false);
    setCurrentStep(0);
    setProgress(0);
  };

  return (
    <section className="py-20 bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-indigo-100 text-indigo-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Play className="w-4 h-4 mr-2" />
            Interactive Demo
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            See Unitasa AI Agents in Action
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Experience how our AI agents analyze, learn, and execute marketing strategies in real-time.
            Choose a scenario and watch the magic happen.
          </p>
        </div>

        {/* Scenario Selector */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {Object.values(demoScenarios).map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => handleScenarioChange(scenario.id)}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                selectedScenario === scenario.id
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 border border-gray-200 hover:border-indigo-300 hover:shadow-md'
              }`}
            >
              {scenario.title}
            </button>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Demo Visualization */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold text-gray-900">{currentScenario.title}</h3>
                <p className="text-gray-600">{currentScenario.description}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handlePlay}
                  className="p-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  disabled={currentStep >= currentScenario.steps.length && !isPlaying}
                >
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                </button>
                <button
                  onClick={handleReset}
                  className="p-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  <RotateCcw className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Challenge Display */}
            <div className="bg-red-50 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-red-800 mb-2">Challenge:</h4>
              <p className="text-red-700">{currentScenario.challenge}</p>
            </div>

            {/* Steps Visualization */}
            <div className="space-y-4">
              {currentScenario.steps.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex items-center p-4 rounded-lg border transition-all duration-300 ${
                    index === currentStep && isPlaying
                      ? 'bg-indigo-50 border-indigo-200 shadow-md'
                      : index < currentStep
                      ? 'bg-green-50 border-green-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className={`p-2 rounded-lg mr-4 ${
                    index === currentStep && isPlaying
                      ? 'bg-indigo-100 text-indigo-600'
                      : index < currentStep
                      ? 'bg-green-100 text-green-600'
                      : 'bg-gray-100 text-gray-400'
                  }`}>
                    {step.icon}
                  </div>
                  <div className="flex-1">
                    <h4 className={`font-semibold ${
                      index === currentStep && isPlaying
                        ? 'text-indigo-900'
                        : index < currentStep
                        ? 'text-green-900'
                        : 'text-gray-900'
                    }`}>
                      {step.title}
                    </h4>
                    <p className={`text-sm ${
                      index === currentStep && isPlaying
                        ? 'text-indigo-700'
                        : index < currentStep
                        ? 'text-green-700'
                        : 'text-gray-600'
                    }`}>
                      {step.description}
                    </p>
                  </div>
                  {index === currentStep && isPlaying && (
                    <div className="ml-4">
                      <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                  )}
                  {index < currentStep && (
                    <div className="ml-4">
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-white" />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Progress Bar */}
            <div className="mt-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span>{Math.round((currentStep / currentScenario.steps.length) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${currentStep >= currentScenario.steps.length ? 100 : ((currentStep + (progress / 100)) / currentScenario.steps.length) * 100}%`
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div className="space-y-6">
            {currentStep >= currentScenario.steps.length ? (
              <>
                {/* Completion Message */}
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-8 text-white text-center">
                  <div className="text-6xl mb-4">🎉</div>
                  <h3 className="text-2xl font-bold mb-2">Demo Complete!</h3>
                  <p className="text-green-100">
                    Watch how Unitasa AI agents transformed this business challenge into measurable results.
                  </p>
                </div>

                {/* Results */}
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                  <h4 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                    <TrendingUp className="w-6 h-6 mr-3 text-green-600" />
                    Results Achieved
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    {currentScenario.results.map((result, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4 text-center">
                        <div className="text-green-600 mb-2">{result.icon}</div>
                        <div className="font-bold text-gray-900 text-lg">{result.value}</div>
                        <div className="text-sm text-gray-600">{result.metric}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* Current Step Details */}
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                  <h4 className="text-xl font-bold text-gray-900 mb-4">What's Happening Now</h4>
                  {currentStep < currentScenario.steps.length ? (
                    <div className="flex items-start">
                      <div className="p-3 bg-indigo-100 text-indigo-600 rounded-lg mr-4">
                        {currentScenario.steps[currentStep].icon}
                      </div>
                      <div>
                        <h5 className="font-semibold text-gray-900 mb-1">
                          {currentScenario.steps[currentStep].title}
                        </h5>
                        <p className="text-gray-600 text-sm">
                          {currentScenario.steps[currentStep].description}
                        </p>
                        {isPlaying && (
                          <div className="mt-3">
                            <div className="text-xs text-gray-500 mb-1">Processing...</div>
                            <div className="w-full bg-gray-200 rounded-full h-1">
                              <div
                                className="bg-indigo-600 h-1 rounded-full transition-all duration-300"
                                style={{ width: `${progress}%` }}
                              ></div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-600">Click play to start the demo!</p>
                  )}
                </div>

                {/* Preview of Results */}
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-6 border border-indigo-200">
                  <h4 className="text-lg font-bold text-gray-900 mb-4">Expected Results</h4>
                  <div className="space-y-3">
                    {currentScenario.results.slice(0, 2).map((result, index) => (
                      <div key={index} className="flex items-center">
                        <div className="text-indigo-600 mr-3">{result.icon}</div>
                        <div>
                          <div className="font-semibold text-gray-900">{result.value}</div>
                          <div className="text-sm text-gray-600">{result.metric}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="text-sm text-gray-500 mt-4">
                    Complete the demo to see all results and how Unitasa achieves them.
                  </p>
                </div>
              </>
            )}

            {/* Call to Action */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 text-center">
              <h4 className="text-lg font-bold text-gray-900 mb-2">Ready to Get These Results?</h4>
              <p className="text-gray-600 mb-4">
                Experience the power of AI-driven marketing automation for your business.
              </p>
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }}
                className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
              >
                Get Your Free AI Assessment
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default InteractiveDemo;