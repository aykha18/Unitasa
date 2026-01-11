import React, { useState, useEffect } from 'react';
import { CoCreatorProgramStatus } from '../../types';
import LandingPageAPI from '../../services/landingPageApi';
import Button from '../ui/Button';
import config from '../../config/environment';
import { pricingService } from '../../services/pricingService';
import {
  Crown,
  Users,
  Zap,
  Clock,
  CheckCircle,
  Star,
  Shield,
  Rocket,
  Heart,
  TrendingUp,
  MessageCircle,
  Award,
  Timer,
  Flame
} from 'lucide-react';

interface CoCreatorProgramInterfaceProps {
  onJoinProgram: () => void;
  className?: string;
}

const CoCreatorProgramInterface: React.FC<CoCreatorProgramInterfaceProps> = ({
  onJoinProgram,
  className = '',
}) => {
  const [programStatus, setProgramStatus] = useState<CoCreatorProgramStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const [timeLeft, setTimeLeft] = useState<{days: number, hours: number, minutes: number, seconds: number} | null>(null);
  const [recentJoins, setRecentJoins] = useState<string[]>([]);
  const [price, setPrice] = useState('');

  useEffect(() => {
    const init = async () => {
      try {
        setLoading(true);
        // Fetch pricing
        const plans = await pricingService.getAllPlans();
        const coCreatorPlan = plans.find(p => p.name === 'co_creator');
        if (coCreatorPlan) {
          setPrice(pricingService.formatPrice(coCreatorPlan.price_inr, 'INR'));
        } else {
          // Fallback if plan not found
          setPrice('₹29,999'); 
        }

        // Load program status
        const status = await LandingPageAPI.getCoCreatorStatus();
        setProgramStatus(status);
      } catch (error) {
        console.error('Failed to initialize Co-Creator Interface:', error);
        // Set fallbacks on error
        setPrice('₹29,999'); 
      } finally {
        setLoading(false);
      }
    };

    init();
    setupWebSocketConnection();
    startCountdownTimer();

    return () => {
      // Cleanup WebSocket connection
      if ((window as any).coCreatorWebSocket) {
        (window as any).coCreatorWebSocket.close();
      }
    };
  }, []);

  const startCountdownTimer = () => {
    // Set program end date to 30 days from now (adjustable)
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 30);

    const updateTimer = () => {
      const now = new Date().getTime();
      const distance = endDate.getTime() - now;

      if (distance > 0) {
        setTimeLeft({
          days: Math.floor(distance / (1000 * 60 * 60 * 24)),
          hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((distance % (1000 * 60)) / 1000)
        });
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  };



  const setupWebSocketConnection = () => {
    // Skip WebSocket connection if disabled
    if (process.env.REACT_APP_DISABLE_WEBSOCKET === 'true') {
      console.log('WebSocket disabled via environment variable');
      return;
    }
    
    try {
      // Use centralized environment configuration
      const wsUrl = process.env.REACT_APP_WS_URL || `${config.wsBaseUrl}/ws/co-creator-status`;
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setIsWebSocketConnected(true);
        console.log('Co-creator WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'seat_update') {
          setProgramStatus(prev => prev ? {
            ...prev,
            seatsRemaining: data.seatsRemaining,
            urgencyLevel: data.urgencyLevel
          } : null);
        } else if (data.type === 'new_join') {
          // Add recent join notification
          setRecentJoins(prev => [data.name, ...prev.slice(0, 2)]);
          // Remove after 10 seconds
          setTimeout(() => {
            setRecentJoins(prev => prev.filter(name => name !== data.name));
          }, 10000);
        }
      };
      
      ws.onclose = () => {
        setIsWebSocketConnected(false);
        console.log('Co-creator WebSocket disconnected');
        // Attempt to reconnect after 5 seconds
        setTimeout(setupWebSocketConnection, 5000);
      };
      
      ws.onerror = (error) => {
        console.error('Co-creator WebSocket error:', error);
        setIsWebSocketConnected(false);
      };
      
      // Store WebSocket reference for cleanup
      (window as any).coCreatorWebSocket = ws;
    } catch (error) {
      console.error('Failed to setup WebSocket:', error);
    }
  };

  const getUrgencyLevel = () => {
    if (!programStatus) return 'medium';
    if (programStatus.seatsRemaining <= 5) return 'high';
    if (programStatus.seatsRemaining <= 10) return 'medium';
    return 'low';
  };

  const getUrgencyMessage = () => {
    if (!programStatus) return '';
    const urgency = getUrgencyLevel();
    
    switch (urgency) {
      case 'high':
        return `🔥 URGENT: Only ${programStatus.seatsRemaining} seats left!`;
      case 'medium':
        return `⚡ ${programStatus.seatsRemaining} seats remaining out of ${programStatus.totalSeats}`;
      case 'low':
        return `✨ ${programStatus.seatsRemaining} seats available out of ${programStatus.totalSeats}`;
      default:
        return '';
    }
  };

  const tieredIncentives = [
    {
      tier: 'Lifetime Access',
      icon: Crown,
      color: 'text-yellow-400',
      benefits: [
        'Unlimited platform access forever',
        'All future features included',
        'No recurring subscription fees',
        'Grandfathered pricing protection'
      ]
    },
    {
      tier: 'Integration Support',
      icon: Zap,
      color: 'text-blue-400',
      benefits: [
        'Priority CRM integration setup',
        'Custom field mapping assistance',
        'Direct technical support channel',
        'Integration troubleshooting help'
      ]
    },
    {
      tier: 'Product Influence',
      icon: Rocket,
      color: 'text-purple-400',
      benefits: [
        'Vote on new features and integrations',
        'Direct feedback to founder',
        'Beta access to new capabilities',
        'Feature request priority'
      ]
    },
    {
      tier: 'Recognition',
      icon: Award,
      color: 'text-green-400',
      benefits: [
        'Co-creator badge and profile',
        'Featured in success stories',
        'Product credits recognition',
        'Exclusive community access'
      ]
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Marketing Director',
      company: 'TechFlow Solutions',
      avatar: '👩‍💼',
      quote: 'Being a co-creator gave me direct influence over the HubSpot integration. The founder actually implemented my suggestions!',
      integration: 'HubSpot',
      joinedDaysAgo: 3
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Sales Manager',
      company: 'Growth Dynamics',
      avatar: '👨‍💻',
      quote: 'The lifetime access alone is worth 10x the investment. Plus, the Pipedrive integration works flawlessly.',
      integration: 'Pipedrive',
      joinedDaysAgo: 7
    },
    {
      name: 'Emily Watson',
      role: 'Founder',
      company: 'StartupBoost',
      avatar: '👩‍🚀',
      quote: 'As a co-creator, I helped shape the Zoho integration. Now my entire sales process is automated.',
      integration: 'Zoho CRM',
      joinedDaysAgo: 12
    },
    {
      name: 'David Kim',
      role: 'VP of Sales',
      company: 'ScaleUp Inc',
      avatar: '👨‍💼',
      quote: 'The Salesforce integration saved us 20 hours/week. As a co-creator, I got priority setup and custom field mapping.',
      integration: 'Salesforce',
      joinedDaysAgo: 1
    },
    {
      name: 'Lisa Thompson',
      role: 'CMO',
      company: 'DigitalFirst',
      avatar: '👩‍💻',
      quote: 'ROI was immediate. The AI automation reduced our lead qualification time by 80%. Worth every penny.',
      integration: 'ActiveCampaign',
      joinedDaysAgo: 5
    }
  ];

  if (loading) {
    return (
      <div className={`bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 rounded-2xl p-8 text-white ${className}`}>
        <div className="animate-pulse space-y-6">
          <div className="h-12 bg-white/10 rounded-lg"></div>
          <div className="h-6 bg-white/10 rounded w-3/4"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-32 bg-white/10 rounded-lg"></div>
            <div className="h-32 bg-white/10 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 rounded-2xl overflow-hidden ${className}`}>
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full -translate-y-48 translate-x-48"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-white rounded-full translate-y-32 -translate-x-32"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
      </div>

      <div className="relative z-10 p-8 text-white">
        {/* Header Section */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Crown className="w-12 h-12 text-yellow-400 mr-4" />
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
              Co-Creator Program
            </h1>
          </div>
          
          <p className="text-xl md:text-2xl opacity-90 mb-6 max-w-3xl mx-auto">
            Join 25 founding entrepreneurs who get lifetime access to our AI marketing platform + direct product influence + priority support
          </p>
          
          {/* Countdown Timer */}
          {timeLeft && (
            <div className="bg-gradient-to-r from-red-600/20 to-orange-600/20 border border-red-400 rounded-lg p-4 max-w-lg mx-auto mb-6">
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <Timer className="w-5 h-5 text-red-400 mr-2" />
                  <div className="text-red-200 font-semibold">⏰ PROGRAM CLOSES IN</div>
                </div>
                <div className="flex justify-center space-x-4 text-2xl font-bold text-white">
                  <div className="text-center">
                    <div className="bg-red-500/30 px-3 py-2 rounded-lg">{timeLeft.days}</div>
                    <div className="text-xs text-red-300 mt-1">DAYS</div>
                  </div>
                  <div className="text-center">
                    <div className="bg-red-500/30 px-3 py-2 rounded-lg">{timeLeft.hours}</div>
                    <div className="text-xs text-red-300 mt-1">HRS</div>
                  </div>
                  <div className="text-center">
                    <div className="bg-red-500/30 px-3 py-2 rounded-lg">{timeLeft.minutes}</div>
                    <div className="text-xs text-red-300 mt-1">MIN</div>
                  </div>
                  <div className="text-center">
                    <div className="bg-red-500/30 px-3 py-2 rounded-lg">{timeLeft.seconds}</div>
                    <div className="text-xs text-red-300 mt-1">SEC</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recent Joins Notifications */}
          {recentJoins.length > 0 && (
            <div className="max-w-lg mx-auto mb-6">
              {recentJoins.map((name, index) => (
                <div key={index} className="bg-green-500/20 border border-green-400 rounded-lg p-3 mb-2 animate-fade-in">
                  <div className="flex items-center text-green-200">
                    <Flame className="w-4 h-4 mr-2" />
                    <span className="text-sm font-medium">{name} just secured their co-creator spot!</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="bg-red-500/20 border border-red-400 rounded-lg p-4 max-w-lg mx-auto mb-6">
            <div className="text-red-200 font-semibold">⚡ FOUNDER PRICING ENDS SOON</div>
            <div className="text-sm text-red-300">Regular price increases to ₹1,67,000+ after founding phase</div>
          </div>

          {/* Real-time Seat Counter */}
          {programStatus && (
            <div className="inline-flex items-center space-x-4 mb-6">
              <div className={`flex items-center px-6 py-3 rounded-full border-2 ${
                getUrgencyLevel() === 'high' ? 'bg-red-500/20 border-red-400 text-red-200' :
                getUrgencyLevel() === 'medium' ? 'bg-yellow-500/20 border-yellow-400 text-yellow-200' :
                'bg-green-500/20 border-green-400 text-green-200'
              }`}>
                <Users className="w-5 h-5 mr-2" />
                <span className="font-bold text-lg">{getUrgencyMessage()}</span>
              </div>
              
              {isWebSocketConnected && (
                <div className="flex items-center text-green-400 text-sm">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
                  Live Updates
                </div>
              )}
            </div>
          )}
        </div>

        {/* Tiered Incentives Display */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-center mb-8 flex items-center justify-center">
            <Star className="w-6 h-6 text-yellow-400 mr-2" />
            Exclusive Co-Creator Benefits
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {tieredIncentives.map((incentive, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center mb-4">
                  <incentive.icon className={`w-8 h-8 ${incentive.color} mr-3`} />
                  <h3 className="text-lg font-bold">{incentive.tier}</h3>
                </div>
                
                <ul className="space-y-2">
                  {incentive.benefits.map((benefit, benefitIndex) => (
                    <li key={benefitIndex} className="flex items-start text-sm opacity-90">
                      <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 mr-2 flex-shrink-0" />
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Program Benefits and Feature Comparison */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-center mb-8">Co-Creator vs Standard Access</h2>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl overflow-hidden border border-white/20">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-4 font-semibold">Feature</th>
                    <th className="text-center p-4 font-semibold">Standard User</th>
                    <th className="text-center p-4 font-semibold bg-gradient-to-r from-yellow-500/20 to-orange-500/20">
                      <div className="flex items-center justify-center">
                        <Crown className="w-5 h-5 text-yellow-400 mr-2" />
                        Co-Creator
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { feature: 'Platform Access', standard: 'Monthly/Annual', coCreator: 'Lifetime' },
                    { feature: 'CRM Integrations', standard: 'Basic Setup', coCreator: 'Priority Support' },
                    { feature: 'Feature Requests', standard: 'Submit Only', coCreator: 'Vote & Influence' },
                    { feature: 'Support Level', standard: 'Standard', coCreator: 'Direct Channel' },
                    { feature: 'Beta Access', standard: '❌', coCreator: '✅ Early Access' },
                    { feature: 'Recognition', standard: '❌', coCreator: '✅ Credits & Badge' },
                    { feature: 'Community', standard: 'General', coCreator: 'Exclusive Group' },
                    { feature: 'Pricing Protection', standard: '❌', coCreator: '✅ Grandfathered' }
                  ].map((row, index) => (
                    <tr key={index} className="border-b border-white/10 hover:bg-white/5">
                      <td className="p-4 font-medium">{row.feature}</td>
                      <td className="p-4 text-center opacity-70">{row.standard}</td>
                      <td className="p-4 text-center font-semibold text-yellow-400">{row.coCreator}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Testimonials and Social Proof */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-center mb-8 flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-blue-400 mr-2" />
            What Co-Creators Are Saying
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="flex items-center mb-4">
                  <div className="text-3xl mr-3">{testimonial.avatar}</div>
                  <div>
                    <h4 className="font-bold">{testimonial.name}</h4>
                    <p className="text-sm opacity-70">{testimonial.role}</p>
                    <p className="text-sm opacity-70">{testimonial.company}</p>
                  </div>
                </div>
                
                <blockquote className="text-sm opacity-90 mb-4 italic">
                  "{testimonial.quote}"
                </blockquote>

                <div className="flex items-center justify-between">
                  <div className="flex items-center text-xs">
                    <Zap className="w-4 h-4 text-blue-400 mr-1" />
                    <span className="text-blue-400 font-semibold">{testimonial.integration} Integration</span>
                  </div>
                  <div className="flex items-center text-xs text-green-400">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    <span>Joined {testimonial.joinedDaysAgo} days ago</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 border border-white/20 max-w-md mx-auto mb-6">
            <div className="flex items-center justify-center mb-4">
              <Heart className="w-6 h-6 text-red-400 mr-2" />
              <span className="text-lg font-semibold">One-Time Investment</span>
            </div>
            
            <div className="text-sm opacity-70 line-through mb-1">
              Regular Price: ₹1,67,000+
            </div>
            <div className="text-5xl font-bold mb-2 text-yellow-400">{price}</div>
            <div className="text-lg opacity-90 mb-2 mt-2">Founding Member Price</div>
            <div className="text-sm opacity-70 bg-red-500/20 px-3 py-1 rounded-full inline-block">
              🔥 75% Founder Discount
            </div>
            <div className="text-xs opacity-60 mt-2">Pays for itself in first month</div>
          </div>

          <Button
            variant="secondary"
            size="lg"
            className="bg-gradient-to-r from-yellow-400 to-orange-400 text-black hover:from-yellow-300 hover:to-orange-300 font-bold text-lg px-12 py-4 mb-4"
            icon={Crown}
            iconPosition="left"
            onClick={onJoinProgram}
          >
            Secure Your Co-Creator Spot
          </Button>

          <div className="flex items-center justify-center space-x-6 text-sm opacity-75">
            <div className="flex items-center">
              <Shield className="w-4 h-4 mr-1" />
              30-day guarantee
            </div>
            <div className="flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              Lifetime ROI
            </div>
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              Limited time
            </div>
          </div>

          {/* Referral Program Teaser */}
          <div className="mt-6 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-400/30 rounded-lg p-4 max-w-md mx-auto">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Users className="w-4 h-4 text-purple-400 mr-2" />
                <span className="text-sm font-semibold text-purple-200">🎁 Referral Bonus</span>
              </div>
              <div className="text-xs text-purple-300">
                Bring a friend and both get $50 credit toward future features
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoCreatorProgramInterface;
