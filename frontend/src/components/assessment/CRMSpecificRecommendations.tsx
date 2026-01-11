import React from 'react';
import { toast } from 'react-hot-toast';
import { CRMAssessmentResult, CRMIntegration } from '../../types';
import { ExternalLink, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import Button from '../ui/Button';

interface CRMSpecificRecommendationsProps {
  result: CRMAssessmentResult;
  crmInfo?: CRMIntegration;
}

const CRMSpecificRecommendations: React.FC<CRMSpecificRecommendationsProps> = ({
  result,
  crmInfo,
}) => {
  // Normalize property names to handle both camelCase and snake_case
  const normalizedResult = {
    currentCRM: result.currentCRM || (result as any).current_crm || 'Unknown',
    readinessLevel: result.readinessLevel || (result as any).readiness_level || 'nurture_with_guides'
  };

  const getIntegrationComplexityInfo = () => {
    if (!crmInfo) return null;

    const complexityConfig = {
      easy: {
        icon: <CheckCircle className="w-5 h-5 text-green-500" />,
        color: 'text-green-700',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        description: 'Quick setup with minimal technical requirements'
      },
      medium: {
        icon: <Clock className="w-5 h-5 text-yellow-500" />,
        color: 'text-yellow-700',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        description: 'Moderate setup requiring some technical configuration'
      },
      advanced: {
        icon: <AlertCircle className="w-5 h-5 text-red-500" />,
        color: 'text-red-700',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        description: 'Advanced setup with enterprise-level configuration'
      }
    };

    return complexityConfig[crmInfo.setupComplexity];
  };

  const getCRMSpecificSteps = () => {
    if (!crmInfo) return [];

    const baseSteps = [
      'Verify API access and permissions in your CRM',
      'Configure field mapping for contacts and deals',
      'Set up automation triggers and workflows',
      'Test integration with sample data',
      'Launch automated marketing campaigns'
    ];

    // Add CRM-specific steps with more detail
    const crmSpecificSteps: Record<string, string[]> = {
      'Pipedrive': [
        'Enable API access in Pipedrive Settings → Personal Preferences → API',
        'Generate API token with full permissions (read/write access)',
        'Configure webhook endpoints for real-time sync (deals, persons, activities)',
        'Set up custom fields for AI lead scoring and automation tags',
        'Map Pipedrive pipeline stages to Unitasa automation triggers',
        ...baseSteps.slice(1)
      ],
      'HubSpot': [
        'Install Unitasa app from HubSpot App Marketplace',
        'Grant necessary permissions: contacts, deals, companies, and workflows',
        'Configure custom properties for AI insights and lead scoring',
        'Set up HubSpot workflows to trigger Unitasa automations',
        'Enable contact and deal sync with bidirectional updates',
        ...baseSteps.slice(1)
      ],
      'Salesforce': [
        'Create connected app in Salesforce Setup → App Manager',
        'Configure OAuth2 authentication with appropriate scopes',
        'Set up custom fields for automation data and AI insights',
        'Install Unitasa managed package from AppExchange',
        'Configure Process Builder flows for automation triggers',
        ...baseSteps.slice(1)
      ],
      'Zoho': [
        'Enable API access in Zoho CRM Setup → Developer Space → APIs',
        'Generate OAuth2 credentials with CRM.modules.ALL scope',
        'Configure custom modules for automation tracking if needed',
        'Set up Zoho Flow integrations for real-time sync',
        'Map Zoho CRM stages to Unitasa automation sequences',
        ...baseSteps.slice(1)
      ],
      'Monday': [
        'Install Unitasa integration from Monday.com marketplace',
        'Configure board permissions and access for relevant workspaces',
        'Map Monday board items to CRM entities (leads, deals, contacts)',
        'Set up Monday automations to trigger Unitasa workflows',
        'Configure status column mapping for lead progression tracking',
        ...baseSteps.slice(1)
      ]
    };

    return crmSpecificSteps[crmInfo.name] || baseSteps;
  };

  const getEstimatedROI = () => {
    if (!result || !crmInfo) return null;

    const baseROI = {
      timesSaved: '15-25 hours/week',
      leadIncrease: '40-60%',
      conversionImprovement: '25-35%',
      paybackPeriod: '2-3 months'
    };

    // Adjust based on readiness level
    if (normalizedResult.readinessLevel === 'priority_integration') {
      return {
        timesSaved: '25-35 hours/week',
        leadIncrease: '60-80%',
        conversionImprovement: '35-50%',
        paybackPeriod: '1-2 months'
      };
    } else if (normalizedResult.readinessLevel === 'co_creator_qualified') {
      return baseROI;
    } else {
      return {
        timesSaved: '10-15 hours/week',
        leadIncrease: '25-40%',
        conversionImprovement: '15-25%',
        paybackPeriod: '3-4 months'
      };
    }
  };

  const complexityInfo = getIntegrationComplexityInfo();

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          {normalizedResult.currentCRM} Integration Plan
        </h3>
        {crmInfo && (
          <div className={`inline-flex items-center px-3 py-1 rounded-full border ${complexityInfo?.bgColor} ${complexityInfo?.borderColor}`}>
            {complexityInfo?.icon}
            <span className={`text-sm font-medium ml-2 ${complexityInfo?.color}`}>
              {crmInfo.setupComplexity.charAt(0).toUpperCase() + crmInfo.setupComplexity.slice(1)} Setup
            </span>
          </div>
        )}
      </div>

      {complexityInfo && (
        <div className={`p-4 rounded-lg border mb-6 ${complexityInfo.bgColor} ${complexityInfo.borderColor}`}>
          <p className={`text-sm ${complexityInfo.color}`}>
            {complexityInfo.description}
          </p>
          {crmInfo && (
            <p className={`text-sm mt-2 ${complexityInfo.color}`}>
              Estimated setup time: {crmInfo.setupTimeMinutes} minutes
            </p>
          )}
        </div>
      )}

      <div className="space-y-4 mb-6">
        <h4 className="font-semibold text-gray-900">Integration Steps:</h4>
        {getCRMSpecificSteps().map((step, index) => (
          <div key={index} className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-semibold mr-3">
              {index + 1}
            </div>
            <p className="text-gray-700 leading-relaxed pt-1">{step}</p>
          </div>
        ))}
      </div>

      {crmInfo && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button
            variant="primary"
            icon={ExternalLink}
            iconPosition="left"
            className="w-full"
            onClick={() => {
              toast(`${normalizedResult.currentCRM} integration setup coming soon!`, { icon: '🚀' });
            }}
          >
            Start {normalizedResult.currentCRM} Integration
          </Button>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => {
              console.log(`View ${normalizedResult.currentCRM} Documentation clicked`);
              window.open(`/crm-documentation/${normalizedResult.currentCRM.toLowerCase()}`, '_blank');
            }}
          >
            View Documentation
          </Button>
        </div>
      )}

      {/* Estimated ROI Section */}
      {getEstimatedROI() && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="font-semibold text-gray-900 mb-4">Estimated ROI with Unitasa Integration</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(getEstimatedROI()!).map(([key, value], index) => (
              <div key={index} className="text-center p-3 bg-primary-50 rounded-lg">
                <div className="text-lg font-bold text-primary-600">{value}</div>
                <div className="text-xs text-gray-600 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {crmInfo && crmInfo.features && crmInfo.features.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="font-semibold text-gray-900 mb-3">Available Integration Features:</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {crmInfo.features.slice(0, 8).map((feature, index) => (
              <div key={index} className="flex items-center text-sm text-gray-700 bg-gray-50 px-3 py-2 rounded">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                {feature}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CRMSpecificRecommendations;
