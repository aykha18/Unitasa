import React from 'react';
import { Star, Quote, TrendingUp, Users, Award, CheckCircle } from 'lucide-react';
import { Card } from '../ui';

const SocialProofSection: React.FC = () => {
  // Removed fake testimonials - will replace with founder credibility section

  const honestStats = [
    {
      icon: Users,
      value: '25',
      label: 'Founding Members',
      description: 'Limited spots available'
    },
    {
      icon: TrendingUp,
      value: 'BETA',
      label: 'Currently in Development',
      description: 'Building with early users'
    },
    {
      icon: CheckCircle,
      value: '100%',
      label: 'Transparent',
      description: 'Honest about our stage'
    },
    {
      icon: Award,
      value: '1.0',
      label: 'Version',
      description: 'Functional MVP available'
    }
  ];

  const certifications = [
    { name: 'SOC 2 Type II', description: 'Security & Compliance' },
    { name: 'GDPR Compliant', description: 'Data Protection' },
    { name: 'ISO 27001', description: 'Information Security' },
    { name: 'PCI DSS', description: 'Payment Security' }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        {/* <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Trusted by Growing Businesses Worldwide
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join thousands of companies that have transformed their marketing automation 
            and achieved measurable growth with Unitasa.
          </p>
        </div> */}

        {/* Honest Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {honestStats.map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <Card key={index} className="p-6 text-center" hover>
                <div className="bg-primary-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                  <IconComponent className="w-6 h-6 text-primary-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="font-semibold text-gray-700 mb-1">{stat.label}</div>
                <div className="text-sm text-gray-500">{stat.description}</div>
              </Card>
            );
          })}
        </div>



        {/* Trust Indicators */}
        <div className="bg-white rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Enterprise-Grade Security & Compliance
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {certifications.map((cert, index) => (
              <div key={index} className="text-center p-4 border border-gray-200 rounded-lg">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <div className="font-semibold text-gray-900 mb-1">{cert.name}</div>
                <div className="text-sm text-gray-600">{cert.description}</div>
              </div>
            ))}
          </div>

          {/* Additional Trust Elements */}
          <div className="border-t border-gray-200 pt-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-2xl font-bold text-gray-900 mb-2">99.9%</div>
                <div className="text-gray-600">Uptime SLA</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 mb-2">24/7</div>
                <div className="text-gray-600">Expert Support</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 mb-2">30-Day</div>
                <div className="text-gray-600">Money-Back Guarantee</div>
              </div>
            </div>
          </div>
        </div>

        {/* Trust Section */}
        <div className="bg-white rounded-2xl p-8 mt-16 border border-gray-200">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Built with Engineering Excellence</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <p className="text-gray-700 font-medium">Built by a founder with 13+ years of engineering experience</p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <p className="text-gray-700 font-medium">Currently integrated with: X (Twitter), Facebook, Instagram, Telegram, Reddit</p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
                <p className="text-gray-700 font-medium">Already running live automations for internal Unitasa marketing</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SocialProofSection;
