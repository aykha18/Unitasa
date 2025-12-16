import React, { useState, useEffect } from 'react';
import { Calculator, TrendingUp, DollarSign, Clock, Users, Target, ArrowRight } from 'lucide-react';
import { useCurrency } from '../../hooks/useCurrency';

interface ROIData {
  currentSpend: number;
  teamSize: number;
  hoursSaved: number;
  conversionIncrease: number;
}

const ROICalculator: React.FC = () => {
  const currency = useCurrency(497);
  const [roiData, setRoiData] = useState<ROIData>({
    currentSpend: 5000,
    teamSize: 3,
    hoursSaved: 15,
    conversionIncrease: 40
  });

  const [calculation, setCalculation] = useState({
    monthlySavings: 0,
    annualSavings: 0,
    roiPercentage: 0,
    paybackPeriod: 0,
    productivityGain: 0
  });

  // Calculate ROI when data changes
  useEffect(() => {
    const monthlyMarketingCost = roiData.currentSpend;
    const teamHourlyRate = 25; // Average marketing salary per hour
    const monthlyHours = roiData.teamSize * roiData.hoursSaved * 4.33; // Weekly hours * 4.33 weeks
    const timeSavingsValue = monthlyHours * teamHourlyRate;
    const conversionValue = monthlyMarketingCost * (roiData.conversionIncrease / 100);

    const totalMonthlySavings = timeSavingsValue + conversionValue;
    const annualSavings = totalMonthlySavings * 12;
    const unitasaMonthlyCost = currency.currency === 'INR' ? 35000 : 450; // Monthly subscription
    const roiPercentage = ((annualSavings - (unitasaMonthlyCost * 12)) / (unitasaMonthlyCost * 12)) * 100;
    const paybackPeriod = unitasaMonthlyCost > 0 ? (unitasaMonthlyCost * 12) / annualSavings : 0;
    const productivityGain = (roiData.hoursSaved / 40) * 100; // Percentage of work week saved

    setCalculation({
      monthlySavings: Math.round(totalMonthlySavings),
      annualSavings: Math.round(annualSavings),
      roiPercentage: Math.round(roiPercentage),
      paybackPeriod: Math.round(paybackPeriod * 10) / 10, // Round to 1 decimal
      productivityGain: Math.round(productivityGain)
    });
  }, [roiData, currency]);

  const formatAmount = (amount: number) => {
    if (currency.currency === 'INR') {
      return amount.toLocaleString('en-IN');
    } else if (currency.currency === 'EUR') {
      return amount.toString();
    }
    return amount.toLocaleString('en-US');
  };

  const handleInputChange = (field: keyof ROIData, value: number) => {
    setRoiData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <section className="py-20 bg-gradient-to-br from-green-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Calculator className="w-4 h-4 mr-2" />
            ROI Calculator
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Calculate Your Marketing ROI
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See exactly how much time and money Unitasa saves your business.
            Customize the inputs below based on your current marketing setup.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Input Section */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Your Current Marketing Setup</h3>

            <div className="space-y-6">
              {/* Current Monthly Marketing Spend */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Monthly Marketing Spend ({currency.symbol})
                </label>
                <input
                  type="range"
                  min="1000"
                  max="50000"
                  step="1000"
                  value={roiData.currentSpend}
                  onChange={(e) => handleInputChange('currentSpend', Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>{currency.symbol}1,000</span>
                  <span className="font-semibold">{currency.symbol}{formatAmount(roiData.currentSpend)}</span>
                  <span>{currency.symbol}50,000</span>
                </div>
              </div>

              {/* Team Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Marketing Team Size
                </label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  step="1"
                  value={roiData.teamSize}
                  onChange={(e) => handleInputChange('teamSize', Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>1 person</span>
                  <span className="font-semibold">{roiData.teamSize} people</span>
                  <span>20 people</span>
                </div>
              </div>

              {/* Hours Saved Per Week */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hours Saved Per Person Per Week
                </label>
                <input
                  type="range"
                  min="5"
                  max="30"
                  step="1"
                  value={roiData.hoursSaved}
                  onChange={(e) => handleInputChange('hoursSaved', Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>5 hours</span>
                  <span className="font-semibold">{roiData.hoursSaved} hours</span>
                  <span>30 hours</span>
                </div>
              </div>

              {/* Expected Conversion Increase */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expected Conversion Rate Increase (%)
                </label>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={roiData.conversionIncrease}
                  onChange={(e) => handleInputChange('conversionIncrease', Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>10%</span>
                  <span className="font-semibold">{roiData.conversionIncrease}%</span>
                  <span>100%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {/* Monthly Savings */}
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Monthly Savings</div>
                  <div className="text-3xl font-bold text-green-600">
                    {currency.symbol}{formatAmount(calculation.monthlySavings)}
                  </div>
                </div>
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>
            </div>

            {/* Annual Savings */}
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Annual Savings</div>
                  <div className="text-3xl font-bold text-green-600">
                    {currency.symbol}{formatAmount(calculation.annualSavings)}
                  </div>
                </div>
                <DollarSign className="w-8 h-8 text-green-500" />
              </div>
            </div>

            {/* ROI Percentage */}
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600 mb-1">ROI</div>
                  <div className="text-3xl font-bold text-blue-600">
                    {calculation.roiPercentage}%
                  </div>
                </div>
                <Target className="w-8 h-8 text-blue-500" />
              </div>
            </div>

            {/* Payback Period */}
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Payback Period</div>
                  <div className="text-3xl font-bold text-purple-600">
                    {calculation.paybackPeriod} months
                  </div>
                </div>
                <Clock className="w-8 h-8 text-purple-500" />
              </div>
            </div>

            {/* Productivity Gain */}
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Productivity Increase</div>
                  <div className="text-3xl font-bold text-orange-600">
                    {calculation.productivityGain}%
                  </div>
                </div>
                <Users className="w-8 h-8 text-orange-500" />
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Ready to Achieve These Results?
            </h3>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Join hundreds of businesses that have transformed their marketing ROI with Unitasa's AI automation platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors flex items-center justify-center"
              >
                Start Free Assessment
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
              <button
                onClick={() => {
                  // Scroll to pricing or open demo
                  document.querySelector('#pricing')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
              >
                View Pricing
              </button>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500 max-w-2xl mx-auto">
            *Calculations are estimates based on industry averages and your inputs.
            Actual results may vary depending on your specific marketing setup and implementation.
          </p>
        </div>
      </div>
    </section>
  );
};

export default ROICalculator;