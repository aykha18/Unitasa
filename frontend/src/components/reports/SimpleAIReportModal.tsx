import React, { useState } from 'react';
import { FileText, X, CheckCircle, Brain } from 'lucide-react';
import Button from '../ui/Button';

interface SimpleAIReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  assessmentData: any;
  leadData?: {
    name?: string;
    email?: string;
    company?: string;
  };
}

const SimpleAIReportModal: React.FC<SimpleAIReportModalProps> = ({
  isOpen,
  onClose,
  assessmentData,
  leadData
}) => {
  const [step, setStep] = useState<'form' | 'generating' | 'complete'>('form');
  const [formData, setFormData] = useState({
    name: leadData?.name || '',
    email: leadData?.email || '',
    company: leadData?.company || ''
  });



  if (!isOpen) return null;

  const handleGenerateReport = async () => {
    setStep('generating');
    
    // Simulate report generation
    setTimeout(() => {
      setStep('complete');
    }, 2000);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  AI Marketing Intelligence Report
                </h2>
                <p className="text-sm text-gray-600">
                  Comprehensive analysis of your AI readiness
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">


          {step === 'form' && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Brain className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Get Your Personalized AI Report
                </h3>
                <p className="text-gray-600">
                  Receive a comprehensive report with your AI readiness analysis
                </p>
              </div>

              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Your report includes:</h4>
                <div className="grid md:grid-cols-2 gap-2 text-sm text-gray-700">
                  <div className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Executive Summary & Readiness Score
                  </div>
                  <div className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    CRM Integration Analysis
                  </div>
                  <div className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    12-Month Implementation Roadmap
                  </div>
                  <div className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    ROI Projections & Business Impact
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Your full name"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  value={formData.company}
                  onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Your company (optional)"
                />
              </div>

              <Button
                onClick={handleGenerateReport}
                disabled={!formData.name || !formData.email}
                className="w-full"
                size="lg"
              >
                Generate My AI Report
                <FileText className="w-4 h-4 ml-2" />
              </Button>
            </div>
          )}

          {step === 'generating' && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                <Brain className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Generating Your AI Report...
              </h3>
              <p className="text-gray-600 mb-6">
                Our AI is analyzing your assessment data and creating personalized recommendations
              </p>
              <div className="w-64 bg-gray-200 rounded-full h-2 mx-auto">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '75%' }}></div>
              </div>
              <p className="text-sm text-gray-500 mt-4">This usually takes 30-60 seconds...</p>
            </div>
          )}

          {step === 'complete' && (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Report Generated Successfully! 🎉
              </h3>
              
              <p className="text-gray-600 mb-6">
                Your comprehensive AI Marketing Intelligence Report has been sent to{' '}
                <span className="font-medium text-blue-600">{formData.email}</span>
              </p>

              <div className="bg-green-50 rounded-lg p-4 mb-6 text-left max-w-md mx-auto">
                <h4 className="font-medium text-gray-900 mb-2">What's included:</h4>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    Executive Summary & AI Readiness Score
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    CRM Integration Analysis
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    12-Month Implementation Roadmap
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    ROI Projections & Business Impact
                  </li>
                </ul>
              </div>

              <div className="space-y-3">
                <Button
                  onClick={onClose}
                  className="w-full"
                  size="lg"
                >
                  Continue Exploring Unitasa
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => window.open('mailto:support@unitasa.in', '_blank')}
                  className="w-full"
                >
                  Questions? Contact Us
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SimpleAIReportModal;