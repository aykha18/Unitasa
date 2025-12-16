import { useState, useEffect } from 'react';

export type IndustryType = 'saas' | 'ecommerce' | 'consulting' | 'healthcare' | 'finance' | 'education' | 'other';

interface IndustryData {
  industry: IndustryType;
  valueProposition: string;
  keyBenefits: string[];
  useCase: string;
}

const INDUSTRY_DATA: Record<IndustryType, IndustryData> = {
  saas: {
    industry: 'saas',
    valueProposition: 'Convert more trial users to paying customers with AI-powered lead scoring and automated onboarding',
    keyBenefits: [
      'Reduce churn by 40% with predictive analytics',
      'Automate customer onboarding sequences',
      'Personalize user experiences at scale'
    ],
    useCase: 'Perfect for SaaS companies struggling with user activation and retention'
  },
  ecommerce: {
    industry: 'ecommerce',
    valueProposition: 'Turn abandoned carts into sales with AI-driven retargeting and personalized product recommendations',
    keyBenefits: [
      'Recover 25% of abandoned carts automatically',
      'Dynamic pricing optimization',
      'AI-powered inventory management'
    ],
    useCase: 'Ideal for online stores looking to maximize conversion rates'
  },
  consulting: {
    industry: 'consulting',
    valueProposition: 'Establish thought leadership and attract high-value clients with automated content creation and lead nurturing',
    keyBenefits: [
      'Generate 10x more qualified leads',
      'Automate proposal creation and follow-ups',
      'Build credibility with consistent expert content'
    ],
    useCase: 'Essential for consultants who need to scale their marketing without losing personal touch'
  },
  healthcare: {
    industry: 'healthcare',
    valueProposition: 'Build patient trust and streamline appointment booking with compliant AI communication',
    keyBenefits: [
      'HIPAA-compliant patient communication',
      'Automated appointment reminders and follow-ups',
      'AI-powered patient satisfaction monitoring'
    ],
    useCase: 'Critical for healthcare providers managing patient relationships at scale'
  },
  finance: {
    industry: 'finance',
    valueProposition: 'Comply with regulations while automating client onboarding and personalized financial advice',
    keyBenefits: [
      'Automated KYC and compliance workflows',
      'Personalized investment recommendations',
      'Risk assessment and portfolio optimization'
    ],
    useCase: 'Perfect for financial advisors and fintech companies'
  },
  education: {
    industry: 'education',
    valueProposition: 'Personalize learning experiences and automate student engagement with AI-powered education tools',
    keyBenefits: [
      'Adaptive learning path recommendations',
      'Automated student progress tracking',
      'Personalized content delivery'
    ],
    useCase: 'Transform online education with intelligent student engagement'
  },
  other: {
    industry: 'other',
    valueProposition: 'Transform your marketing with AI automation that adapts to your unique business needs',
    keyBenefits: [
      'Custom AI workflows for any industry',
      'Flexible automation that grows with you',
      'Expert support for implementation'
    ],
    useCase: 'For businesses ready to embrace AI-powered marketing transformation'
  }
};

export const useIndustryDetection = () => {
  const [detectedIndustry, setDetectedIndustry] = useState<IndustryType>('other');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const detectIndustry = async () => {
      try {
        // Check URL parameters first
        const urlParams = new URLSearchParams(window.location.search);
        const industryParam = urlParams.get('industry') as IndustryType;
        if (industryParam && INDUSTRY_DATA[industryParam]) {
          setDetectedIndustry(industryParam);
          setIsLoading(false);
          return;
        }

        // Check localStorage for previously detected industry
        const storedIndustry = localStorage.getItem('detectedIndustry') as IndustryType;
        if (storedIndustry && INDUSTRY_DATA[storedIndustry]) {
          setDetectedIndustry(storedIndustry);
          setIsLoading(false);
          return;
        }

        // Detect from timezone/geolocation (simplified)
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        // Indian timezone - could be any industry
        if (timezone.includes('Asia/Kolkata')) {
          // For Indian users, default to consulting (common for Indian market)
          setDetectedIndustry('consulting');
        }
        // European timezone - likely consulting or SaaS
        else if (timezone.includes('Europe/')) {
          setDetectedIndustry('consulting');
        }
        // US timezone - likely SaaS or e-commerce
        else if (timezone.includes('America/')) {
          setDetectedIndustry('saas');
        }
        // Default
        else {
          setDetectedIndustry('other');
        }

        // Store the detection
        localStorage.setItem('detectedIndustry', detectedIndustry);

      } catch (error) {
        console.warn('Industry detection failed:', error);
        setDetectedIndustry('other');
      } finally {
        setIsLoading(false);
      }
    };

    detectIndustry();
  }, []);

  const updateIndustry = (industry: IndustryType) => {
    setDetectedIndustry(industry);
    localStorage.setItem('detectedIndustry', industry);
  };

  return {
    industry: detectedIndustry,
    data: INDUSTRY_DATA[detectedIndustry],
    isLoading,
    updateIndustry,
    allIndustries: INDUSTRY_DATA
  };
};

export default useIndustryDetection;