import React, { useState } from 'react';
import { ArrowLeft, CheckCircle, Zap, Star, Crown } from 'lucide-react';
import { Button } from '../components/ui';

const CoCreatorSignupPage: React.FC = () => {
  const [isStartingAssessment, setIsStartingAssessment] = useState(false);

  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  const handleStartAssessment = () => {
    setIsStartingAssessment(true);
    // Trigger the assessment modal directly for co-creator flow
    window.dispatchEvent(new CustomEvent('openAssessment'));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-unitasa-light via-white to-unitasa-light">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={handleBackToHome}
              className="flex items-center text-unitasa-gray hover:text-unitasa-blue transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Home
            </button>
            <div className="flex items-center space-x-2">
              <div className="bg-primary-600 p-2 rounded-lg">
                <div className="w-6 h-6 bg-white rounded flex items-center justify-center text-primary-600 text-sm font-bold">
                  U
                </div>
              </div>
              <span className="text-xl font-bold text-unitasa-blue">Unitasa</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Hero Section */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-8 text-center">
            <div className="inline-flex items-center bg-white/20 text-white px-4 py-2 rounded-full text-sm font-medium mb-4">
              <Crown className="w-4 h-4 mr-2" />
              Exclusive Founding Member Program
            </div>
            <h1 className="text-4xl font-bold mb-4">Join 25 Founding Members</h1>
            <p className="text-xl text-white/90 mb-6">
              Get lifetime access at founding pricing - Only ₹29,999 (vs ₹1,67,000+ later)
            </p>
            <div className="flex items-center justify-center space-x-8 text-sm">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Lifetime Access
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Priority Support
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Product Influence
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Benefits */}
              <div>
                <h2 className="text-2xl font-bold text-unitasa-blue mb-6">Founding Member Benefits</h2>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <Star className="w-5 h-5 text-yellow-500 mr-3 mt-1" />
                    <div>
                      <h3 className="font-semibold">Lifetime Platform Access</h3>
                      <p className="text-gray-600 text-sm">Never pay subscription fees again</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <Zap className="w-5 h-5 text-blue-500 mr-3 mt-1" />
                    <div>
                      <h3 className="font-semibold">Priority Feature Requests</h3>
                      <p className="text-gray-600 text-sm">Direct influence on product development</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-1" />
                    <div>
                      <h3 className="font-semibold">Exclusive Community Access</h3>
                      <p className="text-gray-600 text-sm">Network with other founding members</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-1" />
                    <div>
                      <h3 className="font-semibold">Custom Integrations</h3>
                      <p className="text-gray-600 text-sm">Personalized setup and integrations</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Pricing & CTA */}
              <div>
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 rounded-xl">
                  <h3 className="text-xl font-bold text-center mb-4">Founding Member Pricing</h3>
                  
                  <div className="text-center mb-6">
                    <div className="text-3xl font-bold text-purple-600">₹29,999</div>
                    <div className="text-sm text-gray-500 line-through">Regular Price: ₹1,67,000+</div>
                    <div className="text-green-600 font-semibold">Save 82% as Founding Member</div>
                  </div>

                  <div className="bg-yellow-100 border border-yellow-300 rounded-lg p-4 mb-6">
                    <div className="flex items-center text-yellow-800">
                      <Zap className="w-4 h-4 mr-2" />
                      <span className="font-semibold">Limited Time: Only 25 seats available</span>
                    </div>
                    <div className="text-sm text-yellow-700 mt-1">
                      12 seats remaining - Program fills quickly
                    </div>
                  </div>

                  <Button
                    onClick={handleStartAssessment}
                    className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 text-lg font-semibold"
                    disabled={isStartingAssessment}
                  >
                    {isStartingAssessment ? 'Starting Assessment...' : 'Take Assessment & Join'}
                  </Button>

                  <p className="text-xs text-gray-500 text-center mt-3">
                    Assessment required to qualify for founding member program
                  </p>
                </div>
              </div>
            </div>

            {/* Process Steps */}
            <div className="mt-12 border-t pt-8">
              <h3 className="text-xl font-bold text-center mb-8">Simple 3-Step Process</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    1
                  </div>
                  <h4 className="font-semibold mb-2">Take Assessment</h4>
                  <p className="text-sm text-gray-600">3-minute AI readiness assessment to qualify</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    2
                  </div>
                  <h4 className="font-semibold mb-2">Secure Your Seat</h4>
                  <p className="text-sm text-gray-600">Complete payment to reserve your founding member seat</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    3
                  </div>
                  <h4 className="font-semibold mb-2">Get Lifetime Access</h4>
                  <p className="text-sm text-gray-600">Immediate access to all features + founding member benefits</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="mt-8 text-center">
          <div className="flex items-center justify-center space-x-8 text-sm text-unitasa-gray">
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              30-day money back guarantee
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              Secure payment processing
            </div>
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
              Instant access after payment
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoCreatorSignupPage;