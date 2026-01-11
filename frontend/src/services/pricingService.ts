import apiClient from './api';

export interface PricingPlan {
  id: number;
  name: string;
  display_name: string;
  price_usd: number;
  price_inr: number;
  features: string[];
  description: string;
  is_active: boolean;
}

export const pricingService = {
  getAllPlans: async (): Promise<PricingPlan[]> => {
    try {
      const response = await apiClient.get<PricingPlan[]>('/api/v1/pricing/plans');
      return response.data;
    } catch (error) {
      console.error('Error fetching pricing plans:', error);
      throw error;
    }
  },
  
  // Method to format price based on currency (simple heuristic or passed preference)
  formatPrice: (price: number, currency: 'USD' | 'INR' = 'INR') => {
    return new Intl.NumberFormat(currency === 'USD' ? 'en-US' : 'en-IN', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0
    }).format(price);
  }
};
