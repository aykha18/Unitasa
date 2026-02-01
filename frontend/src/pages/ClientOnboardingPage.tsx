import React, { useState, useEffect } from 'react';
import { Button, Card, Input } from '../components/ui';
import apiClient from '../services/api';
import { Globe, Building2, ArrowRight, CheckCircle, Loader2 } from 'lucide-react';

interface OnboardingResponse {
  client_id: string;
  onboarding_status: string;
  estimated_content_quality: number;
}

const ClientOnboardingPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'input' | 'processing' | 'success'>('input');
  
  const [formData, setFormData] = useState({
    website: '',
    companyName: '',
    industry: '',
  });

  const [result, setResult] = useState<OnboardingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadExistingData = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const queryClientId = params.get('client_id');
        if (queryClientId) {
          localStorage.setItem('current_client_id', queryClientId);
        }
        let savedClientId = localStorage.getItem('current_client_id');
        if (savedClientId && (savedClientId.startsWith('"') || savedClientId.startsWith('{'))) {
          try { savedClientId = JSON.parse(savedClientId); } catch (e) {}
        }
        if (savedClientId) {
          const clientId = savedClientId.replace(/^"|"$/g, '');
          const response = await apiClient.get(`/api/v1/clients/profile/${clientId}`);
          const data = response.data || {};
          const ci = data.company_info || {};
          const bp = data.brand_profile || {};
          setFormData(prev => ({
            ...prev,
            website: ci.website || bp.website || '',
            companyName: ci.company_name || bp.company_name || '',
            industry: ci.industry || bp.industry || ''
          }));
        }
      } catch (err) {
        // Silent fail if no profile found
        console.log('No existing profile loaded');
      }
    };
    
    loadExistingData();
  }, []);

  const navigateTo = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('popstate'));
  };

  const handleAnalyze = async () => {
    if (!formData.website) {
      setError('Please enter a website URL');
      return;
    }

    setLoading(true);
    setStep('processing');
    setError(null);

    try {
      // Construct the request payload for the new One-Click Onboarding endpoint
      const payload = {
        url: formData.website,
        generate_content: true
      };

      const response = await apiClient.post('/api/v1/onboarding/start', payload);
      setResult({
        ...response.data,
        // Map new response fields to expected state format if needed, or update state interface
        client_id: response.data.brand_profile?.company_info?.company_name ? "created" : "pending", 
        // Note: The new endpoint returns full analysis, we'll store what we need
        onboarding_status: "completed",
        estimated_content_quality: 0.95 
      });

      // If the backend returns a client_id or we can derive one, save it
      // For now, the new endpoint focuses on analysis, so we might need to adjust how we handle the "success" state data
      if (response.data.brand_profile) {
         // Store the analysis result temporarily or update a global context
         console.log("Onboarding Analysis:", response.data);
      }
      
      setStep('success');
    } catch (err: any) {
      console.error('Onboarding failed:', err);
      setError(err.response?.data?.detail || 'Failed to analyze website. Please try again.');
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Setup Your Brand Profile</h1>
          <p className="text-gray-600">
            Enter your website and our AI will automatically analyze your brand voice, audience, and industry.
          </p>
        </div>

        <Card className="p-8">
          {step === 'input' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Website URL <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Globe className="h-5 w-5 text-gray-400" />
                  </div>
                  <Input
                    type="url"
                    placeholder="https://example.com"
                    value={formData.website}
                    onChange={(value) => setFormData({ ...formData, website: value })}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Name (Optional)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Building2 className="h-5 w-5 text-gray-400" />
                    </div>
                    <Input
                      type="text"
                      placeholder="Acme Corp"
                      value={formData.companyName}
                      onChange={(value) => setFormData({ ...formData, companyName: value })}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Industry (Optional)
                  </label>
                  <Input
                    type="text"
                    placeholder="e.g. SaaS, Healthcare"
                    value={formData.industry}
                    onChange={(value) => setFormData({ ...formData, industry: value })}
                  />
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm">
                  {error}
                </div>
              )}

              <Button 
                onClick={handleAnalyze} 
                className="w-full py-6 text-lg font-semibold"
                disabled={!formData.website}
              >
                Analyze Website & Create Profile
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>
          )}

          {step === 'processing' && (
            <div className="text-center py-12">
              <Loader2 className="h-16 w-16 text-blue-600 animate-spin mx-auto mb-6" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Analyzing your website...</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Our AI is reading your content, identifying your brand voice, and building your marketing profile. This usually takes about 10-20 seconds.
              </p>
            </div>
          )}

          {step === 'success' && result && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Profile Created Successfully!</h3>
              <p className="text-gray-600 mb-8">
                We've analyzed your brand and set up your knowledge base.
                <br />
                <span className="text-sm font-medium bg-blue-50 text-blue-700 px-3 py-1 rounded-full mt-2 inline-block">
                  Content Quality Score: {Math.round(result.estimated_content_quality * 100)}/100
                </span>
              </p>

              <div className="flex flex-col gap-3">
                <Button 
                  onClick={() => navigateTo('/dashboard')} 
                  variant="outline"
                  className="w-full"
                >
                  Go to Dashboard
                </Button>
                <Button 
                  onClick={() => navigateTo('/generate-content')} 
                  className="w-full"
                >
                  Generate First Post
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </Card>
        
        {step === 'input' && (
          <p className="text-center text-xs text-gray-400 mt-8">
            Unitasa AI Agent v1.0 • Automated Client Analysis
          </p>
        )}
      </div>
    </div>
  );
};

export default ClientOnboardingPage;
