import React, { useState } from 'react';
import { X, Brain, Target, MessageCircle, Zap, Shield, BarChart3, Share2 } from 'lucide-react';
import Button from '../ui/Button';
import AIAgentDemo from './AIAgentDemo';
import PredictiveAnalyticsDemo from './PredictiveAnalyticsDemo';
import ConversationalAIDemo from './ConversationalAIDemo';

interface AIDemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialDemo?: string;
}

type DemoType = 'agent' | 'predictive' | 'conversational' | 'social-media' | 'optimization' | 'security' | 'analytics';

interface DemoTab {
  id: DemoType;
  title: string;
  icon: React.ReactNode;
  description: string;
}

const AIDemoModal: React.FC<AIDemoModalProps> = ({ isOpen, onClose, initialDemo = 'agent' }) => {
  const [activeDemo, setActiveDemo] = useState<DemoType>(initialDemo as DemoType);

  const demoTabs: DemoTab[] = [
    {
      id: 'agent',
      title: 'Autonomous Agent',
      icon: <Brain className="w-5 h-5" />,
      description: 'AI that makes 10,000+ decisions per hour'
    },
    {
      id: 'predictive',
      title: 'Predictive Intelligence',
      icon: <Target className="w-5 h-5" />,
      description: '94% accuracy in conversion prediction'
    },
    {
      id: 'conversational',
      title: 'AI Assistant',
      icon: <MessageCircle className="w-5 h-5" />,
      description: 'Voice-enabled marketing consultation'
    },
    {
      id: 'social-media',
      title: 'Social Media Automation',
      icon: <Share2 className="w-5 h-5" />,
      description: '10+ platforms automated posting & engagement'
    },
    {
      id: 'optimization',
      title: 'Real-Time Optimization',
      icon: <Zap className="w-5 h-5" />,
      description: 'Instant campaign performance tuning'
    },
    {
      id: 'security',
      title: 'Enterprise Security',
      icon: <Shield className="w-5 h-5" />,
      description: 'Bank-level AI-powered protection'
    },
    {
      id: 'analytics',
      title: 'Advanced Analytics',
      icon: <BarChart3 className="w-5 h-5" />,
      description: 'Cross-channel intelligence insights'
    }
  ];

  const renderDemoContent = () => {
    switch (activeDemo) {
      case 'agent':
        return <AIAgentDemo />;
      case 'predictive':
        return <PredictiveAnalyticsDemo />;
      case 'conversational':
        return <ConversationalAIDemo />;
      case 'social-media':
        return (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center mb-6">
              <Share2 className="w-6 h-6 text-blue-600 mr-3" />
              <h3 className="text-xl font-semibold text-gray-900">Multi-Platform Social Media Automation</h3>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600">10+</div>
                  <div className="text-xs text-gray-600">Platforms Supported</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-green-600">24/7</div>
                  <div className="text-xs text-gray-600">Automated Posting</div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">Twitter/X Automated Posting</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">LinkedIn Campaign Management</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">Instagram Content Scheduling</span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Scheduled</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">Facebook Engagement Tracking</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">YouTube Analytics Integration</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>
                </div>
              </div>
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Real-Time Performance</h4>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-blue-600">2.4K</div>
                    <div className="text-xs text-gray-600">Posts This Week</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-green-600">18.5K</div>
                    <div className="text-xs text-gray-600">Engagements</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-purple-600">+127%</div>
                    <div className="text-xs text-gray-600">Reach Growth</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'optimization':
        return (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center mb-6">
              <Zap className="w-6 h-6 text-orange-600 mr-3" />
              <h3 className="text-xl font-semibold text-gray-900">Real-Time Optimization Engine</h3>
            </div>
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-orange-50 to-red-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Live Performance Metrics</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Campaign ROI:</span>
                    <div className="text-2xl font-bold text-green-600">+340%</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Optimization Speed:</span>
                    <div className="text-2xl font-bold text-orange-600">&lt;30s</div>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">Budget reallocation across channels</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">Bid optimization for high-value keywords</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">A/B testing creative variations</span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Running</span>
                </div>
              </div>
            </div>
          </div>
        );
      case 'security':
        return (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center mb-6">
              <Shield className="w-6 h-6 text-green-600 mr-3" />
              <h3 className="text-xl font-semibold text-gray-900">Enterprise Security Dashboard</h3>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-green-600">99.9%</div>
                  <div className="text-xs text-gray-600">Uptime SLA</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600">256-bit</div>
                  <div className="text-xs text-gray-600">Encryption</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                  <span className="text-sm text-gray-700">OAuth2 Authentication</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Secured</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                  <span className="text-sm text-gray-700">Webhook Signature Verification</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                  <span className="text-sm text-gray-700">AI Threat Detection</span>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Monitoring</span>
                </div>
              </div>
            </div>
          </div>
        );
      case 'analytics':
        return (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center mb-6">
              <BarChart3 className="w-6 h-6 text-purple-600 mr-3" />
              <h3 className="text-xl font-semibold text-gray-900">Advanced Analytics Engine</h3>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-purple-50 p-3 rounded-lg">
                  <div className="text-xl font-bold text-purple-600">15+</div>
                  <div className="text-xs text-gray-600">Data Sources</div>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-xl font-bold text-blue-600">Real-time</div>
                  <div className="text-xs text-gray-600">Processing</div>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-xl font-bold text-green-600">360°</div>
                  <div className="text-xs text-gray-600">Customer View</div>
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Cross-Channel Attribution</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">LinkedIn Ads</span>
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                      </div>
                      <span className="text-sm font-medium">75%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Email Marketing</span>
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                      </div>
                      <span className="text-sm font-medium">60%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Google Ads</span>
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                      </div>
                      <span className="text-sm font-medium">45%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return <AIAgentDemo />;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">AI Capabilities Interactive Demo</h2>
            <p className="text-gray-600">Experience Unitasa's advanced AI features in action</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        <div className="flex h-[calc(90vh-120px)]">
          {/* Sidebar */}
          <div className="w-80 bg-gray-50 border-r border-gray-200 overflow-y-auto">
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-4">AI Features</h3>
              <div className="space-y-2">
                {demoTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveDemo(tab.id)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      activeDemo === tab.id
                        ? 'bg-blue-100 text-blue-700 border border-blue-200'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center mb-2">
                      {tab.icon}
                      <span className="ml-2 font-medium">{tab.title}</span>
                    </div>
                    <p className="text-xs text-gray-600">{tab.description}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-6">
              {renderDemoContent()}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Ready to implement these AI capabilities in your marketing?
            </p>
            <div className="flex gap-3">
              <Button variant="outline" onClick={onClose}>
                Close Demo
              </Button>
              <Button>
                Start AI Assessment
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIDemoModal;
