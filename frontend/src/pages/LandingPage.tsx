import React, { useEffect, useState, Suspense, lazy } from 'react';
import { Layout } from '../components/layout';
import {
  HeroSection,
  BenefitCardsSection
} from '../components/sections';
import { CRMAssessmentResult } from '../types';
import { trackPageView } from '../utils/analytics';
import LeadCaptureForm, { LeadData } from '../components/assessment/LeadCaptureForm';
import CRMSelectorStep from '../components/assessment/CRMSelectorStep';
import ConsultationTest from '../components/test/ConsultationTest';
import { LandingPageAPI } from '../services/landingPageApi';

// Lazy load heavy components
const AICapabilitiesSection = lazy(() => import('../components/sections/AICapabilitiesSection'));
const FounderStorySection = lazy(() => import('../components/sections/FounderStorySection'));
const SocialProofSection = lazy(() => import('../components/sections/SocialProofSection'));
const MetaProofSection = lazy(() => import('../components/sections/MetaProofSection'));
const CRMMarketplaceSection = lazy(() => import('../components/sections/CRMMarketplaceSection'));
const ThoughtLeadershipSection = lazy(() => import('../components/sections/ThoughtLeadershipSection'));
const AssessmentModal = lazy(() => import('../components/assessment/AssessmentModal'));
const ChatWidget = lazy(() => import('../components/chat/ChatWidget'));
const ChatProvider = lazy(() => import('../components/chat/ChatProvider'));

// Chat Widget Container Component
const ChatWidgetContainer: React.FC = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isChatMinimized, setIsChatMinimized] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  return (
    <ChatWidget
      isOpen={isChatOpen}
      onToggle={() => setIsChatOpen(!isChatOpen)}
      onMinimize={() => setIsChatMinimized(!isChatMinimized)}
      isMinimized={isChatMinimized}
      unreadCount={unreadCount}
    />
  );
};

const LandingPage: React.FC = () => {
  const [isLeadCaptureOpen, setIsLeadCaptureOpen] = useState(false);
  const [isCRMSelectorOpen, setIsCRMSelectorOpen] = useState(false);
  const [isAssessmentOpen, setIsAssessmentOpen] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<CRMAssessmentResult | null>(null);
  const [leadData, setLeadData] = useState<LeadData | null>(null);


  useEffect(() => {
    trackPageView('/');

    // Listen for custom events to open assessment
    const handleOpenAssessment = () => {
      setIsAssessmentOpen(true);
    };

    // Listen for custom events to open lead capture
    const handleOpenLeadCapture = () => {
      setIsLeadCaptureOpen(true);
    };

    window.addEventListener('openAssessment', handleOpenAssessment);
    window.addEventListener('openLeadCapture', handleOpenLeadCapture);

    return () => {
      window.removeEventListener('openAssessment', handleOpenAssessment);
      window.removeEventListener('openLeadCapture', handleOpenLeadCapture);
    };
  }, []);

  const handleAssessmentComplete = (result: CRMAssessmentResult) => {
    setAssessmentResult(result);
    // Track conversion event
    console.log('Assessment completed:', result);
  };

  const openAssessment = () => {
    // First show lead capture form
    setIsLeadCaptureOpen(true);
  };

  const handleLeadCapture = (data: LeadData) => {
    console.log('Lead captured, opening CRM selector:', data);
    setLeadData(data);
    setIsLeadCaptureOpen(false);
    setIsCRMSelectorOpen(true);
  };

  const handleCRMSelection = (selectedCRM: string) => {
    console.log('CRM selected:', selectedCRM);
    if (leadData) {
      setLeadData({ ...leadData, preferredCRM: selectedCRM });
    }
    setIsCRMSelectorOpen(false);
    setIsAssessmentOpen(true);
  };

  const closeLeadCapture = () => {
    setIsLeadCaptureOpen(false);
  };

  const closeCRMSelector = () => {
    setIsCRMSelectorOpen(false);
  };

  const backToCRMSelector = () => {
    setIsAssessmentOpen(false);
    setIsCRMSelectorOpen(true);
  };

  const backToLeadCapture = () => {
    setIsCRMSelectorOpen(false);
    setIsLeadCaptureOpen(true);
  };

  const closeAssessment = () => {
    setIsAssessmentOpen(false);
  };

  const handleOpenConsultationBooking = () => {
    // Placeholder function to resolve JavaScript error
    console.log('Consultation booking feature coming soon');
    // Future implementation: open consultation booking modal
  };

  return (
    <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>}>
      <ChatProvider>
        <Layout>
          <div className="bg-white">
            <HeroSection onStartAssessment={openAssessment} />

            <BenefitCardsSection />

            <Suspense fallback={<div className="h-96 bg-gray-50 animate-pulse"></div>}>
              <AICapabilitiesSection />
            </Suspense>



            <Suspense fallback={<div className="h-96 bg-gray-50 animate-pulse"></div>}>
              <CRMMarketplaceSection />
            </Suspense>
            
            {/* <Suspense fallback={<div className="h-64 bg-gray-50 animate-pulse"></div>}>
              <SocialProofSection />
            </Suspense> */}

            <Suspense fallback={<div className="h-96 bg-gray-50 animate-pulse"></div>}>
              <MetaProofSection />
            </Suspense>

            {/* <Suspense fallback={<div className="h-96 bg-gray-50 animate-pulse"></div>}>
              <FounderStorySection />
            </Suspense> */}
            
            <Suspense fallback={<div className="h-64 bg-gray-50 animate-pulse"></div>}>
              <ThoughtLeadershipSection isCoCreator={assessmentResult?.readinessLevel === 'priority_integration'} />
            </Suspense>
            

            {/* Lead Capture Form */}
            <LeadCaptureForm
              isOpen={isLeadCaptureOpen}
              onClose={closeLeadCapture}
              onSubmit={handleLeadCapture}
            />

            {/* CRM Selector Step */}
            <CRMSelectorStep
              isOpen={isCRMSelectorOpen}
              onClose={closeCRMSelector}
              onNext={handleCRMSelection}
              onBack={backToLeadCapture}
            />

            {/* Assessment Modal */}
            {isAssessmentOpen && (
              <Suspense fallback={<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              </div>}>
                <AssessmentModal
                  isOpen={isAssessmentOpen}
                  onClose={closeAssessment}
                  onComplete={handleAssessmentComplete}
                  leadData={leadData}
                />
              </Suspense>
            )}

            {/* Chat Widget */}
            <Suspense fallback={null}>
              <ChatWidgetContainer />
            </Suspense>
          </div>
        </Layout>
      </ChatProvider>
    </Suspense>
  );
};

export default LandingPage;
