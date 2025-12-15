import React, { useState } from 'react';
import { Star, Quote, TrendingUp, Users, Award, CheckCircle, ArrowRight, Play } from 'lucide-react';

export {};

interface SuccessStory {
  id: string;
  founder: {
    name: string;
    title: string;
    company: string;
    avatar: string;
  };
  industry: string;
  challenge: string;
  solution: string;
  metrics: {
    label: string;
    value: string;
    change: string;
    timeframe: string;
  }[];
  testimonial: string;
  featured: boolean;
  videoUrl?: string;
}

const EnhancedSocialProof: React.FC = () => {
  const [selectedStory, setSelectedStory] = useState<string | null>(null);

  const successStories: SuccessStory[] = [
    {
      id: 'sarah-chen',
      founder: {
        name: 'Sarah Chen',
        title: 'CEO & Founder',
        company: 'TechFlow',
        avatar: '👩‍💼'
      },
      industry: 'Technology',
      challenge: 'Struggling with consistent content creation and lead generation in a competitive SaaS market',
      solution: 'Unitasa AI agents handle all social media content, lead nurturing, and competitive analysis',
      metrics: [
        { label: 'Monthly Leads', value: '300', change: '+180%', timeframe: '6 months' },
        { label: 'Content Output', value: '50 posts/week', change: '10x increase', timeframe: '3 months' },
        { label: 'Cost Savings', value: '$8,000/mo', change: '65% reduction', timeframe: 'Ongoing' },
        { label: 'Conversion Rate', value: '4.2%', change: '+120%', timeframe: '6 months' }
      ],
      testimonial: 'Unitasa transformed our marketing from a cost center into our biggest growth driver. The AI agents work 24/7, creating content that actually converts while saving us thousands monthly.',
      featured: true,
      videoUrl: '#'
    },
    {
      id: 'marcus-rodriguez',
      founder: {
        name: 'Marcus Rodriguez',
        title: 'Medical Director',
        company: 'HealthFirst',
        avatar: '👨‍⚕️'
      },
      industry: 'Healthcare',
      challenge: 'Building patient trust and engagement in a highly regulated healthcare environment',
      solution: 'Specialized AI agents for healthcare content with compliance monitoring and patient engagement',
      metrics: [
        { label: 'Patient Engagement', value: '250%', change: '+150%', timeframe: '4 months' },
        { label: 'Review Rating', value: '4.8/5', change: '+0.6 stars', timeframe: '6 months' },
        { label: 'New Patients', value: '40%', change: '+180%', timeframe: '5 months' },
        { label: 'Response Time', value: '< 1 hour', change: '95% faster', timeframe: 'Immediate' }
      ],
      testimonial: 'In healthcare, trust is everything. Unitasa\'s AI agents maintain our professional voice while engaging patients 24/7. Our patient satisfaction scores have never been higher.',
      featured: true,
      videoUrl: '#'
    },
    {
      id: 'priya-patel',
      founder: {
        name: 'Priya Patel',
        title: 'Managing Partner',
        company: 'FinSecure',
        avatar: '👩‍💻'
      },
      industry: 'Finance',
      challenge: 'Complex financial content creation with strict regulatory compliance requirements',
      solution: 'AI-powered financial content creation with built-in compliance checks and risk monitoring',
      metrics: [
        { label: 'Content Quality Score', value: '95%', change: '+25%', timeframe: 'Immediate' },
        { label: 'Client Acquisition', value: '150%', change: '+200%', timeframe: '5 months' },
        { label: 'Compliance Accuracy', value: '100%', change: 'Zero violations', timeframe: '6 months' },
        { label: 'Time to Publish', value: '2 hours', change: '80% faster', timeframe: '3 months' }
      ],
      testimonial: 'Regulatory compliance is non-negotiable in finance. Unitasa\'s AI agents create compliant content faster than our team ever could, while maintaining the expertise our clients expect.',
      featured: true,
      videoUrl: '#'
    },
    {
      id: 'david-kim',
      founder: {
        name: 'David Kim',
        title: 'Founder & CEO',
        company: 'RetailPlus',
        avatar: '👨‍💼'
      },
      industry: 'Retail',
      challenge: 'Limited marketing budget and time for customer engagement in competitive e-commerce space',
      solution: 'Cost-effective AI marketing automation tailored for small retail businesses',
      metrics: [
        { label: 'Customer Engagement', value: '400%', change: '+300%', timeframe: '3 months' },
        { label: 'Marketing ROI', value: '5x', change: '+400%', timeframe: '6 months' },
        { label: 'Monthly Savings', value: '$2,500', change: '70% reduction', timeframe: 'Ongoing' },
        { label: 'Conversion Rate', value: '3.8%', change: '+180%', timeframe: '4 months' }
      ],
      testimonial: 'As a small retail business, we couldn\'t afford expensive marketing agencies. Unitasa gives us enterprise-level AI marketing at a price we can actually afford.',
      featured: false,
      videoUrl: '#'
    },
    {
      id: 'emma-thompson',
      founder: {
        name: 'Emma Thompson',
        title: 'Partner',
        company: 'ConsultCo',
        avatar: '👩‍🎓'
      },
      industry: 'Consulting',
      challenge: 'Establishing thought leadership and maintaining client relationships at scale',
      solution: 'AI-powered thought leadership content and automated client relationship management',
      metrics: [
        { label: 'Thought Leadership Reach', value: '10x', change: '+900%', timeframe: '4 months' },
        { label: 'Client Retention', value: '85%', change: '+15%', timeframe: '6 months' },
        { label: 'Lead Quality Score', value: '8.5/10', change: '+70%', timeframe: '3 months' },
        { label: 'Content Output', value: '25 articles/mo', change: '5x increase', timeframe: '3 months' }
      ],
      testimonial: 'Unitasa has elevated our firm\'s thought leadership presence dramatically. The AI agents create insightful content that positions us as industry experts while nurturing our client relationships.',
      featured: false,
      videoUrl: '#'
    }
  ];

  const featuredStories = successStories.filter(story => story.featured);
  const otherStories = successStories.filter(story => !story.featured);

  return (
    <section className="py-20 bg-gradient-to-br from-green-50 via-white to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Award className="w-4 h-4 mr-2" />
            Success Stories
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Real Founders, Real Results
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join 25+ founders who transformed their businesses with Unitasa's AI marketing automation.
            These are their stories.
          </p>
        </div>

        {/* Featured Stories */}
        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          {featuredStories.map((story) => (
            <div key={story.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              {/* Story Header */}
              <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-6 text-white">
                <div className="flex items-center mb-4">
                  <div className="text-4xl mr-4">{story.founder.avatar}</div>
                  <div>
                    <h3 className="text-xl font-bold">{story.founder.name}</h3>
                    <p className="text-green-100">{story.founder.title}</p>
                    <p className="text-green-100 font-medium">{story.founder.company}</p>
                  </div>
                </div>
                <div className="inline-flex items-center bg-white/20 px-3 py-1 rounded-full text-sm">
                  <Star className="w-4 h-4 mr-1" />
                  Featured Success Story
                </div>
              </div>

              {/* Story Content */}
              <div className="p-6">
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Challenge:</h4>
                  <p className="text-gray-600 text-sm">{story.challenge}</p>
                </div>

                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-2">Solution:</h4>
                  <p className="text-gray-600 text-sm">{story.solution}</p>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-3 mb-6">
                  {story.metrics.slice(0, 4).map((metric, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-3 text-center">
                      <div className="text-lg font-bold text-green-600">{metric.value}</div>
                      <div className="text-xs text-gray-600 mb-1">{metric.label}</div>
                      <div className="text-xs font-medium text-green-500">{metric.change}</div>
                    </div>
                  ))}
                </div>

                {/* Testimonial */}
                <div className="bg-blue-50 rounded-lg p-4 mb-4">
                  <Quote className="w-6 h-6 text-blue-500 mb-2" />
                  <p className="text-gray-700 text-sm italic">"{story.testimonial}"</p>
                </div>

                {/* Video CTA */}
                {story.videoUrl && (
                  <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center">
                    <Play className="w-4 h-4 mr-2" />
                    Watch Full Story
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Other Stories Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {otherStories.map((story) => (
            <div key={story.id} className="bg-white rounded-xl shadow-md border border-gray-100 p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start mb-4">
                <div className="text-3xl mr-4">{story.founder.avatar}</div>
                <div className="flex-1">
                  <h4 className="font-bold text-gray-900">{story.founder.name}</h4>
                  <p className="text-sm text-gray-600">{story.founder.title} • {story.founder.company}</p>
                  <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mt-1">
                    {story.industry}
                  </span>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-gray-700 text-sm mb-3">"{story.testimonial}"</p>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                {story.metrics.slice(0, 2).map((metric, index) => (
                  <div key={index} className="text-center">
                    <div className="font-bold text-green-600">{metric.value}</div>
                    <div className="text-xs text-gray-600">{metric.label}</div>
                    <div className="text-xs text-green-500">{metric.change}</div>
                  </div>
                ))}
              </div>

              <button
                onClick={() => setSelectedStory(selectedStory === story.id ? null : story.id)}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
              >
                {selectedStory === story.id ? 'Show Less' : 'Read Full Story'}
                <ArrowRight className={`w-4 h-4 ml-2 transition-transform ${selectedStory === story.id ? 'rotate-90' : ''}`} />
              </button>

              {selectedStory === story.id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="mb-3">
                    <h5 className="font-semibold text-gray-900 mb-1">Challenge:</h5>
                    <p className="text-sm text-gray-600">{story.challenge}</p>
                  </div>
                  <div className="mb-3">
                    <h5 className="font-semibold text-gray-900 mb-1">Solution:</h5>
                    <p className="text-sm text-gray-600">{story.solution}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {story.metrics.map((metric, index) => (
                      <div key={index} className="bg-gray-50 rounded p-2 text-center">
                        <div className="font-bold text-green-600 text-sm">{metric.value}</div>
                        <div className="text-xs text-gray-600">{metric.label}</div>
                        <div className="text-xs text-green-500">{metric.change}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Trust Indicators */}
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 text-center">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="text-3xl font-bold text-green-600 mb-2">25+</div>
              <div className="text-gray-600">Founders Using Unitasa</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600 mb-2">$2M+</div>
              <div className="text-gray-600">Revenue Generated</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600 mb-2">300%</div>
              <div className="text-gray-600">Average ROI Increase</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600 mb-2">24/7</div>
              <div className="text-gray-600">AI Support Available</div>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Join These Success Stories?
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Start your free AI marketing assessment and see how Unitasa can transform your business results.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }}
                className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
              >
                Get Your Free Assessment
              </button>
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openDemo'));
                }}
                className="border-2 border-green-600 text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition-all duration-200"
              >
                See Live Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default EnhancedSocialProof;