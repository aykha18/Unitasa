import React, { useState } from 'react';
import { Button, Card, Input } from '../components/ui';
import { Sparkles, PenTool, Hash, Megaphone } from 'lucide-react';
import apiClient from '../services/api';

type GeneratedItem = {
  id: string;
  feature: string;
  platform: string;
  type: string;
  content: string;
  hashtags: string[];
  call_to_action: string;
  character_count: number;
  generated_at: string;
  source: string;
};

const GenerateContentPage: React.FC = () => {
  const [platform, setPlatform] = useState('twitter');
  const [contentType, setContentType] = useState('educational');
  const [tone, setTone] = useState('professional');
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<GeneratedItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [posting, setPosting] = useState<{[id: string]: boolean}>({});
  const [posted, setPosted] = useState<{[id: string]: { success: boolean; url?: string; note?: string } }>({});

  const generateContent = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get client_id from local storage, handling the case where it might be a JSON string
      let clientId = localStorage.getItem('current_client_id');
      
      // If client_id is stored as a JSON string (e.g. from previous login), clean it
      if (clientId && (clientId.startsWith('"') || clientId.startsWith('{'))) {
          try {
              clientId = JSON.parse(clientId);
          } catch (e) {
              // use as is
          }
      }
      
      const res = await apiClient.post('/api/v1/social/content/generate', {
        feature_key: 'automated_social_posting',
        platform,
        content_type: contentType,
        tone,
        topic,
        client_id: clientId
      });
      const data = res.data;
      setResults(data?.content || []);
    } catch (e: any) {
      setError('Failed to generate content');
    } finally {
      setLoading(false);
    }
  };

  const postNow = async (item: GeneratedItem) => {
    setPosting(prev => ({ ...prev, [item.id]: true }));
    try {
      const res = await apiClient.post('/api/v1/social/posts', {
        content: item.content,
        platforms: [item.platform],
      });
      const result = res.data?.results?.[0] || {};
      setPosted(prev => ({ ...prev, [item.id]: { success: !!result.success, url: result.url } }));
    } catch (e) {
      setPosted(prev => ({ ...prev, [item.id]: { success: false } }));
    } finally {
      setPosting(prev => ({ ...prev, [item.id]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-8 h-8 text-purple-600" />
            <h1 className="text-2xl font-bold text-gray-900">AI Content Generator</h1>
          </div>
          <Button variant="ghost" onClick={() => window.history.pushState({}, '', '/dashboard')}>
            Back to Dashboard
          </Button>
        </div>

        <Card className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Input
                label="Topic (optional)"
                placeholder="e.g., AI marketing automation"
                value={topic}
                onChange={setTopic}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
              <select
                className="w-full px-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
              >
                <option value="twitter">Twitter</option>
                <option value="facebook">Facebook</option>
                <option value="instagram">Instagram</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
              <select
                className="w-full px-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={contentType}
                onChange={(e) => setContentType(e.target.value)}
              >
                <option value="educational">Educational</option>
                <option value="benefit_focused">Benefit Focused</option>
                <option value="social_proof">Social Proof</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tone</label>
              <select
                className="w-full px-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
              >
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="bold">Bold</option>
              </select>
            </div>
          </div>
          <div className="mt-6 flex items-center space-x-3">
            <Button icon={PenTool} onClick={generateContent} loading={loading}>
              Generate
            </Button>
          </div>
        </Card>

        <div className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          {results.map((item) => (
            <Card key={item.id}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Megaphone className="w-5 h-5 text-blue-600" />
                    <span className="text-sm text-gray-600 capitalize">{item.platform}</span>
                    <span className="text-xs text-gray-400">• {new Date(item.generated_at).toLocaleString()}</span>
                  </div>
                  <p className="text-gray-900">{item.content}</p>
                  {item.hashtags?.length > 0 && (
                    <div className="mt-2 flex flex-wrap items-center">
                      <Hash className="w-4 h-4 text-gray-500 mr-2" />
                      {item.hashtags.map((h, i) => (
                        <span key={`${h}-${i}`} className="text-sm text-gray-600 mr-2">{h}</span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">{item.character_count} chars</div>
                  <div className="mt-1 text-sm font-medium text-green-600">{item.call_to_action}</div>
                  <div className="mt-3 flex items-center justify-end space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigator.clipboard.writeText(item.content)}
                    >
                      Copy
                    </Button>
                    <Button
                      size="sm"
                      loading={posting[item.id]}
                      onClick={() => postNow(item)}
                    >
                      Post Now
                    </Button>
                  </div>
                  {posted[item.id] && (
                    <div className={`mt-2 text-sm ${posted[item.id].success ? 'text-green-600' : 'text-red-600'}`}>
                      {posted[item.id].success ? (
                        <>
                          Posted successfully {posted[item.id].url ? (
                            <a className="underline ml-1" href={posted[item.id].url} target="_blank" rel="noreferrer">View</a>
                          ) : null}
                          {posted[item.id].note && (
                            <div className="text-xs text-amber-600 mt-1 font-medium">
                              {posted[item.id].note}
                            </div>
                          )}
                        </>
                      ) : 'Post failed'}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
          {!loading && results.length === 0 && (
            <Card>
              <div className="text-center py-12">
                <p className="text-gray-600">No content yet. Configure options and click Generate.</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default GenerateContentPage;
