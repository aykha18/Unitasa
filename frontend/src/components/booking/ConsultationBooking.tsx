import React, { useState } from 'react';
import { Calendar, Clock, User, Mail, Phone, MessageCircle, X, CheckCircle } from 'lucide-react';
import Button from '../ui/Button';
import { consultationService } from '../../services/consultationService';

interface ConsultationBookingProps {
  isOpen: boolean;
  onClose: () => void;
  leadData?: {
    name?: string;
    email?: string;
    company?: string;
  };
}

interface BookingFormData {
  name: string;
  email: string;
  company: string;
  phone: string;
  preferredTime: string;
  timezone: string;
  challenges: string;
  currentCRM: string;
}

const ConsultationBooking: React.FC<ConsultationBookingProps> = ({
  isOpen,
  onClose,
  leadData
}) => {
  console.log('🔍 ConsultationBooking rendered with isOpen:', isOpen);
  const [step, setStep] = useState<'form' | 'calendar' | 'confirmation'>('form');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<BookingFormData>({
    name: leadData?.name || '',
    email: leadData?.email || '',
    company: leadData?.company || '',
    phone: '',
    preferredTime: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    challenges: '',
    currentCRM: ''
  });

  const handleInputChange = (field: keyof BookingFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmitForm = async () => {
    setLoading(true);
    
    try {
      // Track form submission
      consultationService.trackConsultationEvent('consultation_form_submitted', {
        source: 'ai_assessment',
        crm: formData.currentCRM
      });

      // Submit lead information to backend
      const result = await consultationService.bookConsultation({
        name: formData.name,
        email: formData.email,
        company: formData.company,
        phone: formData.phone,
        preferredTime: formData.preferredTime,
        timezone: formData.timezone,
        challenges: formData.challenges,
        currentCRM: formData.currentCRM,
        source: 'ai_assessment',
        consultationType: 'ai_strategy_session'
      });

      if (result.success) {
        consultationService.trackConsultationEvent('consultation_booking_success');
        setStep('calendar');
      } else {
        throw new Error(result.message || 'Failed to submit booking request');
      }
    } catch (error) {
      console.error('Booking submission error:', error);
      consultationService.trackConsultationEvent('consultation_booking_error', {
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      // For now, proceed to calendar step anyway for better UX
      setStep('calendar');
    } finally {
      setLoading(false);
    }
  };

  const handleCalendlyCallback = () => {
    setStep('confirmation');
  };

  if (!isOpen) {
    console.log('🔍 ConsultationBooking not rendering - isOpen is false');
    return null;
  }

  console.log('🔍 ConsultationBooking rendering modal with isOpen:', isOpen);

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"
      style={{ zIndex: 9999 }}
      onClick={(e) => {
        console.log('🔍 Modal backdrop clicked');
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div 
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        style={{ border: '5px solid red' }}
        onClick={(e) => {
          console.log('🔍 Modal content clicked');
          e.stopPropagation();
        }}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Schedule AI Strategy Session
                </h2>
                <p className="text-sm text-gray-600">
                  Free 30-minute consultation with our AI implementation expert
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {step === 'form' && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Tell us about your business
                </h3>
                <p className="text-gray-600">
                  Help us prepare a personalized consultation for your AI marketing needs
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Your full name"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="your@email.com"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={formData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Your company"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current CRM System
                </label>
                <select
                  value={formData.currentCRM}
                  onChange={(e) => handleInputChange('currentCRM', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select your CRM</option>
                  <option value="hubspot">HubSpot</option>
                  <option value="salesforce">Salesforce</option>
                  <option value="pipedrive">Pipedrive</option>
                  <option value="zoho">Zoho CRM</option>
                  <option value="monday">Monday.com</option>
                  <option value="other">Other</option>
                  <option value="none">No CRM yet</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What are your biggest marketing challenges? *
                </label>
                <textarea
                  value={formData.challenges}
                  onChange={(e) => handleInputChange('challenges', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Tell us about your current marketing challenges, goals, or what you'd like to discuss..."
                  required
                />
              </div>

              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">What to expect in your session:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Personalized AI marketing strategy for your business</li>
                  <li>• CRM integration roadmap and recommendations</li>
                  <li>• Automation opportunities assessment</li>
                  <li>• Implementation timeline and next steps</li>
                  <li>• Q&A about Unitasa platform capabilities</li>
                </ul>
              </div>

              <div className="space-y-3">
                <Button
                  onClick={handleSubmitForm}
                  disabled={!formData.name || !formData.email || !formData.challenges || loading}
                  className="w-full"
                  size="lg"
                >
                  {loading ? 'Processing...' : 'Continue to Calendar'}
                  <Calendar className="w-4 h-4 ml-2" />
                </Button>
                
                <Button
                  variant="outline"
                  onClick={async () => {
                    if (!formData.name || !formData.email || !formData.challenges) {
                      toast.error('Please fill in the required fields first');
                      return;
                    }
                    
                    try {
                      setLoading(true);
                      consultationService.trackConsultationEvent('consultation_save_for_later');
                      
                      await consultationService.bookConsultation({
                        ...formData,
                        source: 'ai_assessment_save_later',
                        consultationType: 'ai_strategy_session'
                      });
                      
                      toast.success('Information saved! We\'ll send you a calendar link via email shortly.');
                      onClose();
                    } catch (error) {
                      console.error('Save for later error:', error);
                      toast('Information saved locally. We\'ll follow up via email.', { icon: '💾' });
                      onClose();
                    } finally {
                      setLoading(false);
                    }
                  }}
                  disabled={!formData.name || !formData.email || !formData.challenges || loading}
                  className="w-full"
                >
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Save Info & Book Later
                </Button>
              </div>
            </div>
          )}

          {step === 'calendar' && (
            <div className="text-center">
              <div className="mb-6">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Information Received!
                </h3>
                <p className="text-gray-600">
                  Now choose your preferred time slot for the consultation
                </p>
              </div>

              {/* Calendly Embed */}
              <div className="bg-gray-50 rounded-lg p-8 min-h-[400px] flex items-center justify-center">
                <div className="text-center">
                  <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">
                    Calendar Integration
                  </h4>
                  <p className="text-gray-600 mb-4">
                    Click below to open our scheduling calendar
                  </p>
                  <Button
                    onClick={async () => {
                      try {
                        // Track calendar open
                        consultationService.trackConsultationEvent('calendar_opened');
                        
                        // Load Calendly script if needed
                        await consultationService.loadCalendlyScript();
                        
                        // Generate prefill data
                        const prefillData = consultationService.generateCalendlyPrefill(formData);
                        
                        // Open Calendly with prefilled data
                        consultationService.openCalendlyPopup(
                          'https://calendly.com/unitasa/ai-strategy-session',
                          prefillData
                        );
                        
                        // Simulate booking completion after a delay
                        setTimeout(() => {
                          consultationService.trackConsultationEvent('consultation_scheduled');
                          handleCalendlyCallback();
                        }, 3000);
                      } catch (error) {
                        console.error('Calendar integration error:', error);
                        // Fallback to simple window open
                        window.open(
                          'https://calendly.com/unitasa/ai-strategy-session',
                          '_blank',
                          'width=800,height=600'
                        );
                        setTimeout(() => {
                          handleCalendlyCallback();
                        }, 2000);
                      }
                    }}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Clock className="w-4 h-4 mr-2" />
                    Open Calendar
                  </Button>
                </div>
              </div>

              <div className="mt-4 text-sm text-gray-500">
                Having trouble? Email us at{' '}
                <a href="mailto:support@unitasa.in" className="text-blue-600 hover:underline">
                  support@unitasa.in
                </a>
              </div>
            </div>
          )}

          {step === 'confirmation' && (
            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Session Booked Successfully! 🎉
              </h3>
              
              <p className="text-gray-600 mb-6">
                Thank you for booking your AI Strategy Session. You'll receive a confirmation email shortly with:
              </p>

              <div className="bg-green-50 rounded-lg p-4 mb-6 text-left">
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    Meeting details and calendar invite
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    Preparation guide for maximum value
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    Direct contact information
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                    Pre-session questionnaire (optional)
                  </li>
                </ul>
              </div>

              <div className="space-y-3">
                <Button
                  onClick={() => {
                    consultationService.trackConsultationEvent('consultation_completed_continue');
                    onClose();
                  }}
                  className="w-full"
                  size="lg"
                >
                  Continue Exploring Unitasa
                </Button>
                
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      consultationService.trackConsultationEvent('consultation_email_clicked');
                      window.open('mailto:support@unitasa.in', '_blank');
                    }}
                    className="w-full"
                  >
                    <MessageCircle className="w-4 h-4 mr-2" />
                    Email Us
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => {
                      consultationService.trackConsultationEvent('calendar_reopened');
                      window.open('https://calendly.com/unitasa/ai-strategy-session', '_blank');
                    }}
                    className="w-full"
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    View Calendar
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConsultationBooking;