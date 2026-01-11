import React, { useState } from 'react';
import { ArrowRight, Play, CheckCircle, Zap } from 'lucide-react';
import { Button } from '../ui';
import AIDemoModal from '../ai-demos/AIDemoModal';
import ConsultationBooking from '../booking/ConsultationBooking';

interface HeroSectionProps {
  onStartAssessment?: () => void;
}

const HeroSection: React.FC<HeroSectionProps> = ({ onStartAssessment }) => {
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);

  return (
    <section className="bg-gradient-to-br from-unitasa-light via-white to-unitasa-light py-20 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Launch Banner */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center bg-gradient-to-r from-unitasa-electric to-unitasa-blue text-white px-6 py-3 rounded-full text-sm font-semibold shadow-lg">
            <Zap className="w-4 h-4 mr-2" />
            🚀 LAUNCHING NOW - Join 25 Founding Members
            <span className="ml-2 bg-white/20 px-2 py-1 rounded text-xs">LIMITED SPOTS</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Content */}
          <div className="text-center lg:text-left">
            {/* Beta Badge */}
            <div className="inline-flex items-center bg-unitasa-electric/10 text-unitasa-blue px-4 py-2 rounded-full text-sm font-medium mb-6 border border-unitasa-electric/20">
              <Zap className="w-4 h-4 mr-2" />
              BETA - Built by Founders, for Founders
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-unitasa-blue mb-6 leading-tight font-display">
              AI Agents That Run Your Marketing For You
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-unitasa-gray mb-8 max-w-2xl mx-auto lg:mx-0 font-medium">
              Unitasa connects to your CRM, social accounts, and ad platforms so autonomous agents can plan, post, and optimize campaigns while you focus on building your product.
            </p>

            {/* Cost Savings Highlight */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 max-w-lg mx-auto lg:mx-0 mb-8">
              <div className="flex items-center justify-center lg:justify-start">
                <div className="bg-green-100 rounded-full p-2 mr-3">
                  <Zap className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <div className="text-green-800 font-semibold text-sm">60-80% Cost Savings</div>
                  <div className="text-green-700 text-xs">vs traditional AI marketing tools</div>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button
                variant="primary"
                size="lg"
                icon={ArrowRight}
                iconPosition="right"
                className="text-lg px-8 py-4"
                onClick={() => setShowBookingModal(true)}
              >
                Book Free AI Strategy Session
              </Button>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  variant="outline"
                  size="lg"
                  icon={Play}
                  iconPosition="left"
                  className="text-lg px-8 py-4"
                  onClick={() => setIsDemoModalOpen(true)}
                >
                  Watch 2-Minute Demo
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  className="text-lg px-8 py-4"
                  onClick={onStartAssessment}
                >
                  Take AI Readiness Assessment
                </Button>
              </div>
            </div>


          </div>

          {/* Right Column - Visual */}
          <div className="relative">
            {/* Main Dashboard Mockup */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 transform rotate-3 hover:rotate-0 transition-transform duration-300">
              <div className="bg-gradient-primary h-12 rounded-lg mb-4 flex items-center px-4 shadow-brand">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                </div>
                <div className="ml-4 text-white font-medium">Unitasa Dashboard</div>
              </div>
              
              {/* Problem Statement */}
              <div className="space-y-4 p-4">
                <h3 className="text-lg font-bold text-unitasa-blue mb-3">The Problem Every B2B Founder Faces:</h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">⏰</span>
                    <span>15+ hours/week managing disconnected marketing tools</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">💔</span>
                    <span>CRM integrations that break constantly</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">🤖</span>
                    <span>"AI marketing" that's just basic if/then rules</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-red-500 mr-2">💸</span>
                    <span>₹40,000+/month on tools that don't talk to each other</span>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-unitasa-light/50 rounded-lg">
                  <p className="text-sm text-unitasa-blue font-medium">
                    Built by a founder who solved these exact marketing automation challenges.
                  </p>
                </div>
              </div>
            </div>

            {/* Floating CRM Icons */}
            <div className="absolute -top-4 -left-4 bg-white rounded-lg shadow-lg p-3 animate-bounce">
              <div className="w-8 h-8 bg-orange-500 rounded flex items-center justify-center text-white text-xs font-bold">
                P
              </div>
            </div>
            <div className="absolute -bottom-4 -right-4 bg-white rounded-lg shadow-lg p-3 animate-pulse">
              <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">
                H
              </div>
            </div>
            <div className="absolute top-1/2 -right-8 bg-white rounded-lg shadow-lg p-3 animate-bounce delay-300">
              <div className="w-8 h-8 bg-red-500 rounded flex items-center justify-center text-white text-xs font-bold">
                Z
              </div>
            </div>
          </div>
        </div>

        {/* AI Demo Modal */}
        <AIDemoModal
          isOpen={isDemoModalOpen}
          onClose={() => setIsDemoModalOpen(false)}
          initialDemo="agent"
        />

        {/* Consultation Booking Modal */}
        {showBookingModal && (
          <ConsultationBooking
            isOpen={showBookingModal}
            onClose={() => setShowBookingModal(false)}
          />
        )}
      </div>
    </section>
  );
};

export default HeroSection;
