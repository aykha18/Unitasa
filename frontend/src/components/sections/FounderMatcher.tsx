import React, { useState, useEffect } from 'react';
import { Users, TrendingUp, Award, Star, ArrowRight, CheckCircle } from 'lucide-react';
import { useIndustryDetection } from '../../hooks/useIndustryDetection';

interface FounderStory {
  id: string;
  founder: {
    name: string;
    title: string;
    company: string;
    avatar: string;
  };
  industry: string;
  companySize: 'startup' | 'small' | 'medium' | 'large';
  challenge: string;
  solution: string;
  metrics: {
    label: string;
    value: string;
    change: string;
  }[];
  testimonial: string;
  credibilityScore: number; // 1-5 stars
}

const FounderMatcher: React.FC = () => {
  const { industry: detectedIndustry } = useIndustryDetection();
  const [selectedStory, setSelectedStory] = useState<FounderStory | null>(null);
  const [matchedStories, setMatchedStories] = useState<FounderStory[]>([]);

  const founderStories: FounderStory[] = [
    {
      id: 'sarah-saas',
      founder: {
        name: 'Sarah Chen',
        title: 'CEO & Founder',
        company: 'TechFlow',
        avatar: '👩‍💼'
      },
      industry: 'saas',
      companySize: 'startup',
      challenge: 'Struggling with consistent lead generation and customer acquisition in a competitive SaaS market',
      solution: 'Unitasa AI agents handle all social media content, lead nurturing, and competitive analysis',
      metrics: [
        { label: 'Monthly Leads', value: '300', change: '+180%' },
        { label: 'CAC Reduction', value: '45%', change: '-60%' },
        { label: 'Conversion Rate', value: '4.2%', change: '+120%' }
      ],
      testimonial: 'Unitasa transformed our marketing from a cost center into our biggest growth driver. The AI agents work 24/7, creating content that actually converts.',
      credibilityScore: 5
    },
    {
      id: 'marcus-healthcare',
      founder: {
        name: 'Marcus Rodriguez',
        title: 'Medical Director',
        company: 'HealthFirst',
        avatar: '👨‍⚕️'
      },
      industry: 'healthcare',
      companySize: 'small',
      challenge: 'Building patient trust and engagement in a highly regulated healthcare environment',
      solution: 'Specialized AI agents for healthcare content with compliance monitoring and patient engagement',
      metrics: [
        { label: 'Patient Engagement', value: '250%', change: '+150%' },
        { label: 'Review Rating', value: '4.8/5', change: '+0.6 stars' },
        { label: 'New Patients', value: '40%', change: '+180%' }
      ],
      testimonial: 'In healthcare, trust is everything. Unitasa\'s AI agents maintain our professional voice while engaging patients 24/7.',
      credibilityScore: 5
    },
    {
      id: 'priya-finance',
      founder: {
        name: 'Priya Patel',
        title: 'Managing Partner',
        company: 'FinSecure',
        avatar: '👩‍💻'
      },
      industry: 'finance',
      companySize: 'medium',
      challenge: 'Complex financial content creation with strict regulatory compliance requirements',
      solution: 'AI-powered financial content creation with built-in compliance checks and risk monitoring',
      metrics: [
        { label: 'Content Quality Score', value: '95%', change: '+25%' },
        { label: 'Client Acquisition', value: '150%', change: '+200%' },
        { label: 'Compliance Accuracy', value: '100%', change: 'Zero violations' }
      ],
      testimonial: 'Regulatory compliance is non-negotiable in finance. Unitasa\'s AI agents create compliant content faster than our team ever could.',
      credibilityScore: 5
    },
    {
      id: 'david-ecommerce',
      founder: {
        name: 'David Kim',
        title: 'Founder & CEO',
        company: 'RetailPlus',
        avatar: '👨‍💼'
      },
      industry: 'ecommerce',
      companySize: 'small',
      challenge: 'Limited marketing budget and time for customer engagement in competitive e-commerce space',
      solution: 'Cost-effective AI marketing automation tailored for small retail businesses',
      metrics: [
        { label: 'Customer Engagement', value: '400%', change: '+300%' },
        { label: 'Marketing ROI', value: '5x', change: '+400%' },
        { label: 'Monthly Savings', value: '$2,500', change: '70% reduction' }
      ],
      testimonial: 'As a small retail business, we couldn\'t afford expensive marketing agencies. Unitasa gives us enterprise-level AI marketing at a price we can actually afford.',
      credibilityScore: 4
    },
    {
      id: 'emma-consulting',
      founder: {
        name: 'Emma Thompson',
        title: 'Partner',
        company: 'ConsultCo',
        avatar: '👩‍🎓'
      },
      industry: 'consulting',
      companySize: 'medium',
      challenge: 'Establishing thought leadership and maintaining client relationships at scale',
      solution: 'AI-powered thought leadership content and automated client relationship management',
      metrics: [
        { label: 'Thought Leadership Reach', value: '10x', change: '+900%' },
        { label: 'Client Retention', value: '85%', change: '+15%' },
        { label: 'Lead Quality Score', value: '8.5/10', change: '+70%' }
      ],
      testimonial: 'Unitasa has elevated our firm\'s thought leadership presence dramatically. The AI agents create insightful content that positions us as industry experts.',
      credibilityScore: 4
    }
  ];

  // Match stories based on detected industry
  useEffect(() => {
    let filteredStories = founderStories;

    // Primary filter: exact industry match
    const exactMatches = founderStories.filter(story => story.industry === detectedIndustry);
    if (exactMatches.length > 0) {
      filteredStories = exactMatches;
    } else {
      // Secondary filter: related industries
      const relatedIndustries: Record<string, string[]> = {
        saas: ['consulting', 'finance'],
        ecommerce: ['consulting', 'saas'],
        consulting: ['saas', 'finance'],
        healthcare: ['consulting'],
        finance: ['consulting', 'saas'],
        education: ['consulting'],
        other: ['saas', 'consulting']
      };

      const related = relatedIndustries[detectedIndustry] || ['saas'];
      filteredStories = founderStories.filter(story => related.includes(story.industry));
    }

    // Sort by credibility score and limit to top 3
    const sortedStories = filteredStories
      .sort((a, b) => b.credibilityScore - a.credibilityScore)
      .slice(0, 3);

    setMatchedStories(sortedStories);
    setSelectedStory(sortedStories[0] || null);
  }, [detectedIndustry]);

  const renderStars = (score: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < score ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  if (!selectedStory) {
    return (
      <section className="py-20 bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto mb-8"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-20 bg-gradient-to-br from-purple-50 to-pink-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-purple-100 text-purple-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Users className="w-4 h-4 mr-2" />
            Founder Stories
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Success Stories from Founders Like You
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See how other founders in your industry transformed their businesses with Unitasa's AI marketing automation.
          </p>
        </div>

        {/* Featured Story */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-12">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center">
              <div className="text-4xl mr-4">{selectedStory.founder.avatar}</div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">{selectedStory.founder.name}</h3>
                <p className="text-gray-600">{selectedStory.founder.title} • {selectedStory.founder.company}</p>
                <div className="flex items-center mt-2">
                  {renderStars(selectedStory.credibilityScore)}
                  <span className="ml-2 text-sm text-gray-600">Verified Success</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                selectedStory.companySize === 'startup' ? 'bg-green-100 text-green-800' :
                selectedStory.companySize === 'small' ? 'bg-blue-100 text-blue-800' :
                selectedStory.companySize === 'medium' ? 'bg-purple-100 text-purple-800' :
                'bg-orange-100 text-orange-800'
              }`}>
                {selectedStory.companySize.charAt(0).toUpperCase() + selectedStory.companySize.slice(1)} Business
              </span>
            </div>
          </div>

          {/* Challenge & Solution */}
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h4 className="font-semibold text-red-800 mb-3 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Challenge
              </h4>
              <p className="text-red-700">{selectedStory.challenge}</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h4 className="font-semibold text-green-800 mb-3 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Solution
              </h4>
              <p className="text-green-700">{selectedStory.solution}</p>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {selectedStory.metrics.map((metric, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">{metric.value}</div>
                <div className="text-sm text-gray-600 mb-1">{metric.label}</div>
                <div className="text-sm font-medium text-green-600">{metric.change}</div>
              </div>
            ))}
          </div>

          {/* Testimonial */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
            <div className="flex items-start">
              <div className="text-purple-600 mr-3 mt-1">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,17H17L19,13V7H13V13H16M6,17H9L11,13V7H5V13H8L6,17Z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-gray-700 italic text-lg mb-4">"{selectedStory.testimonial}"</p>
                <div className="flex items-center">
                  <span className="font-semibold text-gray-900">— {selectedStory.founder.name}</span>
                  <span className="mx-2 text-gray-400">•</span>
                  <span className="text-gray-600">{selectedStory.founder.company}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Story Selector */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {matchedStories.map((story) => (
            <button
              key={story.id}
              onClick={() => setSelectedStory(story)}
              className={`p-6 rounded-xl border-2 transition-all ${
                selectedStory.id === story.id
                  ? 'border-purple-500 bg-purple-50 shadow-md'
                  : 'border-gray-200 hover:border-purple-300 bg-white hover:shadow-md'
              }`}
            >
              <div className="text-center">
                <div className="text-3xl mb-3">{story.founder.avatar}</div>
                <h4 className="font-semibold text-gray-900 mb-1">{story.founder.name}</h4>
                <p className="text-sm text-gray-600 mb-2">{story.founder.company}</p>
                <div className="flex justify-center mb-2">
                  {renderStars(story.credibilityScore)}
                </div>
                <div className="text-xs text-purple-600 font-medium">
                  {story.metrics[0].change} {story.metrics[0].label.toLowerCase()}
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Ready to Join These Success Stories?
            </h3>
            <p className="text-purple-100 mb-6 max-w-2xl mx-auto">
              Start your free AI marketing assessment and see how Unitasa can transform your business results.
            </p>
            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openAssessment'));
              }}
              className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors flex items-center justify-center mx-auto"
            >
              Get Your Free Assessment
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FounderMatcher;