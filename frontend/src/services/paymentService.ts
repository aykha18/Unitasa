/**
 * Secure Payment Service for Razorpay Integration
 * Handles all payment operations through backend APIs
 */

import config from '../config/environment';

export interface PaymentOrderRequest {
  amount: number;
  customer_email: string;
  customer_name: string;
  lead_id?: number;
  program_type: string;
  currency: string;
  customer_country: string;
}

export interface PaymentOrderResponse {
  success: boolean;
  order_id: string;
  amount: number;
  currency: string;
  amount_usd: number;
  amount_inr: number;
  key_id: string;
  customer_email: string;
  customer_name: string;
  customer_country: string;
  message: string;
}

export interface PaymentVerificationRequest {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}

export interface PaymentVerificationResponse {
  success: boolean;
  verified: boolean;
  payment_id: string;
  order_id: string;
  status: string;
  amount: number;
  currency: string;
  method: string;
  co_creator_created: boolean;
  message: string;
}

class PaymentService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${config.apiBaseUrl}/api/v1/payments/razorpay`;
    console.log('Payment Service initialized:', {
      baseUrl: this.baseUrl,
      environment: config.environment
    });
  }

  /**
   * Create a secure payment order through backend
   */
  async createPaymentOrder(request: PaymentOrderRequest): Promise<PaymentOrderResponse> {
    try {
      // Get auth token if available
      const token = localStorage.getItem('token');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/create-order`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Order creation failed');
      }

      return data;
    } catch (error) {
      console.error('Payment order creation failed:', error);
      throw error;
    }
  }

  /**
   * Verify payment signature through backend
   */
  async verifyPayment(request: PaymentVerificationRequest): Promise<PaymentVerificationResponse> {
    try {
      // Get auth token if available
      const token = localStorage.getItem('token');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/verify-payment`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Payment verification failed:', error);
      throw error;
    }
  }

  /**
   * Get payment status
   */
  async getPaymentStatus(paymentId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/payment-status/${paymentId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get payment status:', error);
      throw error;
    }
  }

  /**
   * Detect user currency based on location
   */
  detectUserCurrency(): { currency: string; country: string } {
    try {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const isIndian = timezone.includes('Asia/Kolkata') || timezone.includes('Asia/Calcutta');
      
      return {
        currency: isIndian ? 'INR' : 'USD',
        country: isIndian ? 'IN' : 'US'
      };
    } catch {
      // Fallback to USD for international users
      return { currency: 'USD', country: 'US' };
    }
  }

  /**
   * Load Razorpay script dynamically
   */
  async loadRazorpayScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      if ((window as any).Razorpay) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Razorpay script'));
      document.head.appendChild(script);
    });
  }
}

export const paymentService = new PaymentService();