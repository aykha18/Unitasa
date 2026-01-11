import React, { useState, useEffect } from 'react';
import { Brain, Target, Zap, Shield, BarChart3, MessageCircle, ArrowRight, ArrowLeft, CheckCircle, CreditCard } from 'lucide-react';
import Button from '../ui/Button';
import AIReadinessAssessment from './AIReadinessAssessment';
import { LeadData } from './LeadCaptureForm';
import { paymentService } from '../../services/paymentService';
import { pricingService, PricingPlan } from '../../services/pricingService';
import { useAuth } from '../../context/AuthContext';
import config from '../../config/environment';

interface AssessmentStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  component: React.ReactNode;
}

interface EnhancedAIAssessmentProps {
  onComplete?: (results: any) => void;
  onClose?: () => void;
  leadData?: LeadData | null;
}

const EnhancedAIAssessment: React.FC<EnhancedAIAssessmentProps> = ({ onComplete, onClose, leadData }) => {
  const { user, updateUser } = useAuth();
  
  // Custom navigation function since we're not using React Router
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
    window.scrollTo(0, 0);
  };

  const [currentStep, setCurrentStep] = useState(0);
  const [assessmentData, setAssessmentData] = useState<Record<string, any>>({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);
  
  const [coCreatorPlan, setCoCreatorPlan] = useState<PricingPlan | null>(null);

  useEffect(() => {
    const fetchPricing = async () => {
      try {
        const plans = await pricingService.getAllPlans();
        const plan = plans.find(p => p.name === 'co_creator');
        if (plan) {
          setCoCreatorPlan(plan);
        }
      } catch (error) {
        console.error('Failed to fetch pricing plans:', error);
      }
    };
    fetchPricing();
  }, []);

  const handleSecurePayment = async () => {
    setPaymentLoading(true);
    setPaymentError(null);

    try {
      // Detect user currency and country
      const { currency, country } = paymentService.detectUserCurrency();
      
      const priceInr = coCreatorPlan ? coCreatorPlan.price_inr : 29999;

      // Create secure payment order through backend
      const orderData = await paymentService.createPaymentOrder({
        amount: priceInr,
        customer_email: user?.email || leadData?.email || '',
        customer_name: user?.full_name || leadData?.name || 'Co-Creator Member',
        program_type: 'co_creator',
        customer_country: 'IN', // Defaulting to IN for INR pricing
        currency: 'INR'
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
        description: `Founding Member Access - ₹${orderData.amount_inr || orderData.amount}`,
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
              
              // Refresh user data to reflect new subscription status
              try {
                const token = localStorage.getItem('access_token');
                if (token) {
                  const response = await fetch(`${config.apiBaseUrl}/api/v1/auth/me`, {
                    headers: {
                      'Authorization': `Bearer ${token}`
                    }
                  });
                  
                  if (response.ok) {
                    const updatedUser = await response.json();
                    updateUser(updatedUser);
                    console.log('User profile updated with new subscription:', updatedUser.subscription_tier);
                  }
                }
              } catch (error) {
                console.error('Failed to refresh user profile:', error);
              }

              setPaymentSuccess(true);
              setPaymentLoading(false);
              setShowPaymentModal(false);
              
              // Redirect to profile after a short delay
              setTimeout(() => {
                 navigate('/profile');
              }, 3000);
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
          name: user?.full_name || leadData?.name || 'Co-Creator Member',
          email: user?.email || leadData?.email || '',
          contact: ''
        },
        theme: {
          color: '#7c3aed'
        },
        modal: {
          ondismiss: function() {
            setPaymentLoading(false);
          }
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();

    } catch (error: any) {
      console.error('Payment initialization failed:', error);
      setPaymentError(error.message || 'Failed to initialize payment');
      setPaymentLoading(false);
    }
  };

  const steps: AssessmentStep[] = [
    {
      id: 'welcome',
      title: 'AI Marketing Intelligence Assessment',
      description: 'Discover your AI readiness and unlock autonomous marketing potential',
      icon: <Brain className="w-8 h-8" />,
      component: (
        <div className="text-center py-12">
          <div className="mb-8">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Brain className="w-10 h-10 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Marketing Intelligence Unity Assessment
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Discover how Unitasa can replace your fragmented marketing tools with one unified platform. 
              Get your personalized marketing unity roadmap in just 3 minutes.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 p-6 rounded-lg">
              <Target className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">AI Readiness Score</h3>
              <p className="text-sm text-gray-600">Assess your current AI maturity level</p>
            </div>
            <div className="bg-green-50 p-6 rounded-lg">
              <Zap className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">ROI Prediction</h3>
              <p className="text-sm text-gray-600">Forecast your AI implementation impact</p>
            </div>
            <div className="bg-purple-50 p-6 rounded-lg">
              <BarChart3 className="w-8 h-8 text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Custom Roadmap</h3>
              <p className="text-sm text-gray-600">Get your personalized AI strategy</p>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg mb-8">
            <h3 className="font-semibold text-gray-900 mb-4">What You'll Discover:</h3>
            <div className="grid md:grid-cols-2 gap-4 text-left">
              <div className="flex items-start">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Your AI Marketing IQ Score (0-100)</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Predicted ROI improvement potential</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Priority automation opportunities</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-sm text-gray-700">Personalized AI agent recommendations</span>
              </div>
            </div>
          </div>

          <Button 
            size="lg" 
            onClick={() => setCurrentStep(1)}
            className="px-8 py-4 text-lg"
          >
            Start AI Assessment
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      )
    },
    {
      id: 'ai-readiness',
      title: 'AI Readiness Assessment',
      description: 'Evaluate your current AI and automation capabilities',
      icon: <Brain className="w-8 h-8" />,
      component: <AIReadinessAssessment leadData={leadData} />
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setShowResults(true);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleStepData = (stepId: string, data: any) => {
    setAssessmentData(prev => ({
      ...prev,
      [stepId]: data
    }));
  };

  if (showResults) {
    return (
      <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Brain className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Assessment Complete!
          </h2>
          <p className="text-xl text-gray-600">
            Your AI Marketing Intelligence Report is ready
          </p>
        </div>

        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
            Next Steps: Activate Your AI Marketing Team
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <MessageCircle className="w-8 h-8 text-blue-600 mb-3" />
              <h4 className="font-semibold text-gray-900 mb-2">
                Schedule AI Strategy Session
              </h4>
              <p className="text-sm text-gray-600 mb-4">
                Get a personalized 30-minute consultation to discuss your AI implementation roadmap
              </p>
              <Button size="sm" className="w-full">
                Book Free Session
              </Button>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-purple-200">
              <div className="flex items-center justify-between mb-3">
                <Zap className="w-8 h-8 text-purple-600" />
                <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full font-semibold">
                  LIMITED TIME
                </span>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Join 25 Founding Co-Creators
              </h4>
              <div className="mb-3">
                <div className="text-2xl font-bold text-purple-600">
                  {coCreatorPlan ? pricingService.formatPrice(coCreatorPlan.price_inr, 'INR') : '₹29,000'}
                </div>
                <div className="text-xs text-gray-500 line-through">Regular: ₹1,67,000+</div>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                {coCreatorPlan?.description || 'Lifetime access to AI platform + direct product influence + priority support'}
              </p>
              <Button 
                size="sm" 
                className="w-full bg-purple-600 hover:bg-purple-700"
                onClick={() => setShowPaymentModal(true)}
              >
                Secure Founding Spot
              </Button>
              
              <div className="text-xs text-center text-gray-500 mt-2">
                ⚡ Only 12 spots remaining
              </div>
            </div>
          </div>
        </div>

        <div className="text-center">
          <Button onClick={onClose} variant="outline" className="mr-4">
            Close Assessment
          </Button>
          <Button onClick={() => {
            // For now, just call onComplete - you can add AI Report Modal here too if needed
            onComplete?.(assessmentData);
          }}>
            Get Full AI Report
          </Button>
        </div>
      </div>
    );
  }

  const currentStepData = steps[currentStep];

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
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
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
      {currentStep > 0 && (
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

      {/* Payment Details Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full overflow-hidden transform transition-all">
            {/* Header */}
            <div className="bg-purple-600 p-6 text-center">
              <h2 className="text-2xl font-bold text-white mb-2">
                🚀 Co-Creator Program
              </h2>
              <p className="text-purple-100 text-sm">
                Join the elite group of founding members
              </p>
            </div>
            
            <div className="p-8">
              {/* Pricing */}
              <div className="bg-purple-50 rounded-lg p-6 text-center mb-6 border border-purple-100">
                <div className="text-4xl font-bold text-purple-700 mb-1">
                  {coCreatorPlan ? pricingService.formatPrice(coCreatorPlan.price_inr, 'INR') : '₹29,999'}
                </div>
                <div className="text-sm text-gray-500 line-through mb-2">
                  Regular Price: ₹1,67,000+
                </div>
                <div className="inline-block bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full">
                  🔥 Founding Member Price • ⚡ Only 12 spots left
                </div>
              </div>
              
              {/* Benefits Summary */}
              <div className="space-y-3 mb-8">
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-700 text-sm">Lifetime access to Unitasa AI Platform</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-700 text-sm">Direct influence on product roadmap</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-700 text-sm">Priority support & early access to features</span>
                </div>
              </div>
              
              {/* Actions */}
              <div className="space-y-3">
                <Button 
                  onClick={handleSecurePayment}
                  disabled={paymentLoading}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-lg py-6 shadow-lg shadow-purple-200"
                >
                  {paymentLoading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Processing...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <CreditCard className="w-5 h-5 mr-2" />
                      Secure My Spot Now
                    </div>
                  )}
                </Button>
                
                <button
                  onClick={() => setShowPaymentModal(false)}
                  disabled={paymentLoading}
                  className="w-full py-3 text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors"
                >
                  No, I'll miss this opportunity
                </button>
              </div>
              
              {/* Security Note */}
              <div className="mt-6 text-center flex items-center justify-center text-xs text-gray-400">
                <Shield className="w-3 h-3 mr-1" />
                Secure payment powered by Razorpay • 256-bit SSL encryption
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success State */}
      {paymentSuccess && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-auto text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to the Co-Creator Program!</h3>
            <p className="text-gray-600 mb-6">
              Your payment was successful. You'll receive onboarding instructions via email shortly.
            </p>
            <Button
              onClick={() => {
                setPaymentSuccess(false);
                setShowPaymentModal(false);
              }}
              className="w-full"
            >
              Continue
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedAIAssessment;
