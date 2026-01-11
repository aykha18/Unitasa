import React, { useState, useEffect } from 'react';
import { PaymentResult, CoCreatorProfile } from '../../types';
import { pricingService } from '../../services/pricingService';
import Button from '../ui/Button';
import {
  CheckCircle,
  Crown,
  Download,
  Mail,
  Calendar,
  Users,
  Zap,
  Star,
  ArrowRight,
  Share2,
  ExternalLink,
  Gift,
  Sparkles
} from 'lucide-react';

interface PaymentConfirmationProps {
  paymentResult: PaymentResult;
  onContinue: () => void;
  className?: string;
}

const PaymentConfirmation: React.FC<PaymentConfirmationProps> = ({
  paymentResult,
  onContinue,
  className = '',
}) => {
  const [receiptUrl, setReceiptUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [price, setPrice] = useState('₹29,999');
  const [priceValue, setPriceValue] = useState(29999);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const plans = await pricingService.getAllPlans();
        const coCreatorPlan = plans.find(p => p.name === 'co_creator');
        if (coCreatorPlan) {
          setPrice(pricingService.formatPrice(coCreatorPlan.price_inr, 'INR'));
          setPriceValue(coCreatorPlan.price_inr);
        }
      } catch (error) {
        console.error('Failed to fetch pricing:', error);
      }
    };
    fetchPrice();
  }, []);

  useEffect(() => {
    loadCoCreatorProfile();
    generateReceipt();
  }, [paymentResult, priceValue]);

  const loadCoCreatorProfile = async () => {
    if (!paymentResult.coCreatorId) return;
    
    try {
      const response = await fetch(`/api/v1/landing/co-creator-program/${paymentResult.coCreatorId}/onboarding-status`);
      if (response.ok) {
        // Profile loaded successfully, just set loading to false
        setLoading(false);
      }
    } catch (error) {
      console.error('Failed to load co-creator profile:', error);
      setLoading(false);
    }
  };

  const generateReceipt = async () => {
    if (!paymentResult.paymentIntentId) return;
    
    try {
      // For now, we'll create a simple receipt URL
      // In a real implementation, this would generate a PDF receipt
      const receiptData = {
        paymentId: paymentResult.paymentIntentId,
        amount: priceValue,
        currency: 'INR',
        date: new Date().toISOString(),
        description: 'Co-Creator Program - Lifetime Access'
      };
      
      const blob = new Blob([JSON.stringify(receiptData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      setReceiptUrl(url);
    } catch (error) {
      console.error('Failed to generate receipt:', error);
    }
  };

  const handleShareSuccess = async () => {
    const shareText = `🎉 Just became a Co-Creator at Unitasa! Excited to help shape the future of AI marketing automation. #CoCreator #AIMarketing #AutoMark`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Unitasa Co-Creator',
          text: shareText,
          url: window.location.origin,
        });
      } catch (error) {
        console.log('Share cancelled or failed');
      }
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(shareText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const nextSteps = [
    {
      icon: Mail,
      title: 'Check Your Email',
      description: 'Welcome email with exclusive co-creator resources sent to your inbox',
      action: 'Open Email',
      urgent: true
    },
    {
      icon: Users,
      title: 'Join Co-Creator Community',
      description: 'Access exclusive Slack workspace with other co-creators and the founder',
      action: 'Join Community',
      urgent: true
    },
    {
      icon: Calendar,
      title: 'Schedule Integration Setup',
      description: 'Book your priority CRM integration consultation call',
      action: 'Schedule Call',
      urgent: false
    },
    {
      icon: Star,
      title: 'Influence Roadmap',
      description: 'Vote on upcoming features and submit your integration requests',
      action: 'View Roadmap',
      urgent: false
    }
  ];

  const benefits = [
    { icon: Crown, text: 'Lifetime platform access activated', active: true },
    { icon: Zap, text: 'Priority CRM integration support', active: true },
    { icon: Users, text: 'Exclusive co-creator community access', active: true },
    { icon: Star, text: 'Product roadmap voting rights', active: true },
    { icon: Gift, text: 'Early access to new features', active: true },
    { icon: Sparkles, text: 'Co-creator badge and recognition', active: true }
  ];

  if (loading) {
    return (
      <div className={`bg-gradient-to-br from-green-900 via-primary-800 to-secondary-900 rounded-2xl p-8 text-white ${className}`}>
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-white/20 border-t-white rounded-full mx-auto mb-4"></div>
          <p className="text-lg">Setting up your co-creator profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-br from-green-900 via-primary-800 to-secondary-900 rounded-2xl overflow-hidden ${className}`}>
      {/* Celebration Background */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-1/4 w-32 h-32 bg-yellow-400 rounded-full animate-pulse"></div>
        <div className="absolute top-1/4 right-1/4 w-24 h-24 bg-green-400 rounded-full animate-pulse delay-1000"></div>
        <div className="absolute bottom-1/4 left-1/3 w-20 h-20 bg-blue-400 rounded-full animate-pulse delay-2000"></div>
      </div>

      <div className="relative z-10 p-8 text-white">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
            Welcome, Co-Creator! 🎉
          </h1>
          
          <p className="text-xl md:text-2xl opacity-90 mb-2">
            Your payment was successful and your lifetime access is now active
          </p>
          
          <div className="inline-flex items-center bg-green-500/20 border border-green-400 rounded-full px-6 py-2">
            <Crown className="w-5 h-5 text-yellow-400 mr-2" />
            <span className="font-semibold">Co-Creator #{paymentResult.coCreatorId?.slice(-4)}</span>
          </div>
        </div>

        {/* Payment Details */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <CheckCircle className="w-6 h-6 text-green-400 mr-2" />
            Payment Confirmed
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-300">Amount Paid:</span>
                  <span className="font-semibold">{price}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Payment ID:</span>
                  <span className="font-mono text-sm">{paymentResult.paymentIntentId?.slice(-8)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Date:</span>
                  <span>{new Date().toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Status:</span>
                  <span className="text-green-400 font-semibold">Completed</span>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col justify-center">
              {receiptUrl && (
                <Button
                  variant="outline"
                  className="mb-3"
                  icon={Download}
                  iconPosition="left"
                  onClick={() => {
                    const link = document.createElement('a');
                    link.href = receiptUrl;
                    link.download = `co-creator-receipt-${paymentResult.paymentIntentId}.pdf`;
                    link.click();
                  }}
                >
                  Download Receipt
                </Button>
              )}
              
              <Button
                variant="outline"
                icon={copied ? CheckCircle : Share2}
                iconPosition="left"
                onClick={handleShareSuccess}
                className={copied ? 'text-green-400 border-green-400' : ''}
              >
                {copied ? 'Copied!' : 'Share Success'}
              </Button>
            </div>
          </div>
        </div>

        {/* Active Benefits */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <Sparkles className="w-6 h-6 text-yellow-400 mr-2" />
            Your Co-Creator Benefits (Now Active)
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-center p-3 bg-white/5 rounded-lg">
                <benefit.icon className="w-5 h-5 text-green-400 mr-3" />
                <span className="text-sm">{benefit.text}</span>
                {benefit.active && (
                  <CheckCircle className="w-4 h-4 text-green-400 ml-auto" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <ArrowRight className="w-6 h-6 text-blue-400 mr-2" />
            Your Next Steps
          </h2>
          
          <div className="space-y-4">
            {nextSteps.map((step, index) => (
              <div key={index} className={`flex items-center p-4 rounded-lg border ${
                step.urgent 
                  ? 'bg-yellow-500/10 border-yellow-400/30' 
                  : 'bg-white/5 border-white/20'
              }`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 ${
                  step.urgent ? 'bg-yellow-500/20' : 'bg-blue-500/20'
                }`}>
                  <step.icon className={`w-5 h-5 ${
                    step.urgent ? 'text-yellow-400' : 'text-blue-400'
                  }`} />
                </div>
                
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">{step.title}</h3>
                  <p className="text-sm text-gray-300">{step.description}</p>
                </div>
                
                <Button
                  variant={step.urgent ? 'primary' : 'outline'}
                  size="sm"
                  icon={ExternalLink}
                  iconPosition="right"
                  className={step.urgent ? 'bg-yellow-500 text-black hover:bg-yellow-400' : ''}
                >
                  {step.action}
                </Button>
              </div>
            ))}
          </div>
        </div>

        {/* Welcome Message */}
        <div className="text-center bg-gradient-to-r from-primary-600/20 to-secondary-600/20 rounded-xl p-6 border border-primary-400/30 mb-8">
          <h2 className="text-2xl font-bold mb-4">A Personal Message from the Founder</h2>
          <blockquote className="text-lg italic opacity-90 mb-4">
            "Welcome to the Co-Creator family! Your support and insights will directly shape how Unitasa evolves. 
            I'm personally committed to making sure your CRM integration experience is seamless and that your voice 
            is heard in every product decision. Thank you for believing in this vision."
          </blockquote>
          <div className="flex items-center justify-center">
            <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mr-3">
              <span className="text-white font-bold">JD</span>
            </div>
            <div className="text-left">
              <div className="font-semibold">John Doe</div>
              <div className="text-sm text-gray-300">Founder & CEO, Unitasa</div>
            </div>
          </div>
        </div>

        {/* Continue Button */}
        <div className="text-center">
          <Button
            variant="primary"
            size="lg"
            className="bg-gradient-to-r from-green-400 to-blue-400 text-black hover:from-green-300 hover:to-blue-300 font-bold text-lg px-12 py-4"
            icon={ArrowRight}
            iconPosition="right"
            onClick={onContinue}
          >
            Access Your Co-Creator Dashboard
          </Button>
          
          <p className="text-sm text-gray-400 mt-4">
            Your journey as a Co-Creator begins now. Let's build the future together! 🚀
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentConfirmation;
