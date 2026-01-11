import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { CRMAssessmentResult, CRMIntegration } from '../../types';
import ScoreVisualization from './ScoreVisualization';
import RecommendationsList from './RecommendationsList';
import NextStepsSection from './NextStepsSection';
import CoCreatorProgramOffer from './CoCreatorProgramOffer';
import ResultsSharing from './ResultsSharing';
import CRMSpecificRecommendations from './CRMSpecificRecommendations';
import IndustryBenchmark from './IndustryBenchmark';
import AutomationOpportunityCard from './AutomationOpportunityCard';
import ResultsSummaryCard from './ResultsSummaryCard';
import RazorpayCheckout from '../payment/RazorpayCheckout';
import Button from '../ui/Button';
import LandingPageAPI from '../../services/landingPageApi';
import { X, Download, Share2, Target, Zap, Settings, CheckCircle } from 'lucide-react';

interface AssessmentResultsProps {
  result: CRMAssessmentResult;
  onClose?: () => void;
}

export const AssessmentResults: React.FC<AssessmentResultsProps> = ({
  result,
  onClose,
}) => {
  const [supportedCRMs, setSupportedCRMs] = useState<CRMIntegration[]>([]);
  const [, setLoading] = useState(true);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Normalize property names to handle both camelCase and snake_case
  const normalizedResult = {
    currentCRM: result.currentCRM || (result as any).current_crm || 'Unknown',
    integrationScore: result.integrationScore || (result as any).overall_score || 0,
    readinessLevel: result.readinessLevel || (result as any).readiness_level || 'nurture_with_guides',
    integrationRecommendations: result.integrationRecommendations || (result as any).integration_recommendations || [],
    automationOpportunities: result.automationOpportunities || (result as any).automation_opportunities || [],
    technicalRequirements: result.technicalRequirements || (result as any).technical_requirements || [],
    nextSteps: result.nextSteps || (result as any).next_steps || []
  };

  useEffect(() => {
    loadSupportedCRMs();
  }, []);

  // Auto-hide success toast removed as we use react-hot-toast now

  const loadSupportedCRMs = async () => {
    try {
      const crms = await LandingPageAPI.getSupportedCRMs();
      setSupportedCRMs(crms);
    } catch (error) {
      console.error('Failed to load supported CRMs:', error);
    } finally {
      setLoading(false);
    }
  };
  const getReadinessLevelInfo = () => {
    switch (normalizedResult.readinessLevel) {
      case 'priority_integration':
        return {
          title: 'Priority Integration Ready',
          description: 'Your business is highly ready for AI marketing automation',
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          icon: <Zap className="w-6 h-6 text-green-600" />,
        };
      case 'co_creator_qualified':
        return {
          title: 'Co-Creator Program Qualified',
          description: 'You\'re ready to join our exclusive co-creator program',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          icon: <Target className="w-6 h-6 text-blue-600" />,
        };
      case 'nurture_with_guides':
        return {
          title: 'Foundation Building Phase',
          description: 'Let\'s strengthen your foundation for AI automation',
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          icon: <Settings className="w-6 h-6 text-yellow-600" />,
        };
      default:
        return {
          title: 'Assessment Complete',
          description: 'Here are your personalized results',
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          icon: <Target className="w-6 h-6 text-gray-600" />,
        };
    }
  };

  const getCurrentCRMInfo = () => {
    return supportedCRMs.find(crm => 
      crm.name.toLowerCase() === normalizedResult.currentCRM.toLowerCase()
    );
  };

  const getPersonalizedInsights = () => {
    const crmInfo = getCurrentCRMInfo();
    const insights = [];

    // Score-based insights with specific recommendations
    if (normalizedResult.integrationScore >= 71) {
      insights.push(`🚀 Excellent! Your ${normalizedResult.currentCRM} setup is ready for advanced AI automation with predictive lead scoring and automated nurturing sequences.`);
      insights.push(`🎯 You're qualified for priority integration support with direct founder consultation.`);
    } else if (normalizedResult.integrationScore >= 41) {
      insights.push(`📈 Good foundation! Your ${normalizedResult.currentCRM} has solid potential for automation with some optimization.`);
      insights.push(`🔧 Focus on data quality improvements and workflow automation to reach the next level.`);
    } else {
      insights.push(`🏗️ Building phase! Let's optimize your ${normalizedResult.currentCRM} foundation for better automation readiness.`);
      insights.push(`📚 Start with our CRM strategy guide to strengthen your data structure and processes.`);
    }

    // CRM-specific insights with actionable next steps
    if (crmInfo) {
      if (crmInfo.setupComplexity === 'easy') {
        insights.push(`⚡ Great news! ${normalizedResult.currentCRM} has straightforward integration options - you could be automated within ${crmInfo.setupTimeMinutes} minutes.`);
      } else if (crmInfo.setupComplexity === 'medium') {
        insights.push(`🔨 ${normalizedResult.currentCRM} integration requires some technical setup (${crmInfo.setupTimeMinutes} minutes) but offers powerful automation capabilities.`);
      } else {
        insights.push(`🏢 ${normalizedResult.currentCRM} is enterprise-grade with advanced features - perfect for sophisticated automation workflows once configured.`);
      }
    }

    // Add automation opportunity insights
    if (normalizedResult.automationOpportunities && normalizedResult.automationOpportunities.length > 0) {
      insights.push(`💡 We identified ${normalizedResult.automationOpportunities.length} specific automation opportunities in your current setup.`);
    }

    return insights;
  };

  const levelInfo = getReadinessLevelInfo();

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Your AI Readiness Assessment Results
          </h1>
          <div className={`inline-flex items-center px-4 py-2 rounded-full border ${levelInfo.bgColor} ${levelInfo.borderColor}`}>
            {levelInfo.icon}
            <span className={`font-semibold ${levelInfo.color} ml-2`}>
              {levelInfo.title}
            </span>
          </div>
          <p className="text-gray-600 mt-2">{levelInfo.description}</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            icon={Share2}
            iconPosition="left"
            onClick={() => {/* Handle sharing */}}
          >
            Share
          </Button>
          <Button
            variant="outline"
            icon={Download}
            iconPosition="left"
            onClick={() => {/* Handle export */}}
          >
            Export
          </Button>
          {onClose && (
            <Button
              variant="ghost"
              icon={X}
              onClick={onClose}
            >
              Close
            </Button>
          )}
        </div>
      </div>

      {/* Results Summary Card */}
      <div className="mb-8">
        <ResultsSummaryCard result={result} />
      </div>

      {/* Personalized Insights */}
      <div className="mb-8">
        <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6 border border-primary-100">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Personalized Insights for Your Business</h2>
          <div className="space-y-3">
            {getPersonalizedInsights().map((insight, index) => (
              <div key={index} className="flex items-start">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <p className="text-gray-700">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Score Visualization */}
      <div className="mb-8">
        <ScoreVisualization
          score={normalizedResult.integrationScore}
          readinessLevel={normalizedResult.readinessLevel}
          currentCRM={normalizedResult.currentCRM}
        />
      </div>

      {/* Industry Benchmark Comparison */}
      <div className="mb-8">
        <IndustryBenchmark
          score={normalizedResult.integrationScore}
          currentCRM={normalizedResult.currentCRM}
          readinessLevel={normalizedResult.readinessLevel}
        />
      </div>

      {/* CRM-Specific Integration Plan */}
      <div className="mb-8">
        <CRMSpecificRecommendations
          result={result}
          crmInfo={getCurrentCRMInfo()}
        />
      </div>

      {/* Enhanced Automation Opportunities */}
      <div className="mb-8">
        <AutomationOpportunityCard
          opportunities={normalizedResult.automationOpportunities}
          currentCRM={normalizedResult.currentCRM}
          readinessLevel={normalizedResult.readinessLevel}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column */}
        <div className="space-y-8">
          {/* Integration Recommendations */}
          <RecommendationsList
            title="Integration Recommendations"
            items={normalizedResult.integrationRecommendations}
            icon="🔗"
          />

          {/* Technical Requirements */}
          <RecommendationsList
            title="Technical Requirements"
            items={normalizedResult.technicalRequirements}
            icon="⚙️"
          />
        </div>

        {/* Right Column */}
        <div className="space-y-8">
          {/* Next Steps */}
          <NextStepsSection
            steps={normalizedResult.nextSteps}
            readinessLevel={normalizedResult.readinessLevel}
            onStartPayment={() => setShowPaymentModal(true)}
          />
        </div>
      </div>

      {/* Co-Creator Program Offer (for qualified leads) */}
      {(normalizedResult.readinessLevel === 'co_creator_qualified' || normalizedResult.readinessLevel === 'priority_integration') && (
        <div className="mt-12">
          <CoCreatorProgramOffer
            readinessLevel={normalizedResult.readinessLevel}
            score={normalizedResult.integrationScore}
          />
        </div>
      )}

      {/* Results Sharing */}
      <div className="mt-12">
        <ResultsSharing result={result} />
      </div>

      {/* Payment Modal */}
      {showPaymentModal && !paymentSuccess && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="relative">
            <RazorpayCheckout
              onSuccess={(paymentData) => {
                console.log('Payment successful:', paymentData);
                setPaymentSuccess(true);
                setShowPaymentModal(false);
                // Show success message with modern toast
                toast.success(`Payment successful! Welcome to the Co-Creator Program!\n\nTransaction ID: ${paymentData.transactionId}`, {
                  duration: 6000
                });
                toast.success("You'll receive onboarding instructions via email shortly.", {
                  duration: 6000,
                  icon: '📧'
                });
              }}
              onError={(error) => {
                console.error('Payment error:', error);
                toast.error(`Payment failed: ${error}`);
                toast.error('Please try again or contact support@unitasa.in');
              }}
              onCancel={() => {
                setShowPaymentModal(false);
              }}
              customerEmail=""
              customerName=""
            />
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

      {/* Modern Success Toast - Removed as we use react-hot-toast now */}
    </div>
  );
};

export default AssessmentResults;
