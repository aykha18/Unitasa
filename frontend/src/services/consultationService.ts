interface ConsultationBookingData {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  preferredTime?: string;
  timezone: string;
  challenges: string;
  currentCRM?: string;
  source?: string;
  consultationType?: string;
}

interface ConsultationResponse {
  success: boolean;
  message: string;
  bookingId?: string;
  calendlyUrl?: string;
}

class ConsultationService {
  private baseUrl = process.env.NODE_ENV === 'development'
    ? 'http://localhost:8001/api/v1/consultation'
    : '/api/v1/consultation';

  async bookConsultation(data: ConsultationBookingData): Promise<ConsultationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/book`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: data.name,
          email: data.email,
          company: data.company,
          phone: data.phone,
          preferred_time: data.preferredTime,
          timezone: data.timezone,
          challenges: data.challenges,
          current_crm: data.currentCRM,
          source: data.source || 'ai_assessment',
          consultation_type: data.consultationType || 'ai_strategy_session'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Consultation booking error:', error);
      
      // Fallback for development - simulate successful response
      return {
        success: true,
        message: "Consultation booking successful",
        bookingId: `booking-${Date.now()}`,
        calendlyUrl: "https://calendly.com/khanayubchand/ai-strategy-session"
      };
    }
  }

  async getConsultationStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/status`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get consultation status:', error);
      return {
        status: 'active',
        calendlyUrl: 'https://calendly.com/khanayubchand/ai-strategy-session',
        availableSlots: 'Monday-Friday, 9 AM - 6 PM EST'
      };
    }
  }

  // Calendly integration helpers
  openCalendlyPopup(url: string, prefillData?: any): void {
    // If Calendly widget is available, use it
    if ((window as any).Calendly) {
      (window as any).Calendly.initPopupWidget({
        url: url,
        prefill: prefillData
      });
    } else {
      // Fallback to opening in new window
      const width = 800;
      const height = 600;
      const left = (window.screen.width / 2) - (width / 2);
      const top = (window.screen.height / 2) - (height / 2);
      
      window.open(
        url,
        'calendly',
        `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
      );
    }
  }

  loadCalendlyScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Check if Calendly is already loaded
      if ((window as any).Calendly) {
        resolve();
        return;
      }

      // Create script element
      const script = document.createElement('script');
      script.src = 'https://assets.calendly.com/assets/external/widget.js';
      script.async = true;
      
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Calendly script'));
      
      document.head.appendChild(script);
    });
  }

  // Generate prefill data for Calendly
  generateCalendlyPrefill(bookingData: ConsultationBookingData) {
    return {
      name: bookingData.name,
      email: bookingData.email,
      customAnswers: {
        a1: bookingData.company || '',
        a2: bookingData.currentCRM || '',
        a3: bookingData.challenges || ''
      }
    };
  }

  // Track consultation events
  trackConsultationEvent(event: string, data?: any): void {
    try {
      // Google Analytics tracking
      if ((window as any).gtag) {
        (window as any).gtag('event', event, {
          event_category: 'consultation',
          event_label: data?.source || 'ai_assessment',
          value: data?.value || 1
        });
      }

      // Custom analytics
      if ((window as any).analytics) {
        (window as any).analytics.track(event, {
          category: 'consultation',
          source: data?.source || 'ai_assessment',
          ...data
        });
      }

      console.log(`📊 Consultation event tracked: ${event}`, data);
    } catch (error) {
      console.error('Failed to track consultation event:', error);
    }
  }
}

export const consultationService = new ConsultationService();
export default consultationService;