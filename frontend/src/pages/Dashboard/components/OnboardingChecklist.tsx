import React, { useState } from 'react';
import { CheckCircle, Circle, User, Link, Target, Users, ChevronRight } from 'lucide-react';
import { CreateCampaignModal } from './CreateCampaignModal';
import { InviteTeamModal } from './InviteTeamModal';

interface User {
  subscription_tier: string;
  is_co_creator: boolean;
  is_trial_active: boolean;
}

interface OnboardingChecklistProps {
  progress: {
    profileComplete: boolean;
    crmConnected: boolean;
    firstCampaign: boolean;
    teamInvited: boolean;
  };
  user: User;
  onProgressUpdate: () => void;
}

const OnboardingChecklist: React.FC<OnboardingChecklistProps> = ({ progress, user, onProgressUpdate }) => {
  const [isCampaignModalOpen, setIsCampaignModalOpen] = useState(false);
  const [isTeamModalOpen, setIsTeamModalOpen] = useState(false);

  const steps = [
    {
      id: 'profile',
      title: 'Complete Your Profile',
      description: 'Add your company details and preferences',
      completed: progress.profileComplete,
      icon: User,
      action: () => navigateTo('/onboarding')
    },
    {
      id: 'crm',
      title: 'Connect CRM',
      description: 'Integrate with your existing CRM system',
      completed: progress.crmConnected,
      icon: Link,
      action: () => navigateTo('/settings/crm')
    },
    {
      id: 'campaign',
      title: 'Create First Campaign',
      description: 'Launch your first social media campaign',
      completed: progress.firstCampaign,
      icon: Target,
      action: () => setIsCampaignModalOpen(true)
    },
    {
      id: 'team',
      title: 'Invite Team Members',
      description: 'Add your marketing team to collaborate',
      completed: progress.teamInvited,
      icon: Users,
      action: () => setIsTeamModalOpen(true)
    },
  ];

  const completedSteps = steps.filter(step => step.completed).length;
  const totalSteps = steps.length;
  const progressPercentage = (completedSteps / totalSteps) * 100;

  const navigateTo = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('popstate'));
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Onboarding Progress</h2>
            <p className="text-gray-600 text-sm">
              {completedSteps} of {totalSteps} steps completed
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">{Math.round(progressPercentage)}%</div>
            <div className="text-sm text-gray-600">Complete</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>

        {/* Steps */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div 
              key={step.id} 
              className={`flex items-start space-x-3 p-3 rounded-lg transition-colors cursor-pointer hover:bg-gray-50 border border-transparent hover:border-gray-100`}
              onClick={step.action}
            >
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                step.completed
                  ? 'bg-green-100 text-green-600'
                  : 'bg-gray-100 text-gray-400'
              }`}>
                {step.completed ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <step.icon className="w-5 h-5" />
                )}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className={`text-sm font-medium ${
                    step.completed ? 'text-gray-900' : 'text-gray-700'
                  }`}>
                    {step.title}
                  </h3>
                  {!step.completed && (
                    <button className="text-xs font-medium text-blue-600 hover:text-blue-700 px-2 py-1 rounded bg-blue-50 hover:bg-blue-100 transition-colors">
                      {step.id === 'campaign' ? 'Create' : step.id === 'team' ? 'Invite' : 'Start'}
                    </button>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <CreateCampaignModal 
        isOpen={isCampaignModalOpen}
        onClose={() => setIsCampaignModalOpen(false)}
        onCampaignCreated={() => {
          onProgressUpdate();
        }}
      />

      <InviteTeamModal
        isOpen={isTeamModalOpen}
        onClose={() => setIsTeamModalOpen(false)}
        onInvitationSent={() => {
          onProgressUpdate();
        }}
      />
    </>
  );
};

export default OnboardingChecklist;