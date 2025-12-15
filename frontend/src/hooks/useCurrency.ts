import { useState, useEffect } from 'react';

interface CurrencyInfo {
  currency: string;
  symbol: string;
  displayText: string;
  isIndian: boolean;
}

export const useCurrency = (usdAmount: number): CurrencyInfo => {
  const [currencyInfo, setCurrencyInfo] = useState<CurrencyInfo>({
    currency: 'INR',
    symbol: '₹',
    displayText: usdAmount.toLocaleString('en-IN'),
    isIndian: true
  });

  useEffect(() => {
    // Detect user's location and currency preference
    const detectCurrency = () => {
      // Check for stored currency preference
      const storedCurrency = localStorage.getItem('preferredCurrency');

      if (storedCurrency) {
        const currencyMap: Record<string, CurrencyInfo> = {
          'USD': { currency: 'USD', symbol: '$', displayText: usdAmount.toString(), isIndian: false },
          'EUR': { currency: 'EUR', symbol: '€', displayText: usdAmount.toString(), isIndian: false },
          'INR': { currency: 'INR', symbol: '₹', displayText: usdAmount.toLocaleString('en-IN'), isIndian: true },
          'GBP': { currency: 'GBP', symbol: '£', displayText: usdAmount.toString(), isIndian: false },
          'CAD': { currency: 'CAD', symbol: 'C$', displayText: usdAmount.toString(), isIndian: false },
          'AUD': { currency: 'AUD', symbol: 'A$', displayText: usdAmount.toString(), isIndian: false }
        };

        if (currencyMap[storedCurrency]) {
          setCurrencyInfo(currencyMap[storedCurrency]);
          return;
        }
      }

      // Auto-detect based on timezone and locale
      const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const userLocale = navigator.language || 'en-US';

      // India timezone detection
      if (userTimeZone.includes('Asia/Kolkata') || userTimeZone.includes('Asia/Calcutta') ||
          userLocale.includes('hi') || userLocale.includes('en-IN')) {
        setCurrencyInfo({
          currency: 'INR',
          symbol: '₹',
          displayText: usdAmount.toLocaleString('en-IN'),
          isIndian: true
        });
        return;
      }

      // European timezone detection
      if (userTimeZone.includes('Europe/') || userLocale.includes('de') ||
          userLocale.includes('fr') || userLocale.includes('es') ||
          userLocale.includes('it') || userLocale.includes('nl')) {
        setCurrencyInfo({
          currency: 'EUR',
          symbol: '€',
          displayText: usdAmount.toString(),
          isIndian: false
        });
        return;
      }

      // UK timezone detection
      if (userTimeZone.includes('Europe/London') || userLocale.includes('en-GB')) {
        setCurrencyInfo({
          currency: 'GBP',
          symbol: '£',
          displayText: usdAmount.toString(),
          isIndian: false
        });
        return;
      }

      // Canadian timezone detection
      if (userTimeZone.includes('America/Toronto') || userTimeZone.includes('America/Vancouver') ||
          userLocale.includes('en-CA') || userLocale.includes('fr-CA')) {
        setCurrencyInfo({
          currency: 'CAD',
          symbol: 'C$',
          displayText: usdAmount.toString(),
          isIndian: false
        });
        return;
      }

      // Australian timezone detection
      if (userTimeZone.includes('Australia/') || userLocale.includes('en-AU')) {
        setCurrencyInfo({
          currency: 'AUD',
          symbol: 'A$',
          displayText: usdAmount.toString(),
          isIndian: false
        });
        return;
      }

      // Default to USD
      setCurrencyInfo({
        currency: 'USD',
        symbol: '$',
        displayText: usdAmount.toString(),
        isIndian: false
      });
    };

    detectCurrency();
  }, [usdAmount]);

  return currencyInfo;
};

export default useCurrency;