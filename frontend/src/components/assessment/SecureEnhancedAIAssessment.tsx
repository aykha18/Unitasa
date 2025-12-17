import React, { useState, useEffect } from 'react';
import { Brain, MessageCircle, ArrowRight, ArrowLeft, CheckCircle, X } from 'lucide-react';
import Button from '../ui/Button';
import AIReadinessAssessment from './AIReadinessAssessment';
import { LeadData } from './LeadCaptureForm';
import { paymentService } from '../../services/paymentService';
import ConsultationBooking from '../booking/ConsultationBooking';
import SimpleAIReportModal from '../reports/SimpleAIReportModal';
import { useCurrency } from '../../hooks/useCurrency';

interface AssessmentStep {
  id: string;
  title: string;
  description: string;
  component: React.ReactNode;
}

interface EnhancedAIAssessmentProps {
  onComplete?: (results: any) => void;
  onClose?: () => void;
  leadData?: LeadData | null;
}

const EnhancedAIAssessment: React.FC<EnhancedAIAssessmentProps> = ({ onComplete, onClose, leadData }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [assessmentData, setAssessmentData] = useState<Record<string, any>>({});
  const [showResults, setShowResults] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  
  // Fixed pricing for co-creator program
  const coCreatorPrice = '₹29,999';

  // Auto-hide success toast after 8 seconds
  useEffect(() => {
    if (showSuccessToast) {
      const timer = setTimeout(() => {
        setShowSuccessToast(false);
      }, 8000);
      return () => clearTimeout(timer);
    }
  }, [showSuccessToast]);



  const steps: AssessmentStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to AI Assessment',
      description: 'Discover your AI readiness and unlock growth opportunities',
      component: (
        <div className="text-center py-8">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            AI Marketing Intelligence Assessment
          </h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Get personalized insights on how AI can transform your marketing operations and drive growth.
          </p>
          <Button 
            size="lg" 
            onClick={() => setCurrentStep(1)}
            className="px-8 py-4 text-lg"
          >
            Start Assessment
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      )
    },
    {
      id: 'assessment',
      title: 'AI Readiness Assessment',
      description: 'Answer questions about your current marketing setup',
      component: (
        <AIReadinessAssessment 
          leadData={leadData}
        />
      )
    }
  ];

  const handleSecurePayment = async () => {
    setPaymentLoading(true);
    setPaymentError(null);

    try {
      // Detect user currency and country
      const { currency, country } = paymentService.detectUserCurrency();
      
      // Create secure payment order through backend
      const orderData = await paymentService.createPaymentOrder({
        amount: 361.0,
        customer_email: leadData?.email || 'member@unitasa.in',
        customer_name: leadData?.name || 'Co-Creator Member',
        lead_id: undefined, // You can add lead ID if available
        program_type: 'co_creator',
        currency: currency,
        customer_country: country
      });

      console.log('✅ Secure order created:', orderData);

      // Load Razorpay script
      await paymentService.loadRazorpayScript();

      // Open Razorpay checkout with secure parameters
      const options = {
        key: orderData.key_id, // Secure key from backend
        amount: orderData.amount * 100, // Amount in paise from backend
        currency: orderData.currency, // Currency from backend
        name: 'Unitasa Co-Creator Program',
        description: `Founding Member Access - $${orderData.amount_usd} / ₹${orderData.amount_inr}`,
        order_id: orderData.order_id, // Secure order ID from backend
        handler: async (response: any) => {
          console.log('💳 Payment completed, verifying...');
          
          try {
            // Verify payment signature on backend
            const verifyData = await paymentService.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            });

            if (verifyData.success && verifyData.verified) {
              console.log('✅ Payment verified successfully');
              setPaymentSuccess(true);
              setPaymentLoading(false);
              
              // Show success message with modern toast
              setSuccessMessage(`🎉 Payment successful! Welcome to the Co-Creator Program!\n\nPayment ID: ${response.razorpay_payment_id}\n\nYou will receive onboarding instructions via email shortly.`);
              setShowSuccessToast(true);
            } else {
              throw new Error('Payment verification failed');
            }
            
          } catch (verifyError) {
            console.error('❌ Payment verification failed:', verifyError);
            setPaymentError('Payment completed but verification failed. Please contact support.');
            setPaymentLoading(false);
          }
        },
        prefill: {
          name: orderData.customer_name,
          email: orderData.customer_email,
          contact: '+919999999999'
        },
        theme: {
          color: '#7c3aed'
        },
        method: {
          netbanking: true,
          card: true,
          upi: true,
          wallet: true,
          emi: false,
          paylater: false
        },
        modal: {
          ondismiss: () => {
            console.log('❌ Payment cancelled by user');
            setPaymentLoading(false);
          }
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();

    } catch (error) {
      console.error('❌ Payment initiation failed:', error);
      setPaymentError(error instanceof Error ? error.message : 'Payment failed. Please try again.');
      setPaymentLoading(false);
    }
  };

  const currentStepData = steps[currentStep];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Assessment completed, show results
      const mockResults = {
        aiReadinessScore: 85,
        automationMaturity: 78,
        dataIntelligence: 82,
        integrationReadiness: 90,
        overallScore: 84,
        recommendations: [
          'Implement AI-powered lead scoring',
          'Automate email marketing workflows',
          'Integrate predictive analytics'
        ],
        predictedROI: 340,
        automationOpportunities: 12,
        co_creator_qualified: true
      };
      setAssessmentData(mockResults);
      setShowResults(true);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (showResults) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 max-w-4xl mx-auto">
        {/* Results Header */}
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-blue-50">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Assessment Complete!</h2>
            <p className="text-gray-600">Your AI Marketing Intelligence Report is ready</p>
          </div>
        </div>

        {/* Results Content */}
        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Left Column - Assessment Results */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-6">
                Ready to Activate Your AI Marketing Team?
              </h3>
              
              {/* Primary CTA - Start AI Implementation */}
              <div className="mb-6">
                <Button 
                  size="lg" 
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 text-lg"
                  onClick={() => {
                    console.log('🚀 Start AI Implementation clicked');
                    setShowBookingModal(true);
                  }}
                >
                  🚀 Start AI Implementation
                </Button>
                <p className="text-center text-sm text-gray-600 mt-2">
                  Book your personalized implementation strategy session
                </p>
              </div>
              
              <div className="space-y-6">
                {/* Schedule Session */}
                <div className="bg-blue-50 rounded-lg p-6">
                  <div className="text-center mb-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <MessageCircle className="w-6 h-6 text-blue-600" />
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">Schedule AI Strategy Session</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      Get a personalized 30-minute consultation to discuss your AI implementation roadmap
                    </p>
                  </div>
                  
                  {!showBookingModal ? (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="w-full"
                      onClick={() => {
                        console.log('🔍 Book Free Session clicked');
                        setShowBookingModal(true);
                      }}
                    >
                      Book Free Session
                    </Button>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <p className="text-sm font-medium text-gray-900 mb-4">
                          📅 Ready to book your AI Strategy Session?
                        </p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <Button
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700"
                          onClick={() => {
                            console.log('🔍 Opening Calendly...');
                            // Open your AI Strategy Session booking page
                            window.open('https://calendly.com/khanayubchand/ai-strategy-session', '_blank', 'width=800,height=600');
                          }}
                        >
                          📅 Book Now
                        </Button>
                        
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            console.log('🔍 Closing booking form');
                            setShowBookingModal(false);
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                      
                      <div className="text-center">
                        <p className="text-xs text-gray-500">
                          Free 30-minute consultation • No commitment required
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column - Co-Creator Program */}
            <div>
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
                <div className="text-center mb-4">
                  <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 mb-3">
                    LIMITED TIME
                  </div>
                  <h4 className="text-lg font-bold text-gray-900 mb-2">Join 25 Founding Co-Creators</h4>
                </div>

                <div className="text-center mb-4">
                  {/* Fixed pricing for co-creator program */}
                  <div className="text-3xl font-bold text-purple-600">
                    {coCreatorPrice}
                  </div>
                  <div className="text-sm text-gray-500 line-through mt-2">
                    Regular: ₹1,67,000+
                  </div>
                  <div className="text-sm text-green-600 font-medium mt-1">
                    🚀 Founding Member Price • ⚡ Only 12 spots left
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mb-4 text-center">
                  Lifetime access to AI platform + direct product influence + priority support
                </p>
                
                <Button 
                  size="sm" 
                  className="w-full bg-purple-600 hover:bg-purple-700"
                  onClick={handleSecurePayment}
                  disabled={paymentLoading}
                >
                  {paymentLoading ? 'Processing...' : 'Secure Founding Spot'}
                </Button>
                
                {paymentError && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                    {paymentError}
                  </div>
                )}
                
                {paymentSuccess && (
                  <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
                    🎉 Payment successful! Welcome to the Co-Creator Program!
                  </div>
                )}
                
                <div className="text-xs text-center text-gray-500 mt-2">
                  ⚡ Only 12 spots remaining
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="p-6 border-t border-gray-200">
          {!showReportModal ? (
            <div className="flex justify-between">
              <Button onClick={onClose} variant="outline">
                Close Assessment
              </Button>
              <Button onClick={() => {
                console.log('🔍 Get Full AI Report clicked');
                setShowReportModal(true);
              }}>
                Get Full AI Report
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  📊 Get Your Complete AI Marketing Report
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Receive a detailed PDF report with personalized recommendations, implementation roadmap, and ROI projections.
                </p>
              </div>
              
              <div className="bg-blue-50 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Your Report Includes:</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Detailed AI readiness assessment results</li>
                  <li>• Custom CRM integration recommendations</li>
                  <li>• Step-by-step implementation roadmap</li>
                  <li>• ROI projections and timeline estimates</li>
                  <li>• Automation opportunity analysis</li>
                </ul>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <Button
                  className="bg-blue-600 hover:bg-blue-700"
                  onClick={() => {
                    console.log('🔍 Generating AI report...');
                    // Simulate report generation and show toast
                    setSuccessMessage('📧 Your AI Marketing Report has been sent to your email! Check your inbox in the next few minutes.');
                    setShowSuccessToast(true);
                    setShowReportModal(false);
                  }}
                >
                  📧 Email Report
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => {
                    console.log('🔍 Closing report form');
                    setShowReportModal(false);
                  }}
                >
                  Cancel
                </Button>
              </div>
              
              <div className="flex justify-between items-center mt-4">
                <Button onClick={onClose} variant="outline" size="sm">
                  Close Assessment
                </Button>
                <Button 
                  onClick={() => {
                    console.log('🔄 Retake Assessment clicked');
                    // Reset assessment state
                    setCurrentStep(0);
                    setAssessmentData({});
                    setShowResults(false);
                    setShowBookingModal(false);
                    setShowReportModal(false);
                  }}
                  variant="outline" 
                  size="sm"
                  className="text-blue-600 border-blue-600 hover:bg-blue-50"
                >
                  🔄 Retake Assessment
                </Button>
                <div className="text-xs text-gray-500 self-center">
                  Report delivered within 5 minutes
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 max-w-4xl mx-auto">
      {/* Progress Header */}
      {currentStep > 0 && (
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {currentStepData.title}
            </h2>
            <span className="text-sm text-gray-500">
              Step {currentStep} of {steps.length - 1}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-purple-500 to-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Step Content */}
      <div className="p-6">
        {currentStepData.component}
      </div>

      {/* Navigation */}
      {currentStep > 0 && !showResults && (
        <div className="p-6 border-t border-gray-200 flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>
          <Button onClick={handleNext}>
            {currentStep === steps.length - 1 ? 'Complete Assessment' : 'Continue'}
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      )}

      {/* Modern Success Toast */}
      {showSuccessToast && (
        <div className="fixed top-4 right-4 z-50 max-w-md">
          <div className="bg-green-50 border border-green-200 rounded-lg shadow-lg p-4 transform transition-all duration-300 ease-in-out">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <CheckCircle className="w-6 h-6 text-green-500" />
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-gray-900">
                  Payment Successful!
                </h3>
                <p className="mt-1 text-sm text-gray-600 whitespace-pre-line">
                  {successMessage}
                </p>
              </div>
              <div className="ml-4 flex-shrink-0">
                <button
                  onClick={() => setShowSuccessToast(false)}
                  className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Note: Modals replaced with inline expansions to avoid modal-in-modal conflicts */}
    </div>
  );
};

export default EnhancedAIAssessment;