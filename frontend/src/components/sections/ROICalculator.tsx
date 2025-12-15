import React, { useState, useEffect } from 'react';
import { Calculator, TrendingUp, DollarSign, Clock, Users, Target } from 'lucide-react';
import { useCurrency } from '../../hooks/useCurrency';

export {};

interface ROIData {
  currentSpend: number;
  weeklyHours: number;
  industry: string;
  companySize: string;
}

interface ROICalculation {
  monthlySavings: number;
  annualSavings: number;
  timeSavedHours: number;
  timeSavedWeeks: number;
  productivityGain: number;
  roiPercentage: number;
  breakevenMonths: number;
}

const ROICalculator: React.FC = () => {
  const currency = useCurrency(497);
  const [roiData, setRoiData] = useState<ROIData>({
    currentSpend: 50000, // ₹50,000/month (typical Indian agency cost)
    weeklyHours: 20, // More hours due to manual processes in India
    industry: 'technology',
    companySize: '25-50'
  });

  const [calculation, setCalculation] = useState<ROICalculation | null>(null);

  // Industry benchmarks for realistic calculations
  const industryBenchmarks = {
    technology: { efficiency: 0.75, timeMultiplier: 1.2 },
    healthcare: { efficiency: 0.65, timeMultiplier: 1.1 },
    finance: { efficiency: 0.70, timeMultiplier: 1.15 },
    retail: { efficiency: 0.80, timeMultiplier: 1.3 },
    consulting: { efficiency: 0.60, timeMultiplier: 1.0 },
    manufacturing: { efficiency: 0.55, timeMultiplier: 0.9 },
    default: { efficiency: 0.70, timeMultiplier: 1.0 }
  };

  // Company size multipliers
  const sizeMultipliers = {
    '1-10': 0.8,
    '11-25': 0.9,
    '25-50': 1.0,
    '51-100': 1.1,
    '100+': 1.2
  };

  const calculateROI = (data: ROIData): ROICalculation => {
    const benchmark = industryBenchmarks[data.industry as keyof typeof industryBenchmarks] || industryBenchmarks.default;
    const sizeMultiplier = sizeMultipliers[data.companySize as keyof typeof sizeMultipliers] || 1.0;

    // Base Unitasa cost (Indian pricing)
    const unitasaMonthlyCost = 4999; // ₹4,999/month starting price

    // Calculate current inefficiencies
    const currentMonthlyCost = data.currentSpend;
    const currentWeeklyHours = data.weeklyHours;

    // Unitasa efficiency improvements
    const costReductionFactor = 0.65; // 65% cost reduction
    const timeReductionFactor = 0.75; // 75% time reduction
    const productivityGain = 0.40; // 40% overall productivity gain

    // Monthly savings calculation
    const monthlySavings = Math.max(0, currentMonthlyCost * costReductionFactor - unitasaMonthlyCost);

    // Time savings
    const timeSavedHours = currentWeeklyHours * timeReductionFactor;
    const timeSavedWeeks = timeSavedHours / currentWeeklyHours;

    // ROI calculation
    const annualSavings = monthlySavings * 12;
    const annualInvestment = unitasaMonthlyCost * 12;
    const roiPercentage = annualInvestment > 0 ? ((annualSavings - annualInvestment) / annualInvestment) * 100 : 0;

    // Breakeven calculation
    const breakevenMonths = unitasaMonthlyCost > 0 ? Math.ceil(unitasaMonthlyCost / (currentMonthlyCost * costReductionFactor / 12)) : 0;

    return {
      monthlySavings: Math.round(monthlySavings),
      annualSavings: Math.round(annualSavings),
      timeSavedHours: Math.round(timeSavedHours * 10) / 10, // Round to 1 decimal
      timeSavedWeeks: Math.round(timeSavedWeeks * 10) / 10,
      productivityGain: Math.round(productivityGain * 100),
      roiPercentage: Math.round(roiPercentage),
      breakevenMonths: Math.max(1, breakevenMonths)
    };
  };

  useEffect(() => {
    const calc = calculateROI(roiData);
    setCalculation(calc);
  }, [roiData]);

  const formatAmount = (amount: number) => {
    if (currency.currency === 'INR') {
      return amount.toLocaleString('en-IN');
    } else if (currency.currency === 'EUR') {
      return amount.toString();
    } else {
      return amount.toString();
    }
  };

  const getIndustryDisplayName = (industry: string) => {
    const names = {
      technology: 'Technology/SaaS',
      healthcare: 'Healthcare',
      finance: 'Finance',
      retail: 'Retail/E-commerce',
      consulting: 'Consulting',
      manufacturing: 'Manufacturing',
      default: 'General Business'
    };
    return names[industry as keyof typeof names] || names.default;
  };

  return (
    <section className="py-20 bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Calculator className="w-4 h-4 mr-2" />
            ROI Calculator
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Calculate Your AI Marketing ROI
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See exactly how much time and money Unitasa can save your business with intelligent marketing automation.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Your Current Situation</h3>

            <div className="space-y-6">
              {/* Current Monthly Spend */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Monthly Marketing Spend ({currency.symbol})
                </label>
                <input
                  type="number"
                  value={roiData.currentSpend}
                  onChange={(e) => setRoiData({...roiData, currentSpend: Number(e.target.value)})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="50000"
                  min="0"
                />
                <p className="text-xs text-gray-500 mt-1">Marketing agencies, tools, freelancers, etc.</p>
              </div>

              {/* Weekly Hours */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hours Spent on Marketing/Week
                </label>
                <input
                  type="number"
                  value={roiData.weeklyHours}
                  onChange={(e) => setRoiData({...roiData, weeklyHours: Number(e.target.value)})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="20"
                  min="0"
                  max="168"
                />
                <p className="text-xs text-gray-500 mt-1">Content creation, social media management, customer engagement</p>
              </div>

              {/* Industry */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <select
                  value={roiData.industry}
                  onChange={(e) => setRoiData({...roiData, industry: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="technology">Technology/SaaS</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="finance">Finance</option>
                  <option value="retail">Retail/E-commerce</option>
                  <option value="consulting">Consulting</option>
                  <option value="manufacturing">Manufacturing</option>
                </select>
              </div>

              {/* Company Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Size (Employees)
                </label>
                <select
                  value={roiData.companySize}
                  onChange={(e) => setRoiData({...roiData, companySize: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="1-10">1-10 employees</option>
                  <option value="11-25">11-25 employees</option>
                  <option value="25-50">25-50 employees</option>
                  <option value="51-100">51-100 employees</option>
                  <option value="100+">100+ employees</option>
                </select>
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div className="space-y-6">
            {calculation && (
              <>
                {/* Main ROI Result */}
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-8 text-white shadow-lg">
                  <div className="flex items-center mb-4">
                    <TrendingUp className="w-8 h-8 mr-3" />
                    <h3 className="text-2xl font-bold">Your Potential Savings</h3>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div className="text-center">
                      <div className="text-4xl font-bold mb-1">
                        {currency.symbol}{formatAmount(calculation.monthlySavings)}
                      </div>
                      <div className="text-green-100 text-sm">Monthly Savings</div>
                    </div>
                    <div className="text-center">
                      <div className="text-4xl font-bold mb-1">
                        {currency.symbol}{formatAmount(calculation.annualSavings)}
                      </div>
                      <div className="text-green-100 text-sm">Annual Savings</div>
                    </div>
                  </div>

                  <div className="mt-6 pt-6 border-t border-green-400">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-yellow-300 mb-1">
                        {calculation.roiPercentage > 0 ? '+' : ''}{calculation.roiPercentage}%
                      </div>
                      <div className="text-green-100 text-sm">ROI in Year 1</div>
                    </div>
                  </div>
                </div>

                {/* Detailed Breakdown */}
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Detailed Breakdown</h4>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="flex items-center p-4 bg-blue-50 rounded-lg">
                      <Clock className="w-8 h-8 text-blue-600 mr-3" />
                      <div>
                        <div className="font-semibold text-gray-900">{calculation.timeSavedHours} hours/week</div>
                        <div className="text-sm text-gray-600">Time Saved</div>
                      </div>
                    </div>

                    <div className="flex items-center p-4 bg-purple-50 rounded-lg">
                      <Users className="w-8 h-8 text-purple-600 mr-3" />
                      <div>
                        <div className="font-semibold text-gray-900">{calculation.productivityGain}%</div>
                        <div className="text-sm text-gray-600">Productivity Gain</div>
                      </div>
                    </div>

                    <div className="flex items-center p-4 bg-orange-50 rounded-lg">
                      <Target className="w-8 h-8 text-orange-600 mr-3" />
                      <div>
                        <div className="font-semibold text-gray-900">{calculation.breakevenMonths} months</div>
                        <div className="text-sm text-gray-600">Breakeven Period</div>
                      </div>
                    </div>

                    <div className="flex items-center p-4 bg-green-50 rounded-lg">
                      <DollarSign className="w-8 h-8 text-green-600 mr-3" />
                      <div>
                        <div className="font-semibold text-gray-900">{currency.symbol}{currency.displayText}</div>
                        <div className="text-sm text-gray-600">Monthly Investment</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Industry Context */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm text-gray-600">
                    <strong>Based on your {getIndustryDisplayName(roiData.industry)} business:</strong> Indian companies in your industry typically see {industryBenchmarks[roiData.industry as keyof typeof industryBenchmarks]?.efficiency * 100 || 70}% efficiency improvements with AI automation, saving ₹2-6 lakh monthly on average.
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-12">
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 max-w-2xl mx-auto">
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Ready to Start Saving?
            </h3>
            <p className="text-gray-600 mb-6">
              Join 25 founding entrepreneurs who get lifetime access to this ROI-generating platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                className="bg-gradient-primary text-white px-8 py-3 rounded-lg font-semibold hover:shadow-brand transition-all duration-200"
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }}
              >
                Get Free AI Assessment
              </button>
              <button
                onClick={() => {
                  window.dispatchEvent(new CustomEvent('openDemo'));
                }}
                className="border-2 border-unitasa-electric text-unitasa-electric px-8 py-3 rounded-lg font-semibold hover:bg-unitasa-electric hover:text-white transition-all duration-200"
              >
                See Live Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ROICalculator;