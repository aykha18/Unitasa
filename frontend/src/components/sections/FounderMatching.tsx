import React, { useState, useEffect } from 'react';
import { Users, Target, TrendingUp, Award, Star, CheckCircle, ArrowRight } from 'lucide-react';

export {};

interface FounderProfile {
  id: string;
  name: string;
  company: string;
  industry: string;
  companySize: string;
  challenge: string;
  solution: string;
  results: {
    metric: string;
    value: string;
    timeframe: string;
  }[];
  avatar: string;
  matchScore: number;
}

interface UserProfile {
  industry: string;
  companySize: string;
  challenges: string[];
}

const FounderMatching: React.FC = () => {
  const [userProfile, setUserProfile] = useState<UserProfile>({
    industry: '',
    companySize: '',
    challenges: []
  });

  const [matchedFounders, setMatchedFounders] = useState<FounderProfile[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);

  // Sample founder database - in real app this would come from API
  const founderDatabase: FounderProfile[] = [
    {
      id: '1',
      name: 'Sarah Chen',
      company: 'TechFlow',
      industry: 'technology',
      companySize: '25-50',
      challenge: 'Struggling with consistent content creation and lead generation',
      solution: 'Unitasa AI agents handle all social media content and lead nurturing',
      results: [
        { metric: 'Lead Generation', value: '300%', timeframe: '6 months' },
        { metric: 'Content Output', value: '10x increase', timeframe: '3 months' },
        { metric: 'Cost Savings', value: '$8,000/mo', timeframe: 'Ongoing' }
      ],
      avatar: '👩‍💼',
      matchScore: 0
    },
    {
      id: '2',
      name: 'Marcus Rodriguez',
      company: 'HealthFirst',
      industry: 'healthcare',
      companySize: '11-25',
      challenge: 'Manual patient engagement and brand awareness challenges',
      solution: 'AI-powered content strategy and automated social media management',
      results: [
        { metric: 'Patient Engagement', value: '250% increase', timeframe: '4 months' },
        { metric: 'Brand Awareness', value: '180% growth', timeframe: '6 months' },
        { metric: 'Time Saved', value: '20 hours/week', timeframe: 'Ongoing' }
      ],
      avatar: '👨‍⚕️',
      matchScore: 0
    },
    {
      id: '3',
      name: 'Priya Patel',
      company: 'FinSecure',
      industry: 'finance',
      companySize: '51-100',
      challenge: 'Complex financial content creation and regulatory compliance',
      solution: 'Specialized AI agents for financial content with compliance checks',
      results: [
        { metric: 'Content Quality', value: '95% accuracy', timeframe: 'Immediate' },
        { metric: 'Client Acquisition', value: '150% increase', timeframe: '5 months' },
        { metric: 'Compliance Time', value: '80% reduction', timeframe: '3 months' }
      ],
      avatar: '👩‍💻',
      matchScore: 0
    },
    {
      id: '4',
      name: 'David Kim',
      company: 'RetailPlus',
      industry: 'retail',
      companySize: '1-10',
      challenge: 'Limited marketing budget and time for customer engagement',
      solution: 'Cost-effective AI marketing automation for small businesses',
      results: [
        { metric: 'Customer Engagement', value: '400% increase', timeframe: '3 months' },
        { metric: 'Marketing ROI', value: '5x return', timeframe: '6 months' },
        { metric: 'Monthly Savings', value: '$2,500', timeframe: 'Ongoing' }
      ],
      avatar: '👨‍💼',
      matchScore: 0
    },
    {
      id: '5',
      name: 'Emma Thompson',
      company: 'ConsultCo',
      industry: 'consulting',
      companySize: '25-50',
      challenge: 'Thought leadership content and client relationship management',
      solution: 'AI-powered thought leadership and automated client nurturing',
      results: [
        { metric: 'Thought Leadership Reach', value: '10x increase', timeframe: '4 months' },
        { metric: 'Client Retention', value: '85% improvement', timeframe: '6 months' },
        { metric: 'Lead Quality', value: '200% better', timeframe: '3 months' }
      ],
      avatar: '👩‍🎓',
      matchScore: 0
    }
  ];

  const industries = [
    { value: 'technology', label: 'Technology/SaaS' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'finance', label: 'Finance' },
    { value: 'retail', label: 'Retail/E-commerce' },
    { value: 'consulting', label: 'Consulting' },
    { value: 'manufacturing', label: 'Manufacturing' }
  ];

  const companySizes = [
    { value: '1-10', label: '1-10 employees' },
    { value: '11-25', label: '11-25 employees' },
    { value: '25-50', label: '25-50 employees' },
    { value: '51-100', label: '51-100 employees' },
    { value: '100+', label: '100+ employees' }
  ];

  const challenges = [
    'Content creation consistency',
    'Lead generation struggles',
    'Time management issues',
    'Budget constraints',
    'Technical complexity',
    'Measuring ROI',
    'Brand awareness',
    'Customer engagement'
  ];

  const calculateMatches = (profile: UserProfile) => {
    if (!profile.industry || !profile.companySize) return [];

    const matches = founderDatabase.map(founder => {
      let score = 0;

      // Industry match (40% weight)
      if (founder.industry === profile.industry) score += 40;

      // Company size match (30% weight)
      if (founder.companySize === profile.companySize) score += 30;

      // Challenge relevance (30% weight)
      const relevantChallenges = profile.challenges.length;
      if (relevantChallenges > 0) {
        score += (30 / relevantChallenges) * relevantChallenges; // Simplified scoring
      }

      return { ...founder, matchScore: Math.min(100, score) };
    });

    return matches
      .filter(match => match.matchScore >= 50) // Only show good matches
      .sort((a, b) => b.matchScore - a.matchScore)
      .slice(0, 3); // Top 3 matches
  };

  useEffect(() => {
    if (userProfile.industry && userProfile.companySize) {
      setIsCalculating(true);
      // Simulate API call delay
      setTimeout(() => {
        const matches = calculateMatches(userProfile);
        setMatchedFounders(matches);
        setIsCalculating(false);
      }, 1000);
    }
  }, [userProfile]);

  const handleProfileUpdate = (field: keyof UserProfile, value: any) => {
    setUserProfile(prev => ({ ...prev, [field]: value }));
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-blue-600 bg-blue-100';
    return 'text-orange-600 bg-orange-100';
  };

  return (
    <section className="py-20 bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-purple-100 text-purple-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Users className="w-4 h-4 mr-2" />
            Founder Matching
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            See How Founders Like You Succeed with Unitasa
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get matched with successful founders in your industry who faced similar challenges and achieved remarkable results.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Profile Input */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Target className="w-6 h-6 mr-3 text-purple-600" />
              Tell Us About Your Business
            </h3>

            <div className="space-y-6">
              {/* Industry Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <select
                  value={userProfile.industry}
                  onChange={(e) => handleProfileUpdate('industry', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Select your industry</option>
                  {industries.map(industry => (
                    <option key={industry.value} value={industry.value}>
                      {industry.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Company Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Size
                </label>
                <select
                  value={userProfile.companySize}
                  onChange={(e) => handleProfileUpdate('companySize', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Select company size</option>
                  {companySizes.map(size => (
                    <option key={size.value} value={size.value}>
                      {size.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Challenges */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Current Challenges (Select all that apply)
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {challenges.map(challenge => (
                    <label key={challenge} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={userProfile.challenges.includes(challenge)}
                        onChange={(e) => {
                          const newChallenges = e.target.checked
                            ? [...userProfile.challenges, challenge]
                            : userProfile.challenges.filter(c => c !== challenge);
                          handleProfileUpdate('challenges', newChallenges);
                        }}
                        className="mr-2 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="text-sm text-gray-700">{challenge}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div className="space-y-6">
            {isCalculating ? (
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Finding your perfect matches...</p>
                </div>
              </div>
            ) : matchedFounders.length > 0 ? (
              <>
                <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white">
                  <h4 className="text-xl font-bold mb-2">🎯 Perfect Matches Found!</h4>
                  <p className="text-purple-100">
                    These founders faced similar challenges and achieved remarkable results with Unitasa.
                  </p>
                </div>

                {matchedFounders.map((founder, index) => (
                  <div key={founder.id} className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center">
                        <div className="text-3xl mr-4">{founder.avatar}</div>
                        <div>
                          <h4 className="font-bold text-gray-900">{founder.name}</h4>
                          <p className="text-sm text-gray-600">{founder.company} • {industries.find(i => i.value === founder.industry)?.label}</p>
                        </div>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreColor(founder.matchScore)}`}>
                        {founder.matchScore}% Match
                      </div>
                    </div>

                    <div className="mb-4">
                      <h5 className="font-semibold text-gray-900 mb-2">Challenge:</h5>
                      <p className="text-gray-700 text-sm mb-3">{founder.challenge}</p>

                      <h5 className="font-semibold text-gray-900 mb-2">Solution:</h5>
                      <p className="text-gray-700 text-sm">{founder.solution}</p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <TrendingUp className="w-4 h-4 mr-2 text-green-600" />
                        Results Achieved:
                      </h5>
                      <div className="grid grid-cols-1 gap-2">
                        {founder.results.map((result, idx) => (
                          <div key={idx} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">{result.metric}</span>
                            <div className="text-right">
                              <div className="font-bold text-green-600">{result.value}</div>
                              <div className="text-xs text-gray-500">{result.timeframe}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </>
            ) : userProfile.industry && userProfile.companySize ? (
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 text-center">
                <Award className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 mb-2">No Matches Yet</h4>
                <p className="text-gray-600">
                  Try selecting different challenges or check back soon as we add more founder stories.
                </p>
              </div>
            ) : (
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 text-center">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Complete Your Profile</h4>
                <p className="text-gray-600">
                  Fill out your business details above to see how similar founders succeeded with Unitasa.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-12">
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 max-w-2xl mx-auto">
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Ready to Join Successful Founders?
            </h3>
            <p className="text-gray-600 mb-6">
              Get matched with a personalized AI marketing strategy and start seeing results like these founders.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }}
              >
                Get My Free AI Assessment
              </button>
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openDemo'));
                }}
                className="border-2 border-purple-600 text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-all duration-200"
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

export default FounderMatching;