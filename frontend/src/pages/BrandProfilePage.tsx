import React, { useState, useEffect } from 'react';
import { Button, Card, Input } from '../components/ui';
import { Building, Users, MessageSquare, ArrowLeft, Save, Loader2, CheckCircle, RefreshCw, List, Zap, ClipboardCheck, Plus, Trash2 } from 'lucide-react';
import apiClient from '../services/api';

interface CompanyInfo {
  company_name: string;
  industry: string;
  brand_voice: string;
  mission_statement?: string;
}

interface TargetAudience {
  primary_persona: string;
  pain_points: string[];
}

interface ContentStrategy {
  themes: string[];
  tone: string;
}

interface Feature {
  title: string;
  description: string;
}

interface Step {
  step: number;
  title: string;
  description: string;
}

interface Assessment {
  title: string;
  description: string;
}

interface BrandProfile {
  client_id: string;
  brand_profile: CompanyInfo;
  audience_profile: TargetAudience;
  content_strategy: ContentStrategy;
  features?: Feature[];
  how_it_works?: Step[];
  assessments?: Assessment[];
}

const BrandProfilePage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<BrandProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form states
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [brandVoice, setBrandVoice] = useState('');
  const [painPoints, setPainPoints] = useState(''); // Comma separated
  const [themes, setThemes] = useState(''); // Comma separated
  const [features, setFeatures] = useState<Feature[]>([]);
  const [howItWorks, setHowItWorks] = useState<Step[]>([]);
  const [assessments, setAssessments] = useState<Assessment[]>([]);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    // Fetch profile
    try {
      let clientId = localStorage.getItem('current_client_id');
      if (clientId && (clientId.startsWith('"') || clientId.startsWith('{'))) {
        try { clientId = JSON.parse(clientId); } catch (e) {}
      }

      if (!clientId) {
        setError("No client ID found. Please go back to onboarding.");
        setLoading(false);
        return;
      }

      const res = await apiClient.get(`/api/v1/clients/profile/${clientId}`);
      const data = res.data;
      setProfile(data);
      
      // Initialize form
      setCompanyName(data.brand_profile.company_name || '');
      setIndustry(data.brand_profile.industry || 'General');
      setBrandVoice(data.brand_profile.brand_voice || 'Professional');
      setPainPoints((data.audience_profile.pain_points || []).join(', '));
      setThemes((data.content_strategy.themes || []).join(', '));
      setFeatures(data.features || []);
      setHowItWorks(data.how_it_works || []);
      setAssessments(data.assessments || []);
      
    } catch (e) {
      setError("Failed to load profile.");
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    setSuccessMessage(null);
    setError(null);

    try {
      const updatedProfile = {
        company_info: {
          ...profile.brand_profile,
          company_name: companyName,
          industry: industry,
          brand_voice: brandVoice
        },
        target_audience: {
          ...profile.audience_profile,
          pain_points: painPoints.split(',').map(s => s.trim()).filter(Boolean)
        },
        content_preferences: {
            content_tone: brandVoice,
            key_messages: themes.split(',').map(s => s.trim()).filter(Boolean)
        },
        features,
        how_it_works: howItWorks,
        assessments
      };

      await apiClient.put(`/api/v1/clients/profile/${profile.client_id}`, updatedProfile);
      setSuccessMessage("Profile updated successfully! Content generation will now reflect these changes.");
      
      // Refresh profile data
      fetchProfile();
      
    } catch (e) {
      setError("Failed to save profile.");
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 text-purple-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" onClick={() => window.history.back()}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Brand Knowledge Base</h1>
              <p className="text-gray-500">Review and approve what the AI knows about your business</p>
            </div>
        

          </div>
          <div className="flex space-x-3">
             <Button variant="outline" onClick={fetchProfile}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Reload
             </Button>
             <Button onClick={handleSave} disabled={saving} className="bg-purple-600 hover:bg-purple-700 text-white">
                {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                Save & Approve
             </Button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
            <span className="mr-2">⚠️</span> {error}
          </div>
        )}

        {successMessage && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" /> {successMessage}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Company Info */}
          <Card className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Building className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Company Identity</h2>
            </div>
            
            <div className="space-y-4">
              <Input
                label="Company Name"
                value={companyName}
                onChange={setCompanyName}
                placeholder="e.g. Acme Corp"
              />
              <div>
                <Input
                  label="Industry / Niche"
                  value={industry}
                  onChange={setIndustry}
                  placeholder="e.g. Blockchain Security, SaaS, etc."
                />
                <p className="text-xs text-gray-500 mt-1">Be specific! This determines the templates we use.</p>
              </div>
              <Input
                label="Brand Voice"
                value={brandVoice}
                onChange={setBrandVoice}
                placeholder="e.g. Professional, Witty, Technical"
              />
            </div>
          </Card>

          {/* Audience & Strategy */}
          <Card className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Audience & Strategy</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Customer Pain Points
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent min-h-[80px]"
                  value={painPoints}
                  onChange={(e) => setPainPoints(e.target.value)}
                  placeholder="e.g. Manual processes, High costs, Security risks"
                />
                <p className="text-xs text-gray-500 mt-1">Comma separated list of problems you solve.</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Key Content Themes
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent min-h-[80px]"
                  value={themes}
                  onChange={(e) => setThemes(e.target.value)}
                  placeholder="e.g. Innovation, Security Tips, Case Studies"
                />
                <p className="text-xs text-gray-500 mt-1">Topics you want to post about.</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Extended Profile Sections */}
        <div className="space-y-6 mt-6">
          
          {/* Features */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <Zap className="w-5 h-5 text-yellow-600" />
                </div>
                <h2 className="text-lg font-semibold text-gray-900">Key Features</h2>
              </div>
              <Button size="sm" variant="outline" onClick={() => setFeatures([...features, { title: '', description: '' }])}>
                <Plus className="w-4 h-4 mr-2" /> Add Feature
              </Button>
            </div>
            <div className="space-y-4">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1 space-y-3">
                    <Input 
                      label=""
                      placeholder="Feature Title" 
                      value={feature.title} 
                      onChange={(v) => {
                        const newFeatures = [...features];
                        newFeatures[index].title = v;
                        setFeatures(newFeatures);
                      }}
                    />
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Feature Description"
                      value={feature.description}
                      onChange={(e) => {
                        const newFeatures = [...features];
                        newFeatures[index].description = e.target.value;
                        setFeatures(newFeatures);
                      }}
                    />
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setFeatures(features.filter((_, i) => i !== index))}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              ))}
              {features.length === 0 && <p className="text-gray-500 italic text-center py-4">No features added yet.</p>}
            </div>
          </Card>

          {/* How It Works */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <List className="w-5 h-5 text-blue-600" />
                </div>
                <h2 className="text-lg font-semibold text-gray-900">How It Works</h2>
              </div>
              <Button size="sm" variant="outline" onClick={() => setHowItWorks([...howItWorks, { step: howItWorks.length + 1, title: '', description: '' }])}>
                <Plus className="w-4 h-4 mr-2" /> Add Step
              </Button>
            </div>
            <div className="space-y-4">
              {howItWorks.map((step, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-12 h-12 flex items-center justify-center bg-white rounded-full border font-bold text-gray-500 flex-shrink-0">
                    {index + 1}
                  </div>
                  <div className="flex-1 space-y-3">
                    <Input 
                      label=""
                      placeholder="Step Title" 
                      value={step.title} 
                      onChange={(v) => {
                        const newSteps = [...howItWorks];
                        newSteps[index].title = v;
                        setHowItWorks(newSteps);
                      }}
                    />
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Step Description"
                      value={step.description}
                      onChange={(e) => {
                        const newSteps = [...howItWorks];
                        newSteps[index].description = e.target.value;
                        setHowItWorks(newSteps);
                      }}
                    />
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setHowItWorks(howItWorks.filter((_, i) => i !== index))}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              ))}
              {howItWorks.length === 0 && <p className="text-gray-500 italic text-center py-4">No steps added yet.</p>}
            </div>
          </Card>

          {/* Assessments */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <ClipboardCheck className="w-5 h-5 text-green-600" />
                </div>
                <h2 className="text-lg font-semibold text-gray-900">Assessments / Lead Magnets</h2>
              </div>
              <Button size="sm" variant="outline" onClick={() => setAssessments([...assessments, { title: '', description: '' }])}>
                <Plus className="w-4 h-4 mr-2" /> Add Assessment
              </Button>
            </div>
            <div className="space-y-4">
              {assessments.map((item, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1 space-y-3">
                    <Input 
                      label=""
                      placeholder="Assessment Title" 
                      value={item.title} 
                      onChange={(v) => {
                        const newItems = [...assessments];
                        newItems[index].title = v;
                        setAssessments(newItems);
                      }}
                    />
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Description"
                      value={item.description}
                      onChange={(e) => {
                        const newItems = [...assessments];
                        newItems[index].description = e.target.value;
                        setAssessments(newItems);
                      }}
                    />
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setAssessments(assessments.filter((_, i) => i !== index))}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              ))}
              {assessments.length === 0 && <p className="text-gray-500 italic text-center py-4">No assessments added yet.</p>}
            </div>
          </Card>
        </div>

        {/* Preview Section */}
        <div className="mt-8">
            <Card className="p-6 bg-purple-50 border-purple-100">
                <div className="flex items-center space-x-3 mb-4">
                    <MessageSquare className="w-5 h-5 text-purple-600" />
                    <h3 className="text-lg font-semibold text-gray-900">Why is this important?</h3>
                </div>
                <p className="text-gray-700">
                    The AI uses this profile to generate every single post. If your Industry is set to "General", you'll get generic business advice. 
                    If you change it to <strong>"Blockchain Security"</strong>, you'll get content about smart contracts, audits, and Web3 safety.
                </p>
                <div className="mt-4 flex justify-end">
                    <Button onClick={() => window.location.href = '/generate-content'} variant="outline">
                        Go to Content Generator
                    </Button>
                </div>
            </Card>
        </div>
      </div>
    </div>
  );
};

export default BrandProfilePage;
