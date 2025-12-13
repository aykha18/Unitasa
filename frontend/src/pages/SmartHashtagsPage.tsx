import React, { useState } from 'react';
import { Sparkles, Hash, Copy, RefreshCw, TrendingUp } from 'lucide-react';
import { Button } from '../components/ui';

const SmartHashtagsPage: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [platform, setPlatform] = useState('twitter');
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // Mock hashtag data - in production this would come from an API
  const mockHashtags = {
    twitter: {
      'marketing': ['#MarketingAutomation', '#DigitalMarketing', '#SaaS', '#B2B', '#MarketingTech', '#GrowthHacking', '#ContentMarketing', '#SocialMedia'],
      'technology': ['#AI', '#MachineLearning', '#TechInnovation', '#Startups', '#FinTech', '#SaaS', '#Automation', '#FutureOfWork'],
      'business': ['#Entrepreneurship', '#BusinessGrowth', '#Leadership', '#Innovation', '#Strategy', '#Success', '#Motivation', '#BusinessTips']
    },
    instagram: {
      'marketing': ['#marketing', '#digitalmarketing', '#socialmediamarketing', '#contentcreator', '#brandstrategy', '#marketingtips', '#businessgrowth'],
      'technology': ['#technology', '#innovation', '#ai', '#startups', '#techlife', '#futuretech', '#digitaltransformation'],
      'business': ['#business', '#entrepreneur', '#success', '#motivation', '#leadership', '#businessowner', '#smallbusiness']
    },
    linkedin: {
      'marketing': ['#Marketing', '#DigitalMarketing', '#B2BMarketing', '#ContentStrategy', '#BrandBuilding', '#MarketingAutomation'],
      'technology': ['#Technology', '#Innovation', '#ArtificialIntelligence', '#DigitalTransformation', '#TechTrends'],
      'business': ['#BusinessStrategy', '#Leadership', '#Entrepreneurship', '#BusinessDevelopment', '#ProfessionalDevelopment']
    }
  };

  const generateHashtags = async () => {
    if (!topic.trim()) return;

    setLoading(true);

    // Simulate API call delay
    setTimeout(() => {
      const topicKey = topic.toLowerCase().includes('market') ? 'marketing' :
                      topic.toLowerCase().includes('tech') ? 'technology' : 'business';

      const platformHashtags = mockHashtags[platform as keyof typeof mockHashtags][topicKey] || [];

      // Add some dynamic hashtags based on the topic
      const dynamicHashtags = [
        `#${topic.replace(/\s+/g, '')}`,
        `#${topic.split(' ')[0]}`,
        `#${platform === 'twitter' ? 'Twitter' : platform === 'instagram' ? 'Instagram' : 'LinkedIn'}Marketing`
      ];

      setHashtags([...platformHashtags, ...dynamicHashtags]);
      setLoading(false);
    }, 1500);
  };

  const copyHashtag = async (hashtag: string, index: number) => {
    try {
      await navigator.clipboard.writeText(hashtag);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy hashtag:', err);
    }
  };

  const copyAllHashtags = async () => {
    try {
      const allHashtags = hashtags.join(' ');
      await navigator.clipboard.writeText(allHashtags);
      alert('All hashtags copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy hashtags:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <Sparkles className="w-8 h-8 text-purple-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Smart Hashtags</h1>
          </div>
          <p className="text-gray-600 text-lg">
            Generate trending and relevant hashtags to boost your social media engagement
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Topic or Keyword
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., marketing automation, AI technology, business growth"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Platform
              </label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="twitter">Twitter</option>
                <option value="instagram">Instagram</option>
                <option value="linkedin">LinkedIn</option>
              </select>
            </div>
          </div>

          <Button
            onClick={generateHashtags}
            disabled={loading || !topic.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Hashtags
              </>
            )}
          </Button>
        </div>

        {/* Results */}
        {hashtags.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <Hash className="w-6 h-6 text-purple-600 mr-2" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Generated Hashtags ({hashtags.length})
                </h2>
              </div>

              <div className="flex space-x-3">
                <Button
                  onClick={copyAllHashtags}
                  variant="outline"
                  size="sm"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy All
                </Button>
                <Button
                  onClick={generateHashtags}
                  variant="outline"
                  size="sm"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Regenerate
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {hashtags.map((hashtag, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  onClick={() => copyHashtag(hashtag, index)}
                >
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {hashtag}
                  </span>
                  {copiedIndex === index ? (
                    <span className="text-xs text-green-600 font-medium">Copied!</span>
                  ) : (
                    <Copy className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              ))}
            </div>

            {/* Usage Tips */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start">
                <TrendingUp className="w-5 h-5 text-blue-600 mr-3 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium text-blue-900 mb-1">Pro Tips</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Use 2-3 hashtags on Twitter for optimal engagement</li>
                    <li>• Instagram performs best with 5-10 relevant hashtags</li>
                    <li>• LinkedIn favors professional, industry-specific hashtags</li>
                    <li>• Mix popular and niche hashtags for better reach</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {hashtags.length === 0 && !loading && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <Hash className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Generate Smart Hashtags
            </h3>
            <p className="text-gray-600 mb-6">
              Enter a topic and select a platform to get AI-powered hashtag suggestions
              that will boost your social media engagement.
            </p>
            <div className="text-sm text-gray-500">
              Popular topics: marketing automation, AI technology, business growth, digital transformation
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SmartHashtagsPage;