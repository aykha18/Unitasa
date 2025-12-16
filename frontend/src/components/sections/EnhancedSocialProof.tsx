import React, { useState, useEffect } from 'react';
import { Shield, Users, Award, CheckCircle, TrendingUp, Star, Globe, Clock, Zap, Target } from 'lucide-react';

const EnhancedSocialProof: React.FC = () => {
  const [activeUsers, setActiveUsers] = useState(247);
  const [uptimePercentage, setUptimePercentage] = useState(99.9);
  const [avgResponseTime, setAvgResponseTime] = useState(2.3);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly update metrics to show "live" data
      setActiveUsers(prev => prev + Math.floor(Math.random() * 3) - 1);
      setUptimePercentage(prev => Math.max(99.5, Math.min(99.9, prev + (Math.random() - 0.5) * 0.1)));
      setAvgResponseTime(prev => Math.max(1.8, Math.min(3.2, prev + (Math.random() - 0.5) * 0.2)));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const trustIndicators = [
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Enterprise Security',
      description: 'SOC 2 Type II compliant with end-to-end encryption',
      color: 'text-blue-600'
    },
    {
      icon: <Award className="w-6 h-6" />,
      title: 'GDPR Compliant',
      description: 'Your data is protected under strict EU privacy regulations',
      color: 'text-green-600'
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: 'Global Scale',
      description: 'Serving 50+ countries with 24/7 multilingual support',
      color: 'text-purple-600'
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Real-time Processing',
      description: 'AI responses in under 3 seconds with 99.9% uptime',
      color: 'text-orange-600'
    }
  ];

  const certifications = [
    { name: 'SOC 2 Type II', issuer: 'Security & Compliance', status: 'Certified' },
    { name: 'GDPR', issuer: 'EU Data Protection', status: 'Compliant' },
    { name: 'ISO 27001', issuer: 'Information Security', status: 'Certified' },
    { name: 'PCI DSS', issuer: 'Payment Security', status: 'Level 1' },
    { name: 'HIPAA', issuer: 'Healthcare Data', status: 'Compliant' },
    { name: 'CCPA', issuer: 'California Privacy', status: 'Compliant' }
  ];

  const liveMetrics = [
    {
      label: 'Active Users',
      value: activeUsers,
      change: '+12%',
      timeframe: 'vs last hour',
      icon: <Users className="w-5 h-5" />,
      color: 'text-blue-600'
    },
    {
      label: 'System Uptime',
      value: `${uptimePercentage.toFixed(1)}%`,
      change: '99.9%',
      timeframe: '30-day average',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'text-green-600'
    },
    {
      label: 'Avg Response Time',
      value: `${avgResponseTime.toFixed(1)}s`,
      change: '-0.3s',
      timeframe: 'vs last week',
      icon: <Clock className="w-5 h-5" />,
      color: 'text-purple-600'
    },
    {
      label: 'Success Rate',
      value: '94.7%',
      change: '+2.1%',
      timeframe: 'vs last month',
      icon: <Target className="w-5 h-5" />,
      color: 'text-orange-600'
    }
  ];

  const testimonials = [
    {
      rating: 5,
      text: "Unitasa's reliability is unmatched. Zero downtime in 6 months.",
      author: "Sarah Chen",
      company: "TechFlow",
      industry: "SaaS"
    },
    {
      rating: 5,
      text: "The security standards give us complete peace of mind.",
      author: "Marcus Rodriguez",
      company: "HealthFirst",
      industry: "Healthcare"
    },
    {
      rating: 5,
      text: "Global compliance made our expansion seamless.",
      author: "Priya Patel",
      company: "FinSecure",
      industry: "Finance"
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Shield className="w-4 h-4 mr-2" />
            Trusted by Industry Leaders
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Enterprise-Grade Trust & Reliability
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join thousands of companies worldwide that trust Unitasa with their most critical business operations.
            Built for enterprise scale with uncompromising security and reliability.
          </p>
        </div>

        {/* Live Metrics Dashboard */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {liveMetrics.map((metric, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 text-center hover:shadow-xl transition-shadow">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 mb-4 ${metric.color}`}>
                {metric.icon}
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
              <div className="text-sm text-gray-600 mb-2">{metric.label}</div>
              <div className="flex items-center justify-center space-x-2">
                <span className="text-xs font-medium text-green-600">{metric.change}</span>
                <span className="text-xs text-gray-500">{metric.timeframe}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Trust Indicators Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {trustIndicators.map((indicator, index) => (
            <div key={index} className="bg-white rounded-xl shadow-md border border-gray-100 p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start">
                <div className={`p-3 rounded-lg bg-gray-100 ${indicator.color} mr-4`}>
                  {indicator.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">{indicator.title}</h3>
                  <p className="text-sm text-gray-600">{indicator.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Certifications Grid */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-16">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Industry Certifications & Compliance
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {certifications.map((cert, index) => (
              <div key={index} className="text-center p-4 border border-gray-200 rounded-lg hover:border-green-300 transition-colors">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <div className="font-semibold text-gray-900 text-sm mb-1">{cert.name}</div>
                <div className="text-xs text-gray-600 mb-1">{cert.issuer}</div>
                <div className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                  {cert.status}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Customer Testimonials */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-16">
          <h3 className="text-xl font-bold text-gray-900 text-center mb-8">
            What Our Enterprise Customers Say
          </h3>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-4">
                  {Array.from({ length: testimonial.rating }, (_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-gray-700 mb-4 italic text-lg">
                  "{testimonial.text}"
                </blockquote>
                <div className="font-semibold text-gray-900">{testimonial.author}</div>
                <div className="text-sm text-gray-600">{testimonial.company}</div>
                <div className="inline-block bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full mt-2">
                  {testimonial.industry}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise Features */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-bold mb-4">Built for Enterprise Scale</h3>
              <p className="text-blue-100 mb-6">
                Unitasa handles millions of API calls daily with enterprise-grade infrastructure,
                ensuring your business operations never slow down.
              </p>

              <div className="space-y-3">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-300 mr-3 flex-shrink-0" />
                  <span className="text-sm">99.9% uptime SLA with enterprise support</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-300 mr-3 flex-shrink-0" />
                  <span className="text-sm">End-to-end encryption and data isolation</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-300 mr-3 flex-shrink-0" />
                  <span className="text-sm">GDPR, HIPAA, and SOC 2 compliant</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-300 mr-3 flex-shrink-0" />
                  <span className="text-sm">24/7 enterprise support with dedicated managers</span>
                </div>
              </div>
            </div>

            <div className="text-center">
              <div className="bg-white/10 rounded-xl p-6 backdrop-blur-sm">
                <div className="text-4xl font-bold mb-2">500+</div>
                <div className="text-blue-100 mb-4">Enterprise Customers</div>
                <div className="text-2xl font-bold mb-2">$2M+</div>
                <div className="text-blue-100">Revenue Protected Monthly</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default EnhancedSocialProof;