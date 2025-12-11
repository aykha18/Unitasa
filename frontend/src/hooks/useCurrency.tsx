import { useState, useEffect } from 'react';

interface CurrencyDisplay {
  currency: 'USD' | 'INR' | 'EUR';
  symbol: string;
  amount: number;
  displayText: string;
  isIndian: boolean;
  isEuropean: boolean;
  isAmerican: boolean;
}

// Exchange rates (approximate, update as needed)
const EXCHANGE_RATES = {
  USD: 1,
  INR: 83,
  EUR: 0.85
};

// EU country codes for EUR detection
const EU_COUNTRIES = [
  'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
  'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
  'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
];

export const useCurrency = (baseAmountUSD: number = 497): CurrencyDisplay => {
  const [currencyDisplay, setCurrencyDisplay] = useState<CurrencyDisplay>({
    currency: 'INR',
    symbol: '₹',
    amount: Math.round(baseAmountUSD * EXCHANGE_RATES.INR),
    displayText: `₹${Math.round(baseAmountUSD * EXCHANGE_RATES.INR).toLocaleString('en-IN')}`,
    isIndian: true,
    isEuropean: false,
    isAmerican: false
  });

  useEffect(() => {
    const detectCurrency = async () => {
      try {
        // Try to fetch user's country via IP geolocation with timeout and error handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
        
        const response = await fetch('https://ipapi.co/json/', {
          signal: controller.signal,
          mode: 'cors'
        });
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();

        const countryCode = data.country_code || 'US';
        let currency: 'USD' | 'INR' | 'EUR' = 'USD';
        let symbol = '$';
        let rate = 1;
        let isIndian = false;
        let isEuropean = false;
        let isAmerican = false;

        if (countryCode === 'IN') {
          currency = 'INR';
          symbol = '₹';
          rate = EXCHANGE_RATES.INR;
          isIndian = true;
        } else if (EU_COUNTRIES.includes(countryCode)) {
          currency = 'EUR';
          symbol = '€';
          rate = EXCHANGE_RATES.EUR;
          isEuropean = true;
        } else if (countryCode === 'US') {
          currency = 'USD';
          symbol = '$';
          rate = EXCHANGE_RATES.USD;
          isAmerican = true;
        } else {
          // Default to USD for other countries
          currency = 'USD';
          symbol = '$';
          rate = EXCHANGE_RATES.USD;
          isAmerican = true;
        }

        const amount = Math.round(baseAmountUSD * rate);
        let displayText = '';

        if (currency === 'INR') {
          displayText = `₹${amount.toLocaleString('en-IN')}`;
        } else if (currency === 'EUR') {
          displayText = `€${amount}`;
        } else {
          displayText = `$${amount}`;
        }

        setCurrencyDisplay({
          currency,
          symbol,
          amount,
          displayText,
          isIndian,
          isEuropean,
          isAmerican
        });
      } catch (error) {
        // Silently handle errors (CORS, network issues, rate limiting)
        // This prevents console spam while maintaining functionality
        // Default to USD on error
        setCurrencyDisplay({
          currency: 'USD',
          symbol: '$',
          amount: baseAmountUSD,
          displayText: `$${baseAmountUSD}`,
          isIndian: false,
          isEuropean: false,
          isAmerican: true
        });
      }
    };

    detectCurrency();
  }, [baseAmountUSD]);

  return currencyDisplay;
};

export default useCurrency;
