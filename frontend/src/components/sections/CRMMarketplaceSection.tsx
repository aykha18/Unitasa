import React, { useState } from 'react';
import { 
  CheckCircle, 
  Clock, 
  Star, 
  ExternalLink, 
  Play, 
  Settings, 
  Zap,
  Shield,
  Code,
  BookOpen,
  RefreshCw,
  AlertCircle,
  Activity
} from 'lucide-react';
import { Card, Button } from '../ui';
import CRMDemoModal from '../crm/CRMDemoModal';
import CRMSetupWizard from '../crm/CRMSetupWizard';

interface CRMConnector {
  id: string;
  name: string;
  logo: string;
  status: 'available' | 'beta' | 'coming_soon';
  setupComplexity: 'easy' | 'medium' | 'advanced';
  setupTimeMinutes: number;
  rating: number;
  reviews: number;
  features: {
    contacts: boolean;
    deals: boolean;
    activities: boolean;
    campaigns: boolean;
    analytics: boolean;
    webhooks: boolean;
  };
  authMethod: 'OAuth2' | 'API_Key' | 'JWT';
  documentation: string;
  demoAvailable: boolean;
  description: string;
  pricing: string;
  healthScore?: number;
  connectionStatus?: 'connected' | 'disconnected' | 'error' | 'syncing';
}

const CRMMarketplaceSection: React.FC = () => {
  const [viewMode, setViewMode] = useState<'gallery' | 'comparison'>('gallery');
  const [selectedDemo, setSelectedDemo] = useState<CRMConnector | null>(null);
  const [selectedSetup, setSelectedSetup] = useState<CRMConnector | null>(null);

  const crmConnectors: CRMConnector[] = [
    {
      id: 'pipedrive',
      name: 'Pipedrive',
      logo: '🔶',
      status: 'available',
      setupComplexity: 'easy',
      setupTimeMinutes: 5,
      rating: 4.8,
      reviews: 1250,
      features: {
        contacts: true,
        deals: true,
        activities: true,
        campaigns: true,
        analytics: true,
        webhooks: true,
      },
      authMethod: 'OAuth2',
      documentation: '/docs/pipedrive',
      demoAvailable: true,
      description: 'Visual sales pipeline with excellent API support and comprehensive automation features.',
      pricing: 'Free tier available',
      healthScore: 98,
      connectionStatus: 'connected'
    },
    {
      id: 'hubspot',
      name: 'HubSpot',
      logo: '🟠',
      status: 'available',
      setupComplexity: 'easy',
      setupTimeMinutes: 3,
      rating: 4.9,
      reviews: 2100,
      features: {
        contacts: true,
        deals: true,
        activities: true,
        campaigns: true,
        analytics: true,
        webhooks: true,
      },
      authMethod: 'OAuth2',
      documentation: '/docs/hubspot',
      demoAvailable: true,
      description: 'All-in-one marketing, sales, and service platform with robust integration capabilities.',
      pricing: 'Free tier available',
      healthScore: 95,
      connectionStatus: 'syncing'
    },
    {
      id: 'zoho',
      name: 'Zoho CRM',
      logo: '🔵',
      status: 'available',
      setupComplexity: 'medium',
      setupTimeMinutes: 8,
      rating: 4.6,
      reviews: 890,
      features: {
        contacts: true,
        deals: true,
        activities: true,
        campaigns: true,
        analytics: true,
        webhooks: true,
      },
      authMethod: 'OAuth2',
      documentation: '/docs/zoho',
      demoAvailable: true,
      description: 'Comprehensive business suite with powerful CRM and extensive customization options.',
      pricing: 'Free tier available',
      healthScore: 92,
      connectionStatus: 'connected'
    },
    {
      id: 'monday',
      name: 'Monday.com',
      logo: '🟣',
      status: 'available',
      setupComplexity: 'easy',
      setupTimeMinutes: 4,
      rating: 4.7,
      reviews: 1560,
      features: {
        contacts: true,
        deals: true,
        activities: true,
        campaigns: false,
        analytics: true,
        webhooks: true,
      },
      authMethod: 'OAuth2',
      documentation: '/docs/monday',
      demoAvailable: true,
      description: 'Visual project management platform with CRM capabilities and modern interface.',
      pricing: 'Free tier available',
      healthScore: 88,
      connectionStatus: 'disconnected'
    },
    {
      id: 'salesforce',
      name: 'Salesforce',
      logo: '☁️',
      status: 'available',
      setupComplexity: 'advanced',
      setupTimeMinutes: 15,
      rating: 4.5,
      reviews: 3200,
      features: {
        contacts: true,
        deals: true,
        activities: true,
        campaigns: true,
        analytics: true,
        webhooks: true,
      },
      authMethod: 'OAuth2',
      documentation: '/docs/salesforce',
      demoAvailable: true,
      description: 'Enterprise-grade CRM with extensive customization and advanced automation features.',
      pricing: 'Paid plans only',
      healthScore: 96,
      connectionStatus: 'connected'
    },
    {
      id: 'airtable',
      name: 'Airtable',
      logo: '🟡',
      status: 'beta',
      setupComplexity: 'medium',
      setupTimeMinutes: 10,
      rating: 4.4,
      reviews: 670,
      features: {
        contacts: true,
        deals: false,
        activities: true,
        campaigns: false,
        analytics: false,
        webhooks: true,
      },
      authMethod: 'API_Key',
      documentation: '/docs/airtable',
      demoAvailable: false,
      description: 'Flexible database platform with CRM templates and powerful automation capabilities.',
      pricing: 'Free tier available',
      healthScore: 75,
      connectionStatus: 'error'
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'available':
        return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">Available</span>;
      case 'beta':
        return <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">Beta</span>;
      case 'coming_soon':
        return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium">Coming Soon</span>;
      default:
        return null;
    }
  };

  const getComplexityBadge = (complexity: string) => {
    switch (complexity) {
      case 'easy':
        return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">Easy Setup</span>;
      case 'medium':
        return <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">Medium Setup</span>;
      case 'advanced':
        return <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">Advanced Setup</span>;
      default:
        return null;
    }
  };

  const getConnectionStatusBadge = (status?: string) => {
    if (!status) return null;
    
    switch (status) {
      case 'connected':
        return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium flex items-center">
          <CheckCircle className="w-3 h-3 mr-1" />
          Connected
        </span>;
      case 'syncing':
        return <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium flex items-center">
          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
          Syncing
        </span>;
      case 'error':
        return <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium flex items-center">
          <AlertCircle className="w-3 h-3 mr-1" />
          Error
        </span>;
      case 'disconnected':
        return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium">
          Disconnected
        </span>;
      default:
        return null;
    }
  };

  const renderGalleryView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {crmConnectors.map((crm) => (
        <Card key={crm.id} className="p-6" hover>
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">{crm.logo}</div>
              <div>
                <h3 className="font-semibold text-gray-900">{crm.name}</h3>
                <div className="flex items-center space-x-2 mt-1 flex-wrap gap-1">
                  {getStatusBadge(crm.status)}
                  {getComplexityBadge(crm.setupComplexity)}
                  {getConnectionStatusBadge(crm.connectionStatus)}
                </div>
              </div>
            </div>
          </div>

          {/* Health Score */}
          {crm.healthScore && (
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Health Score</span>
                <span className={`text-xs font-semibold ${
                  crm.healthScore >= 90 ? 'text-green-600' : 
                  crm.healthScore >= 70 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {crm.healthScore}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${
                    crm.healthScore >= 90 ? 'bg-green-500' :
                    crm.healthScore >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${crm.healthScore}%` }}
                />
              </div>
            </div>
          )}

          {/* Rating */}
          <div className="flex items-center space-x-2 mb-3">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(crm.rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-600">
              {crm.rating} ({crm.reviews} reviews)
            </span>
          </div>

          {/* Description */}
          <p className="text-gray-600 text-sm mb-4">{crm.description}</p>

          {/* Setup Info */}
          <div className="flex items-center justify-between mb-4 text-sm">
            <div className="flex items-center text-gray-500">
              <Clock className="w-4 h-4 mr-1" />
              {crm.setupTimeMinutes} min setup
            </div>
            <div className="flex items-center text-gray-500">
              <Shield className="w-4 h-4 mr-1" />
              {crm.authMethod}
            </div>
          </div>

          {/* Features Preview */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            {Object.entries(crm.features).slice(0, 6).map(([feature, supported]) => (
              <div key={feature} className="flex items-center text-xs">
                {supported ? (
                  <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                ) : (
                  <div className="w-3 h-3 rounded-full bg-gray-300 mr-1" />
                )}
                <span className={supported ? 'text-gray-700' : 'text-gray-400'}>
                  {feature.charAt(0).toUpperCase() + feature.slice(1)}
                </span>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex space-x-2">
            {crm.demoAvailable && (
              <Button 
                variant="outline" 
                size="sm" 
                icon={Play} 
                className="flex-1"
                onClick={() => setSelectedDemo(crm)}
              >
                Demo
              </Button>
            )}
            <Button 
              variant="primary" 
              size="sm" 
              icon={Zap} 
              className="flex-1"
              onClick={() => setSelectedSetup(crm)}
            >
              Connect
            </Button>
          </div>

          {/* Additional Links */}
          <div className="flex justify-between mt-3 pt-3 border-t border-gray-200">
            <a
              href={crm.documentation}
              className="flex items-center text-xs text-primary-600 hover:text-primary-700"
            >
              <BookOpen className="w-3 h-3 mr-1" />
              Docs
            </a>
            <span className="text-xs text-gray-500">{crm.pricing}</span>
          </div>
        </Card>
      ))}
    </div>
  );

  const renderComparisonView = () => (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-4 px-4 font-semibold text-gray-900">CRM Platform</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Setup</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Contacts</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Deals</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Activities</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Campaigns</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Analytics</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Webhooks</th>
            <th className="text-center py-4 px-4 font-semibold text-gray-900">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {crmConnectors.map((crm) => (
            <tr key={crm.id} className="hover:bg-gray-50">
              <td className="py-4 px-4">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">{crm.logo}</div>
                  <div>
                    <div className="font-medium text-gray-900">{crm.name}</div>
                    <div className="flex items-center space-x-2 mt-1">
                      {getStatusBadge(crm.status)}
                    </div>
                  </div>
                </div>
              </td>
              <td className="py-4 px-4 text-center">
                <div className="text-sm">
                  <div>{crm.setupTimeMinutes} min</div>
                  {getComplexityBadge(crm.setupComplexity)}
                </div>
              </td>
              {Object.entries(crm.features).map(([feature, supported]) => (
                <td key={feature} className="py-4 px-4 text-center">
                  {supported ? (
                    <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                  ) : (
                    <div className="w-5 h-5 rounded-full bg-gray-300 mx-auto" />
                  )}
                </td>
              ))}
              <td className="py-4 px-4 text-center">
                <div className="flex space-x-2 justify-center">
                  {crm.demoAvailable && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      icon={Play}
                      onClick={() => setSelectedDemo(crm)}
                    >
                      Demo
                    </Button>
                  )}
                  <Button 
                    variant="primary" 
                    size="sm" 
                    icon={Zap}
                    onClick={() => setSelectedSetup(crm)}
                  >
                    Connect
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <section id="integrations" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-unitasa-blue mb-4 font-display">
            CRM Intelligence Enhancement
          </h2>
          <p className="text-xl text-unitasa-gray max-w-3xl mx-auto">
            Transform your existing CRM into an AI-powered revenue engine. We don't replace your CRM—we make it 10x smarter with autonomous decision-making and predictive intelligence.
          </p>

          {/* CRM App Promotion */}
          <div className="mt-8 bg-gradient-to-r from-unitasa-electric/10 to-unitasa-purple/10 border border-unitasa-electric/20 rounded-2xl p-6 max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-4">
              <div className="bg-unitasa-electric text-white p-3 rounded-full mr-4">
                <Settings className="w-6 h-6" />
              </div>
              <div className="text-left">
                <h3 className="text-lg font-bold text-unitasa-blue">🚀 Bonus: Custom CRM App Included</h3>
                <p className="text-unitasa-gray text-sm">Get a fully customized CRM application built specifically for your business</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-semibold text-unitasa-blue text-sm">Tailored Interface</div>
                  <div className="text-unitasa-gray text-xs">Custom dashboard designed for your workflow</div>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-semibold text-unitasa-blue text-sm">Advanced Automation</div>
                  <div className="text-unitasa-gray text-xs">AI-powered workflows and smart triggers</div>
                </div>
              </div>
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-semibold text-unitasa-blue text-sm">Full Integration</div>
                  <div className="text-unitasa-gray text-xs">Seamlessly connects with Unitasa platform</div>
                </div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <span className="inline-block bg-gradient-primary bg-clip-text text-transparent font-bold text-sm">
                🎁 FREE with any CRM integration - No additional cost!
              </span>
            </div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('gallery')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'gallery'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Gallery View
            </button>
            <button
              onClick={() => setViewMode('comparison')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'comparison'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Compare Features
            </button>
          </div>
        </div>

        {/* Content */}
        {viewMode === 'gallery' ? renderGalleryView() : renderComparisonView()}

        {/* Integration Support */}
        <div className="mt-16 bg-unitasa-light rounded-2xl p-8">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-unitasa-blue mb-4 font-display">
              Need Help with Integration?
            </h3>
            <p className="text-unitasa-gray max-w-2xl mx-auto">
              Our integration experts are here to help you connect any CRM, customize workflows,
              and optimize your automation setup for maximum results.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-6 text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <Code className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Custom Integration</h4>
              <p className="text-gray-600 text-sm mb-4">
                Don't see your CRM? We'll build a custom integration for you.
              </p>
              <Button variant="outline" size="sm">
                Request Integration
              </Button>
            </Card>

            <Card className="p-6 text-center">
              <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <Settings className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Setup Assistance</h4>
              <p className="text-gray-600 text-sm mb-4">
                Get personalized help setting up your CRM integration.
              </p>
              <Button variant="outline" size="sm">
                Book Setup Call
              </Button>
            </Card>

            <Card className="p-6 text-center">
              <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Developer Resources</h4>
              <p className="text-gray-600 text-sm mb-4">
                Access APIs, SDKs, and comprehensive documentation.
              </p>
              <Button variant="outline" size="sm" icon={ExternalLink}>
                View Docs
              </Button>
            </Card>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <h3 className="text-2xl font-bold text-unitasa-blue mb-4 font-display">
            Ready to Evolve Beyond Traditional CRM?
          </h3>
          <p className="text-unitasa-gray mb-8 max-w-2xl mx-auto">
            Join marketing leaders who have transformed their CRM from a data repository into an autonomous revenue-generating AI system.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              icon={Zap}
              className="bg-gradient-primary text-white hover:shadow-brand"
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openLeadCapture'));
              }}
            >
              Assess Your AI Readiness
            </Button>
            <Button
              variant="outline"
              size="lg"
              icon={Play}
              className="border-unitasa-electric text-unitasa-electric hover:bg-unitasa-electric hover:text-white"
            >
              See AI in Action
            </Button>
          </div>
        </div>
      </div>

      {/* Demo Modal */}
      {selectedDemo && (
        <CRMDemoModal
          crmName={selectedDemo.name}
          crmLogo={selectedDemo.logo}
          isOpen={!!selectedDemo}
          onClose={() => setSelectedDemo(null)}
          onStartSetup={() => {
            setSelectedDemo(null);
            setSelectedSetup(selectedDemo);
          }}
        />
      )}

      {/* Setup Wizard Modal */}
      {selectedSetup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <CRMSetupWizard
                crmType={selectedSetup.name}
                onComplete={(config) => {
                  console.log('Setup completed:', config);
                  setSelectedSetup(null);
                }}
                onCancel={() => setSelectedSetup(null)}
              />
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default CRMMarketplaceSection;
